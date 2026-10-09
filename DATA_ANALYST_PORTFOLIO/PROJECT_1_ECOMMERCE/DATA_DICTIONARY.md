# DATA DICTIONARY — RetailEdge Project

## Overview

This document describes all tables, columns, and metrics used in the RetailEdge E-Commerce Analytics project.

---

## TABLES OVERVIEW

| Table | Description | Rows | Grain |
|-------|-------------|------|-------|
| dim_customers | Customer information | 1,000 | One row per customer |
| dim_products | Product catalog | 300 | One row per product variant |
| dim_regions | Regional information | 10 | One row per region |
| dim_date | Date dimension | 731 (raw) / 1,047 (Power BI) | One row per day |
| fact_orders | Order transactions | 5,150 (5,000 after removing 150 duplicates) | One row per order |
| fact_order_items | Line items per order | 10,461 | One row per line item |
| fact_payments | Payment records | 5,000 | One row per payment |
| fact_refunds | Refund records | 500 | One row per refund |

---

## 1. dim_customers

**Description:** Contains customer master data including contact information and membership details.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| customer_id | STRING | Unique identifier for each customer | System | CUST00001-CUST99999 | CUST00123 | PRIMARY KEY, No NULLs |
| name | STRING | Full name of customer | Signup form | 2-100 characters | Aarav Sharma | No NULLs |
| email | STRING | Email address | Signup form | Valid email format | aarav@email.com | ~5% NULL (missing) |
| phone | STRING | Phone number | Signup form | 10 digits | +919876543210 | No NULLs |
| city | STRING | City of residence | Signup form | Valid city name | Mumbai | ~3% NULL (missing) |
| state | STRING | State of residence | Signup form | Valid state name | Maharashtra | No NULLs |
| country | STRING | Country | System | India | India | No NULLs |
| signup_date | DATE | Date customer registered | System | 2023-01-01 to 2024-12-31 | 2023-06-15 | No NULLs |
| membership_tier | STRING | Loyalty tier | System | Basic/Silver/Gold/Platinum | Gold | No NULLs |

---

## 2. dim_products

**Description:** Contains product catalog with pricing and category information.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| product_id | STRING | Unique identifier for each product | System | PROD00001-PROD00300 | PROD00045 | PRIMARY KEY, No NULLs |
| product_name | STRING | Product name with variant | Catalog | 3-100 characters | Smartphone Variant 1 | No NULLs |
| category | STRING | Product category | Catalog | 10 categories | Electronics | No NULLs |
| subcategory | STRING | Product subcategory | Catalog | 100 subcategories | Smartphone | No NULLs |
| cost_price | DECIMAL | Cost price in INR | Catalog | 100-5000 | 1500.00 | No NULLs, Positive |
| selling_price | DECIMAL | Selling price in INR | Catalog | 200-12500 | 2999.00 | ~2% NULL (missing) |
| seller_id | STRING | Seller identifier | System | SELL001-SELL050 | SELL012 | No NULLs |

---

## 3. dim_regions

**Description:** Contains regional reference data.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| region_id | INTEGER | Unique identifier for region | System | 1-10 | 1 | PRIMARY KEY, No NULLs |
| region_name | STRING | Region name | Master data | 10 regions | North | No NULLs |
| country | STRING | Country name | Master data | India | India | No NULLs |
| tier | STRING | City tier classification | Master data | Tier 1/Tier 2/Tier 3 | Tier 1 | No NULLs |

---

## 4. dim_date

**Description:** Date dimension table for time-based analysis.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| date_id | STRING | Date identifier (YYYY-MM-DD) | System | 2023-01-01 to 2024-12-31 | 2023-06-15 | PRIMARY KEY, No NULLs |
| full_date | DATE | Full date value | System | 2023-01-01 to 2024-12-31 | 2023-06-15 | No NULLs |
| year | INTEGER | Year | Derived | 2023-2024 | 2023 | No NULLs |
| quarter | STRING | Quarter (Q1-Q4) | Derived | Q1-Q4 | Q2 | No NULLs |
| month | INTEGER | Month number | Derived | 1-12 | 6 | No NULLs |
| month_name | STRING | Month name | Derived | January-December | June | No NULLs |
| week | INTEGER | Week of year | Derived | 1-53 | 24 | No NULLs |
| day_name | STRING | Day name | Derived | Monday-Sunday | Thursday | No NULLs |
| is_weekend | INTEGER | Weekend flag | Derived | 0 or 1 | 0 | No NULLs |

---

## 5. fact_orders

