-- ============================================
-- RETAILEDGE - SQL VALIDATION QUERIES
-- Day 5: Data Validation
-- ============================================

USE retailedge_db;

-- ============================================
-- 1. DUPLICATE DETECTION
-- ============================================

-- Check for duplicate orders
SELECT order_id, COUNT(*) AS duplicate_count
FROM fact_orders
GROUP BY order_id
HAVING COUNT(*) > 1
LIMIT 10;

-- ============================================
-- 2. NULL CHECKS
-- ============================================

-- Check for missing values in orders
SELECT 
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer,
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS missing_date,
    SUM(CASE WHEN status IS NULL THEN 1 ELSE 0 END) AS missing_status
FROM fact_orders;

-- Check for empty status (not NULL)
SELECT 
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = '' THEN 1 ELSE 0 END) AS empty_status,
    SUM(CASE WHEN status != '' THEN 1 ELSE 0 END) AS has_status
FROM fact_orders;

-- ============================================
-- 3. INVALID VALUES
-- ============================================

-- Check for negative quantities
SELECT COUNT(*) AS negative_quantity
FROM fact_order_items
WHERE quantity < 0;

-- Check for missing emails in customers
SELECT 
    COUNT(*) AS total_customers,
    SUM(CASE WHEN email = '' THEN 1 ELSE 0 END) AS missing_email
FROM dim_customers;

-- ============================================
-- 4. ORPHAN RECORDS
-- ============================================

-- Check for orders without valid customer
SELECT COUNT(*) AS orphan_orders
FROM fact_orders o
LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- ============================================
-- 5. PAYMENT MISMATCHES
-- ============================================

-- NOTE: aggregate order items and payments separately first. Joining the raw
-- tables together fans out (items x payments) and inflates the totals.

-- Find payment mismatches
SELECT 
    o.order_id,
    oi.order_total,
    p.payment_total,
    oi.order_total - p.payment_total AS difference
FROM fact_orders o
JOIN (
    SELECT order_id, SUM(line_total) AS order_total
    FROM fact_order_items
    GROUP BY order_id
) oi ON o.order_id = oi.order_id
JOIN (
    SELECT order_id, SUM(amount_paid) AS payment_total
    FROM fact_payments
    GROUP BY order_id
) p ON o.order_id = p.order_id
WHERE ABS(oi.order_total - p.payment_total) > 0.01
ORDER BY ABS(oi.order_total - p.payment_total) DESC
LIMIT 10;

-- Count total mismatches
SELECT COUNT(*) AS total_mismatches
FROM (
    SELECT o.order_id
    FROM fact_orders o
    JOIN (
        SELECT order_id, SUM(line_total) AS order_total
        FROM fact_order_items
        GROUP BY order_id
    ) oi ON o.order_id = oi.order_id
    JOIN (
        SELECT order_id, SUM(amount_paid) AS payment_total
        FROM fact_payments
        GROUP BY order_id
    ) p ON o.order_id = p.order_id
    WHERE ABS(oi.order_total - p.payment_total) > 0.01
) AS mismatches;

-- ============================================
-- VALIDATION COMPLETE
-- ============================================
