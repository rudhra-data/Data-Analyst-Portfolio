# RetailEdge — E-Commerce Revenue, Customer & Financial Analytics

An end-to-end analytics project for a synthetic e-commerce business: from raw transactional data to a validated, executive-ready insight package. Built with **Excel, MySQL, Python, and Power BI**, the project mirrors a real analyst workflow — data cleaning, validation, feature engineering, exploratory analysis, business analytics, SQL, and dashboarding.

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Revenue | INR 6.99 Crore (69,936,702.76) |
| Net Revenue (Payments − Refunds) | INR 6.65 Crore |
| Total Orders / Customers | 5,000 / 996 |
| Average Order Value (AOV) | INR 13,987 |
| Payment Match Rate | 95.04% |
| Revenue Leakage | 5.30% (INR 37.09 Lakh) |
| Month-1 Customer Retention | 20.6% |
| Champions (RFM Segment) | 264 (26.5%) |

---

## Business Problem

The company needed answers to five questions:

1. What are the revenue patterns and growth trends?
2. Who are the best and most at-risk customers?
3. Which products and categories drive revenue?
4. Where is money being lost to payment mismatches and refunds?
5. How many customers come back, and what drives churn?

---

## Data Sources

7 tables, 22,271 records (after de-duplication).

| Table | Records | Description |
|-------|---------|-------------|
| dim_customers | 1,000 | Customer information |
| dim_products | 300 | Product catalog |
| dim_regions | 10 | Geographic regions |
| fact_orders | 5,150 → 5,000 | Orders (150 duplicates removed) |
| fact_order_items | 10,461 | Order line items |
| fact_payments | 5,000 | Payment transactions |
| fact_refunds | 500 | Refund transactions |

---

## Tools & Skills Demonstrated

| Tool | What it was used for |
|------|----------------------|
| Excel | Data-quality checks, reconciliation workbook, PivotTables |
| MySQL | Schema design, views, 20+ analytical queries (CTEs, window functions) |
| Python | Data cleaning, validation, feature engineering, EDA, advanced analytics |
| Power BI | 5-page dashboard, 20+ DAX measures, data model (star schema) |

---

## Key Findings

### Revenue
- Total Revenue: INR 6.99 Crore
- Net Revenue: INR 6.65 Crore
- Average Order Value: INR 13,987
- Top Category: Fashion at ~10.8% of revenue
- Top Product: **PROD00059** (INR 7.78 Lakh)

### Customers
- 996 active customers (of 1,000 registered)
- Champions: 264 (26.5%) — highest-value, most recent buyers
- At Risk: 156 (15.7%) — high value but fading
- Month-1 Retention: 20.6%

### Financial Health
- Payment Match Rate: **95.04%** (248 orders mismatch)
- Refund Rate: 4.87%
- Revenue Leakage: **5.30% (INR 37.09 Lakh)** = INR 3.02 Lakh payment gaps + INR 34.07 Lakh refunds

**Recommended next steps:** fix payment reconciliation for the 248 mismatched orders, tighten the refund process, and run a reactivation campaign for the 156 at-risk customers. Full recommendations in [`EXECUTIVE_RECOMMENDATIONS.md`](EXECUTIVE_RECOMMENDATIONS.md).

---

## Dashboard

The Power BI dashboard is a 5-page interactive report driven by a star schema and DAX measures. The source file is [`powerbi/RetailEdge_Dashboard.pbix`](powerbi/RetailEdge_Dashboard.pbix).

<!-- Dashboard screenshots belong here - add your page screenshots under reports/dashboard/ and embed them below -->

---

## Project Structure

