-- ============================================
-- RETAILEDGE - BUSINESS ANALYSIS QUERIES
-- Day 5: Basic Business Analysis
-- ============================================

USE retailedge_db;

-- ============================================
-- 1. REVENUE BY CATEGORY
-- ============================================

SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.line_total) AS total_revenue
FROM fact_order_items oi
JOIN dim_products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- ============================================
-- 2. REVENUE BY REGION
-- ============================================

SELECT 
    r.region_name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.line_total) AS total_revenue
FROM fact_orders o
JOIN dim_regions r ON o.region_id = r.region_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
GROUP BY r.region_name
ORDER BY total_revenue DESC;

-- ============================================
-- 3. PAYMENT METHOD MISMATCHES
-- ============================================

SELECT 
    p.payment_method,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(CASE WHEN ABS(oi_sum.total - pay_sum.total) > 0.01 THEN 1 ELSE 0 END) AS mismatch_count
FROM fact_orders o
JOIN fact_payments p ON o.order_id = p.order_id
JOIN (
    SELECT order_id, SUM(line_total) AS total 
    FROM fact_order_items 
    GROUP BY order_id
) oi_sum ON o.order_id = oi_sum.order_id
JOIN (
    SELECT order_id, SUM(amount_paid) AS total 
    FROM fact_payments 
    GROUP BY order_id
) pay_sum ON o.order_id = pay_sum.order_id
GROUP BY p.payment_method
ORDER BY mismatch_count DESC;

-- ============================================
-- 4. REFUND RATE BY CATEGORY
-- ============================================

SELECT 
    p.category,
    COUNT(DISTINCT r.refund_id) AS total_refunds,
    SUM(r.refund_amount) AS total_refund_amount,
    ROUND(SUM(r.refund_amount) / (SELECT SUM(line_total) FROM fact_order_items) * 100, 2) AS refund_rate_pct
FROM fact_refunds r
JOIN fact_order_items oi ON r.item_id = oi.item_id
JOIN dim_products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_refund_amount DESC;

-- ============================================
-- 5. CUSTOMER MEMBERSHIP PERFORMANCE
-- ============================================

SELECT 
    c.membership_tier,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.line_total) AS total_revenue,
    ROUND(SUM(oi.line_total) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM dim_customers c
JOIN fact_orders o ON c.customer_id = o.customer_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
GROUP BY c.membership_tier
ORDER BY revenue_per_customer DESC;

-- ============================================
-- BUSINESS ANALYSIS COMPLETE
-- ============================================
