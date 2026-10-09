# RetailEdge - E-Commerce Revenue, Customer & Financial Analytics

## Project Overview

RetailEdge is a comprehensive e-commerce analytics project analyzing revenue, customer behavior, and financial performance. This project demonstrates end-to-end data analytics skills across Excel, MySQL, Python, and Power BI.

---

## Business Problem

An e-commerce company needs to understand:
1. Revenue patterns and growth trends
2. Customer segmentation and behavior
3. Product performance
4. Payment reconciliation and revenue leakage
5. Retention and churn analysis

---

## Data Sources

| Table | Records | Description |
|-------|---------|-------------|
| dim_customers | 1,000 | Customer information |
| dim_products | 300 | Product catalog |
| dim_regions | 10 | Geographic regions |
| fact_orders | 5,150 (5,000 after removing 150 duplicates) | Order transactions |
| fact_order_items | 10,461 | Order line items |
| fact_payments | 5,000 | Payment transactions |
| fact_refunds | 500 | Refund transactions |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Excel | Data validation, PivotTables |
| MySQL | Database storage, SQL queries |
| Python | Data cleaning, EDA, feature engineering |
| Power BI | Dashboard, DAX measures |

---

## Key Findings

### Revenue
- Total Revenue: INR 6.99 Crore
- Net Revenue: INR 6.65 Crore
- Average Order Value: INR 13,987

### Customers
- Total Customers: 996
- Champions: 264 (26.5%)
- At Risk: 156 (15.7%)

### Products
- Top Category: Fashion (10.8%)
- Top Product: PROD00059 (INR 7.78 Lakh)

### Financial
- Payment Match Rate: 95.04% (248 mismatched orders)
- Refund Rate: 4.87%
- Revenue Leakage: 5.30% (INR 37.09 Lakh)

---

## Project Structure

```
PROJECT_1_ECOMMERCE/
├── data/
│   ├── raw/              # Original CSV files
│   ├── processed/        # Cleaned data
│   └── powerbi/          # Power BI import files
├── src/
│   ├── generate_data.py
│   ├── data_cleaning.py
│   ├── data_validation.py
│   ├── feature_engineering.py
│   ├── advanced_business_analysis.py
│   └── powerbi_preparation.py
├── notebooks/
│   └── eda_analysis.py
├── sql/
│   ├── create_database.sql
│   ├── validation_queries.sql
│   └── business_analysis.sql
├── excel/
│   └── retailedge_validation.xlsx
├── powerbi/
│   ├── dax_measures.dax
│   ├── SETUP_GUIDE.md
│   └── DASHBOARD_GUIDE.md
├── reports/
│   └── figures/          # EDA visualizations
├── EXECUTIVE_RECOMMENDATIONS.md
├── DATA_DICTIONARY.md
├── METRIC_DICTIONARY.md
└── README.md
```

---

## Methodology

### 1. Data Collection
- Generated realistic synthetic data
- 7 tables with 22,271 total records (cleaned; 22,652 before de-duplication)

### 2. Data Cleaning (Python)
- Handled missing values
- Removed duplicates
- Fixed invalid values

### 3. Data Validation
- Referential integrity checks
- Payment reconciliation
- Business rule validation

### 4. Feature Engineering
- RFM segmentation
- Customer lifetime value
- Profit margins

### 5. Exploratory Data Analysis
- 18 visualizations
- Univariate, bivariate, multivariate analysis

### 6. SQL Analysis
- 20+ queries for business insights
- Advanced analytics with CTEs, window functions

### 7. Power BI Dashboard
- 5-page interactive dashboard
- 20+ DAX measures

---

## Interview Preparation

### Key Questions and Answers

**Q: What is RFM analysis?**
A: RFM stands for Recency, Frequency, Monetary. It segments customers based on buying behavior.

**Q: What is revenue leakage?**
A: Revenue leakage is money lost due to payment discrepancies, refunds, or errors. In our case, 5.30% of revenue (INR 37.09 Lakh: INR 3.02 Lakh payment gaps + INR 34.07 Lakh refunds).

**Q: How did you validate the data?**
A: I used referential integrity checks, payment reconciliation, and cross-tool validation (Excel, SQL, Python).

---

## Author

Data Analyst Portfolio Project

---

## Date

September 2026
