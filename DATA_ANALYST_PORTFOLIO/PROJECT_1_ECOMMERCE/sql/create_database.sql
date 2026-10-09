-- ============================================
-- RetailEdge Database Creation Script
-- MySQL Compatible
-- ============================================

-- Step 1: Create Database
DROP DATABASE IF EXISTS retailedge_db;
CREATE DATABASE retailedge_db;
USE retailedge_db;

-- ============================================
-- Step 2: Create Dimension Tables
-- ============================================

-- dim_customers
CREATE TABLE dim_customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(50),
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    membership_tier VARCHAR(20) NOT NULL
);

-- dim_products
CREATE TABLE dim_products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2),
    seller_id VARCHAR(10) NOT NULL
);

-- dim_regions
CREATE TABLE dim_regions (
    region_id INT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    tier VARCHAR(20) NOT NULL
);

-- dim_date
CREATE TABLE dim_date (
    date_id VARCHAR(10) PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter VARCHAR(5) NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend INT NOT NULL
);

-- ============================================
-- Step 3: Create Fact Tables
-- ============================================

-- fact_orders
CREATE TABLE fact_orders (
    order_id VARCHAR(12) PRIMARY KEY,
    customer_id VARCHAR(10) NOT NULL,
    order_date DATE NOT NULL,
    region_id INT NOT NULL,
    status VARCHAR(20),
    shipping_address VARCHAR(200) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (region_id) REFERENCES dim_regions(region_id)
);

-- fact_order_items
CREATE TABLE fact_order_items (
    item_id VARCHAR(15) PRIMARY KEY,
    order_id VARCHAR(12) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(5,2) NOT NULL,
    line_total DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES fact_orders(order_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
);

-- fact_payments
CREATE TABLE fact_payments (
    payment_id VARCHAR(15) PRIMARY KEY,
    order_id VARCHAR(12) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES fact_orders(order_id)
);

-- fact_refunds
CREATE TABLE fact_refunds (
    refund_id VARCHAR(12) PRIMARY KEY,
    order_id VARCHAR(12) NOT NULL,
    item_id VARCHAR(15) NOT NULL,
    refund_date DATE NOT NULL,
    refund_amount DECIMAL(12,2) NOT NULL,
    reason VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES fact_orders(order_id),
    FOREIGN KEY (item_id) REFERENCES fact_order_items(item_id)
);

-- ============================================
-- Step 4: Create Indexes
-- ============================================

-- Indexes for faster queries
CREATE INDEX idx_orders_customer ON fact_orders(customer_id);
CREATE INDEX idx_orders_date ON fact_orders(order_date);
CREATE INDEX idx_orders_status ON fact_orders(status);
CREATE INDEX idx_order_items_order ON fact_order_items(order_id);
CREATE INDEX idx_order_items_product ON fact_order_items(product_id);
CREATE INDEX idx_payments_order ON fact_payments(order_id);
CREATE INDEX idx_payments_date ON fact_payments(payment_date);
CREATE INDEX idx_refunds_order ON fact_refunds(order_id);
CREATE INDEX idx_products_category ON dim_products(category);
CREATE INDEX idx_customers_city ON dim_customers(city);
CREATE INDEX idx_customers_tier ON dim_customers(membership_tier);

-- ============================================
-- Step 5: Create Views for Common Queries
-- ============================================

-- View: Order Summary with Customer Info
CREATE VIEW vw_order_summary AS
SELECT 
    o.order_id,
    o.order_date,
    o.status,
    c.name AS customer_name,
    c.city,
    c.membership_tier,
    r.region_name,
    SUM(oi.line_total) AS order_total
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
JOIN dim_regions r ON o.region_id = r.region_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.order_date, o.status, c.name, c.city, c.membership_tier, r.region_name;

-- View: Payment Reconciliation
-- NOTE: each source is aggregated to one row per order BEFORE joining.
-- Joining the raw tables directly would multiply rows (order items x payments x
-- refunds) and inflate payment_total / refund_total (a JOIN fan-out).
CREATE VIEW vw_payment_reconciliation AS
SELECT 
    o.order_id,
    o.order_date,
    oi.order_total,
    COALESCE(p.payment_total, 0) AS payment_total,
    COALESCE(ref.refund_total, 0) AS refund_total,
    oi.order_total - COALESCE(p.payment_total, 0) AS discrepancy
FROM fact_orders o
JOIN (
    SELECT order_id, SUM(line_total) AS order_total
    FROM fact_order_items
    GROUP BY order_id
) oi ON o.order_id = oi.order_id
LEFT JOIN (
    SELECT order_id, SUM(amount_paid) AS payment_total
    FROM fact_payments
    GROUP BY order_id
) p ON o.order_id = p.order_id
LEFT JOIN (
    SELECT order_id, SUM(refund_amount) AS refund_total
    FROM fact_refunds
    GROUP BY order_id
) ref ON o.order_id = ref.order_id;

-- View: Category Performance
CREATE VIEW vw_category_performance AS
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.line_total) AS total_revenue,
    AVG(oi.line_total) AS avg_order_value
FROM fact_order_items oi
JOIN dim_products p ON oi.product_id = p.product_id
GROUP BY p.category;

-- ============================================
-- DATABASE CREATED SUCCESSFULLY
-- ============================================
