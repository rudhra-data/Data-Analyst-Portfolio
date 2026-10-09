# METRIC DICTIONARY — RetailEdge Project

## Overview

This document defines all business metrics (KPIs) used in the RetailEdge E-Commerce Analytics project.

---

## REVENUE METRICS

### 1. Gross Revenue

| Attribute | Value |
|-----------|-------|
| **Formula** | SUM(line_total) from fact_order_items |
| **Business Meaning** | Total sales value before any deductions |
| **Grain** | Total across all orders |
| **Source Fields** | fact_order_items.line_total |
| **Caveats** | Includes cancelled/returned orders |

---

### 2. Net Revenue

| Attribute | Value |
|-----------|-------|
| **Formula** | Gross Revenue - SUM(refund_amount) from fact_refunds |
| **Business Meaning** | Actual revenue after refunds |
| **Grain** | Total across all orders |
| **Source Fields** | fact_order_items.line_total, fact_refunds.refund_amount |
| **Caveats** | Does not account for pending refunds |

---

### 3. Revenue by Category

| Attribute | Value |
|-----------|-------|
| **Formula** | SUM(line_total) GROUP BY dim_products.category |
| **Business Meaning** | Which product categories drive revenue |
| **Grain** | Per category |
| **Source Fields** | fact_order_items.line_total, dim_products.category |
| **Caveats** | Categories may have different product counts |

---

### 4. Revenue by Region

| Attribute | Value |
|-----------|-------|
| **Formula** | SUM(line_total) GROUP BY dim_regions.region_name |
| **Business Meaning** | Geographic revenue distribution |
| **Grain** | Per region |
| **Source Fields** | fact_order_items.line_total, dim_regions.region_name |
| **Caveats** | Regions have different population sizes |

---

## ORDER METRICS

### 5. Total Orders

| Attribute | Value |
|-----------|-------|
| **Formula** | COUNT(DISTINCT order_id) from fact_orders |
| **Business Meaning** | Number of unique orders placed |
| **Grain** | Count of orders |
| **Source Fields** | fact_orders.order_id |
| **Caveats** | Includes all statuses (cancelled, returned) |

---

### 6. Average Order Value (AOV)

| Attribute | Value |
|-----------|-------|
| **Formula** | Gross Revenue / Total Orders |
| **Business Meaning** | Average amount spent per order |
| **Grain** | Per order |
| **Source Fields** | fact_order_items.line_total, fact_orders.order_id |
| **Caveats** | Can be skewed by high-value orders |

---

### 7. Orders by Status

| Attribute | Value |
|-----------|-------|
| **Formula** | COUNT(order_id) GROUP BY status |
| **Business Meaning** | Order fulfillment distribution |
| **Grain** | Per status |
| **Source Fields** | fact_orders.status |
| **Caveats** | NULL status indicates data quality issue |

---

## CUSTOMER METRICS

### 8. Total Customers

| Attribute | Value |
|-----------|-------|
| **Formula** | COUNT(DISTINCT customer_id) from fact_orders (customers who ordered) |
| **Business Meaning** | Total active (purchasing) customers |
| **Grain** | Count of customers |
| **Source Fields** | fact_orders.customer_id |
| **Caveats** | dim_customers has 1,000 registered; 996 placed at least one order |

---

### 9. Active Customers

| Attribute | Value |
|-----------|-------|
| **Formula** | COUNT(DISTINCT customer_id) from fact_orders WHERE order_date >= date_threshold |
| **Business Meaning** | Customers who placed orders in period |
| **Grain** | Per time period |
| **Source Fields** | fact_orders.customer_id, fact_orders.order_date |
| **Caveats** | Threshold varies (30/60/90 days) |

---

### 10. Repeat Customer Rate

| Attribute | Value |
|-----------|-------|
| **Formula** | (Customers with 2+ orders / Total customers) * 100 |
| **Business Meaning** | Customer loyalty indicator |
| **Grain** | Percentage |
| **Source Fields** | fact_orders.customer_id |
| **Caveats** | Time period affects calculation |

---

### 11. Customer Lifetime Value (CLV) Approximation

| Attribute | Value |
|-----------|-------|
| **Formula** | AVG(order_value) * AVG(orders_per_customer) * AVG(customer_lifespan) |
| **Business Meaning** | Estimated total value of a customer |
| **Grain** | Per customer |
| **Source Fields** | fact_order_items.line_total, fact_orders.customer_id, fact_orders.order_date |
| **Caveats** | This is an approximation, not exact CLV |

---

## REFUND & RETURN METRICS

### 12. Refund Rate

