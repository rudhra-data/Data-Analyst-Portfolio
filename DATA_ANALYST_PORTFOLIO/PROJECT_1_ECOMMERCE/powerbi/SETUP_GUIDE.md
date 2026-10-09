# DAY 9 - Power BI Setup Guide

## STEP 1: Import Data

1. Open Power BI Desktop
2. Click **Get Data** > **Text/CSV**
3. Import these files from `data\powerbi\` folder:

| File | Table Name | Type |
|------|------------|------|
| dim_date.csv | dim_date | Dimension |
| dim_customer.csv | dim_customer | Dimension |
| dim_product.csv | dim_product | Dimension |
| dim_region.csv | dim_region | Dimension |
| fact_order_items.csv | fact_order_items | Fact |
| fact_payments.csv | fact_payments | Fact |
| fact_refunds.csv | fact_refunds | Fact |

---

## STEP 2: Create Relationships

Go to **Model View** and create these relationships:

```
dim_date[date_key] ← fact_order_items[date_key]
dim_customer[customer_id] ← fact_order_items[customer_id]
dim_product[product_id] ← fact_order_items[product_id]
dim_region[region_id] ← fact_order_items[region_id]
fact_order_items[order_id] ← fact_payments[order_id]
fact_order_items[order_id] ← fact_refunds[order_id]
```

---

## STEP 3: Create DAX Measures

1. Go to **Data View**
2. Click **New Measure** for each measure
3. Copy from `powerbi\dax_measures.dax`

### Key Measures to Create:

| Measure | DAX Formula |
|---------|-------------|
| Total Revenue | `SUM(fact_order_items[line_total])` |
| Total Orders | `DISTINCTCOUNT(fact_order_items[order_id])` |
| Total Customers | `DISTINCTCOUNT(fact_order_items[customer_id])` |
| AOV | `DIVIDE([Total Revenue], [Total Orders], 0)` |
| Refund Rate | `DIVIDE([Total Refunds], [Total Revenue], 0) * 100` |
| Profit Margin | `DIVIDE([Total Profit], [Total Revenue], 0) * 100` |

---

## STEP 4: Create Visuals

### Page 1: Executive Dashboard

| Visual | Field | Purpose |
|--------|-------|---------|
| Card | Total Revenue | KPI |
| Card | Total Orders | KPI |
| Card | AOV | KPI |
| Card | Profit Margin | KPI |
| Line Chart | Revenue by Month | Trend |
| Bar Chart | Revenue by Category | Comparison |
| Map | Revenue by Region | Geographic |

### Page 2: Customer Analytics

| Visual | Field | Purpose |
|--------|-------|---------|
| Pie Chart | Customers by Tier | Distribution |
| Bar Chart | Top 10 Customers | Performance |
| Table | RFM Segments | Segmentation |
| Line Chart | Repeat Customer Rate | Retention |

### Page 3: Product Analytics

| Visual | Field | Purpose |
|--------|-------|---------|
| Table | Top 10 Products | Performance |
| Bar Chart | Revenue by Category | Comparison |
| Scatter | Quantity vs Revenue | Analysis |
| Matrix | Category by Region | Cross-tab |

### Page 4: Financial Analytics

| Visual | Field | Purpose |
|--------|-------|---------|
| Card | Revenue Leakage | KPI |
| Card | Payment Match Rate | KPI |
| Bar Chart | Refunds by Category | Analysis |
| Table | Payment Discrepancies | Details |

---

## STEP 5: Format & Publish

1. Add title: "RetailEdge Analytics Dashboard"
2. Add company logo
3. Set color theme
4. Add filters (Date Range, Category, Region)
5. Save as `.pbix` file
6. Publish to Power BI Service (optional)

---

## Interview Questions:

### Q1: What is a star schema?
**Answer:** A star schema has fact tables (transactions) in the center and dimension tables (descriptive attributes) around it. It's optimized for query performance and easy understanding.

### Q2: Why use measures instead of calculated columns?
**Answer:** Measures are calculated on-the-fly when queried, using less memory. Calculated columns are stored in the model and computed for every row, increasing file size.

### Q3: How do you validate Power BI numbers?
**Answer:** I cross-check Power BI totals against SQL query results and Python calculations to ensure consistency across all tools.