**Description:** Contains order header information.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| order_id | STRING | Unique identifier for order | System | ORD000001-ORD999999 | ORD001234 | PRIMARY KEY, No NULLs |
| customer_id | STRING | Foreign key to dim_customers | System | CUST00001-CUST99999 | CUST00123 | FOREIGN KEY, No NULLs |
| order_date | DATE | Date order was placed | System | 2023-01-01 to 2025-11-12 | 2023-06-15 | 23 orders (0.4%) dated after 2024-12-31 |
| region_id | INTEGER | Foreign key to dim_regions | System | 1-10 | 1 | FOREIGN KEY, No NULLs |
| status | STRING | Order status | System | Completed/Shipped/Delivered/Cancelled/Returned/Pending | Completed | ~2% NULL (missing) |
| shipping_address | STRING | Delivery address | Customer | 10-200 characters | Address 123, City 5 | No NULLs |

---

## 6. fact_order_items

**Description:** Contains individual line items within each order.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| item_id | STRING | Unique identifier for line item | System | ITEM0000001-ITEM9999999 | ITEM0001234 | PRIMARY KEY, No NULLs |
| order_id | STRING | Foreign key to fact_orders | System | ORD000001-ORD999999 | ORD001234 | FOREIGN KEY, No NULLs |
| product_id | STRING | Foreign key to dim_products | System | PROD00001-PROD00300 | PROD00045 | FOREIGN KEY, No NULLs |
| quantity | INTEGER | Number of units ordered | Order | -10 to 10 | 2 | Negative = return line item (104 rows) |
| unit_price | DECIMAL | Price per unit at time of order | System | 200-12500 | 2999.00 | No NULLs, Positive |
| discount | DECIMAL | Discount fraction (0-0.3) | System | 0-0.30 | 0.10 | No NULLs |
| line_total | DECIMAL | quantity * unit_price * (1-discount) | Calculated | -10000 to 50000 | 5398.20 | No NULLs |

---

## 7. fact_payments

**Description:** Contains payment transaction records.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| payment_id | STRING | Unique identifier for payment | System | PAY0000001-PAY9999999 | PAY0001234 | PRIMARY KEY, No NULLs |
| order_id | STRING | Foreign key to fact_orders | System | ORD000001-ORD999999 | ORD001234 | FOREIGN KEY, No NULLs |
| payment_date | DATE | Date payment was made | System | 2023-01-01 to 2025-01-01 | 2023-06-18 | No NULLs |
| payment_method | STRING | Payment method used | Gateway | Credit Card/Debit Card/UPI/Net Banking/COD/Wallet | UPI | No NULLs |
| amount_paid | DECIMAL | Amount paid in INR | Gateway | 0-100000 | 5398.20 | ~5% mismatch with order |
| status | STRING | Payment status | Gateway | Success/Failed/Pending/Refunded | Success | No NULLs |

---

## 8. fact_refunds

**Description:** Contains refund transaction records.

| Column | Data Type | Definition | Source | Valid Range | Example | Data Quality Rule |
|--------|-----------|------------|--------|-------------|---------|-------------------|
| refund_id | STRING | Unique identifier for refund | System | REF000001-REF999999 | REF001234 | PRIMARY KEY, No NULLs |
| order_id | STRING | Foreign key to fact_orders | System | ORD000001-ORD999999 | ORD001234 | FOREIGN KEY, No NULLs |
| item_id | STRING | Foreign key to fact_order_items | System | ITEM0000001-ITEM9999999 | ITEM0001234 | FOREIGN KEY, No NULLs |
| refund_date | DATE | Date refund was processed | System | 2023-01-01 to 2025-02-01 | 2023-07-01 | No NULLs |
| refund_amount | DECIMAL | Amount refunded in INR | System | 0-50000 | 2999.00 | ~3% > order amount (invalid) |
| reason | STRING | Refund reason | Customer/Cs | Damaged/Wrong Item/Quality Issue/Not as Described/Changed Mind/Late Delivery | Damaged | No NULLs |
| status | STRING | Refund status | System | Approved/Pending/Rejected | Approved | No NULLs |

---

## RELATIONSHIP DIAGRAM

```
dim_customers (1) ──────< (M) fact_orders
                              │
dim_regions (1) ──────< (M)  │
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
          fact_order_items        fact_payments
                    │
                    ▼
          fact_refunds
                    
dim_products (1) ──────< (M) fact_order_items

dim_date (1) ──────< (M) fact_orders
```

---

## PRIMARY KEYS

| Table | Primary Key |
|-------|-------------|
| dim_customers | customer_id |
| dim_products | product_id |
| dim_regions | region_id |
| dim_date | date_id |
| fact_orders | order_id |
| fact_order_items | item_id |
| fact_payments | payment_id |
| fact_refunds | refund_id |

---

## FOREIGN KEYS

| Table | Column | References |
|-------|--------|------------|
| fact_orders | customer_id | dim_customers.customer_id |
| fact_orders | region_id | dim_regions.region_id |
| fact_order_items | order_id | fact_orders.order_id |
| fact_order_items | product_id | dim_products.product_id |
| fact_payments | order_id | fact_orders.order_id |
| fact_refunds | order_id | fact_orders.order_id |
| fact_refunds | item_id | fact_order_items.item_id |

---

*Data Dictionary Version 1.0 — Created 2026-09-07*