```
PROJECT_1_ECOMMERCE/
├── data/
│   ├── raw/                  # Original CSV files
│   ├── processed/            # Cleaned + engineered data
│   └── powerbi/              # Star-schema files imported into Power BI
├── src/
│   ├── generate_data.py
│   ├── data_cleaning.py
│   ├── data_validation.py
│   ├── feature_engineering.py
│   ├── advanced_business_analysis.py
│   ├── create_excel_validation.py
│   ├── load_to_mysql.py
│   ├── powerbi_preparation.py
│   └── project_config.py     # Central, portable path configuration
├── notebooks/
│   ├── eda_analysis.py       # EDA engine used by the pipeline
│   └── project1_eda.py       # Standalone EDA script
├── sql/
│   ├── create_database.sql
│   ├── validation_queries.sql
│   └── business_analysis.sql
├── excel/
│   └── retailedge_validation.xlsx    # Validation & reconciliation workbook
├── powerbi/
│   ├── RetailEdge_Dashboard.pbix    # Power BI project file
│   ├── dax_measures.dax
│   ├── SETUP_GUIDE.md
│   ├── KPI_VALIDATION.md
│   └── DASHBOARD_GUIDE.md
├── reports/
│   ├── figures/             # 18 EDA visualizations
│   ├── business_analysis/   # RFM, cohort, leakage outputs
│   └── dashboard/           # Power BI screenshots (add yours here)
├── EXECUTIVE_RECOMMENDATIONS.md
├── DATA_DICTIONARY.md
├── METRIC_DICTIONARY.md
└── README.md
```

---

## How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run the analysis pipeline

```
python main_analysis.py                    # Cleaning → Validation → Features → EDA (18 figures)
```

### 3. Run advanced business analytics

```
python src/advanced_business_analysis.py   # RFM segments, cohort retention, revenue leakage
python src/create_excel_validation.py      # Builds excel/retailedge_validation.xlsx
```

### 4. Load data into MySQL

1. Create the schema and views: run `sql/create_database.sql`.
2. Create a `.env` file in the project root with your connection details:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=retailedge_db
```

3. Load the data:

```
python src/load_to_mysql.py
```

### 5. Power BI

1. Regenerate the star-schema files (if needed): `python src/powerbi_preparation.py`.
2. Follow [`powerbi/SETUP_GUIDE.md`](powerbi/SETUP_GUIDE.md) to build the model and measures.
3. Compare every KPI across tools in [`powerbi/KPI_VALIDATION.md`](powerbi/KPI_VALIDATION.md).

All paths resolve relative to the project via `src/project_config.py`, so the code runs from any working directory.

---

## Methodology

1. **Data Collection** — realistic synthetic e-commerce data (7 tables).
2. **Data Cleaning (Python)** — handled missing values, removed 150 duplicate orders, normalised returns.
3. **Data Validation** — referential integrity, business rules, and payment reconciliation checks.
4. **Feature Engineering** — RFM segmentation, monthly aggregates, product/order/customer features.
5. **Exploratory Data Analysis** — 18 visualizations (univariate, bivariate, multivariate).
6. **SQL Analysis** — 20+ queries using CTEs, window functions, and a reconciliation view.
7. **Power BI** — star-schema data model, 20+ DAX measures, 5-page dashboard.
8. **Cross-Tool Validation** — every KPI confirmed identical in Excel, SQL, and Python.

---

## Interview Prep

**Q: What is RFM analysis?**
A: RFM stands for Recency, Frequency, Monetary value. It segments customers by how recently they bought, how often, and how much they spend — from which I identified Champions, Loyal, Potential Loyalists, At-Risk, and Lost segments.

**Q: What is revenue leakage?**
A: Money lost to payment discrepancies, refunds, or errors. Here it is **5.30%** of revenue (INR 37.09 Lakh) — INR 3.02 Lakh from payment mismatches across 248 orders, plus INR 34.07 Lakh in refunds.

**Q: How did you validate the data?**
A: I combined referential-integrity checks, payment reconciliation, and cross-tool verification — every KPI was compared across Excel, SQL, and Python and matched exactly.

**Q: How do you measure customer retention?**
A: Cohort analysis — I group customers by their first-purchase month and track what percentage return in each following month. Month-1 retention here is 20.6%.

---

## Documentation

- [`EXECUTIVE_RECOMMENDATIONS.md`](EXECUTIVE_RECOMMENDATIONS.md) — business recommendations with measurable targets
- [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) — every table and field explained
- [`METRIC_DICTIONARY.md`](METRIC_DICTIONARY.md) — every KPI: formula, meaning, and caveats
- [`powerbi/KPI_VALIDATION.md`](powerbi/KPI_VALIDATION.md) — Excel vs SQL vs Python numbers
- [`powerbi/DASHBOARD_GUIDE.md`](powerbi/DASHBOARD_GUIDE.md) — how to read each dashboard page

---

## Author

**Rudhra Patel** — Data Analyst Portfolio Project

- GitHub: [github.com/rudhra-data](https://github.com/rudhra-data)
- Email: work.rudhra@gmail.com

---

*October 2026*