| Attribute | Value |
|-----------|-------|
| **Formula** | (Total Refund Amount / Gross Revenue) * 100 |
| **Business Meaning** | Percentage of revenue lost to refunds |
| **Grain** | Percentage |
| **Source Fields** | fact_refunds.refund_amount, fact_order_items.line_total |
| **Caveats** | High refund rate indicates quality/service issues |

---

### 13. Return Rate

| Attribute | Value |
|-----------|-------|
| **Formula** | (Orders with status 'Returned' / Total Orders) * 100 |
| **Business Meaning** | Percentage of orders returned |
| **Grain** | Percentage |
| **Source Fields** | fact_orders.status |
| **Caveats** | Different from refund rate (may have refunds without returns) |

---

### 14. Refunds by Reason

| Attribute | Value |
|-----------|-------|
| **Formula** | COUNT(refund_id), SUM(refund_amount) GROUP BY reason |
| **Business Meaning** | Why customers request refunds |
| **Grain** | Per reason |
| **Source Fields** | fact_refunds.reason, fact_refunds.refund_amount |
| **Caveats** | Some reasons may be miscategorized |

---

## PAYMENT METRICS

### 15. Payment Match Rate

| Attribute | Value |
|-----------|-------|
| **Formula** | (Orders where payment = order value / Total orders) * 100 |
| **Business Meaning** | Payment processing accuracy |
| **Grain** | Percentage |
| **Source Fields** | fact_payments.amount_paid, fact_order_items.line_total |
| **Caveats** | Mismatches may be legitimate (partial payments, fees) |

---

### 16. Payment Method Distribution

| Attribute | Value |
|-----------|-------|
| **Formula** | COUNT(payment_id), SUM(amount_paid) GROUP BY payment_method |
| **Business Meaning** | Customer payment preferences |
| **Grain** | Per payment method |
| **Source Fields** | fact_payments.payment_method, fact_payments.amount_paid |
| **Caveats** | Method popularity varies by region |

---

### 17. Revenue Leakage

| Attribute | Value |
|-----------|-------|
| **Formula** | SUM(ABS(order_total - amount_paid)) + SUM(refund_amount) |
| **Business Meaning** | Unaccounted revenue differences plus refunds |
| **Grain** | Total amount |
| **Source Fields** | fact_payments.amount_paid, fact_order_items.line_total, fact_refunds.refund_amount |
| **Caveats** | Payment mismatch tolerance is 0.01; not all leakage is fraud |

---

## GROWTH METRICS

### 18. Month-over-Month (MoM) Growth

| Attribute | Value |
|-----------|-------|
| **Formula** | ((Current Month Revenue - Previous Month Revenue) / Previous Month Revenue) * 100 |
| **Business Meaning** | Revenue growth trend |
| **Grain** | Per month |
| **Source Fields** | fact_order_items.line_total, fact_orders.order_date |
| **Caveats** | Seasonal effects can distort |

---

### 19. New vs Returning Customers

| Attribute | Value |
|-----------|-------|
| **Formula** | Flag customers as 'New' (first order) or 'Returning' (2+ orders) |
| **Business Meaning** | Customer acquisition vs retention |
| **Grain** | Per customer |
| **Source Fields** | fact_orders.customer_id, fact_orders.order_date |
| **Caveats** | First order in dataset may not be first ever order |

---

## SEGMENTATION METRICS

### 20. RFM Segmentation

| Attribute | Value |
|-----------|-------|
| **Formula** | Score each customer on Recency, Frequency, Monetary value |
| **Business Meaning** | Customer value segmentation |
| **Grain** | Per customer |
| **Source Fields** | fact_orders.order_date, fact_orders.customer_id, fact_order_items.line_total |
| **Caveats** | Scoring thresholds are subjective |

---

### 21. Customer Segments

| Segment | Definition |
|---------|------------|
| Champions | High R, High F, High M |
| Loyal Customers | High F, Medium-High M |
| Potential Loyalists | High R, Low F |
| At Risk | Low R, High F |
| Lost Customers | Low R, Low F |
| New Customers | High R, Low F, Low M |

---

## DATA QUALITY METRICS

### 22. Data Completeness

| Attribute | Value |
|-----------|-------|
| **Formula** | (Non-null values / Total values) * 100 per column |
| **Business Meaning** | Data quality indicator |
| **Grain** | Per column |
| **Source Fields** | All columns |
| **Caveats** | Low completeness affects analysis reliability |

---

### 23. Duplicate Rate

| Attribute | Value |
|-----------|-------|
| **Formula** | (Duplicate rows / Total rows) * 100 |
| **Business Meaning** | Data integrity indicator |
| **Grain** | Per table |
| **Source Fields** | All columns |
| **Caveats** | Duplicates can skew calculations |

---

*Metric Dictionary Version 1.0 — Created 2026-09-07*
