# KPI VALIDATION - Project 1

## Validation Summary

| KPI | Power BI | SQL | Python | Match |
|-----|----------|-----|--------|-------|
| Total Revenue | 69,936,702.76 | 69,936,702.76 | 69,936,702.76 | Yes |
| Total Orders | 5,000 | 5,000 | 5,000 | Yes |
| Total Customers | 996 | 996 | 996 | Yes |
| Total Items (gross units) | 16,794 | 16,794 | 16,794 | Yes |
| AOV | 13,987.34 | 13,987.34 | 13,987.34 | Yes |
| Refund Rate | 4.87% | 4.87% | 4.87% | Yes |
| Payment Match | 95.04% | 95.04% | 95.04% | Yes |
| Revenue Leakage | 37,09,431.67 | 37,09,431.67 | 37,09,431.67 | Yes |

---

## Revenue by Category

| Category | Revenue | Share |
|----------|---------|-------|
| Fashion | 75,81,376.63 | 10.8% |
| Automotive | 73,46,609.90 | 10.5% |
| Toys | 73,26,148.57 | 10.5% |
| Electronics | 73,13,227.50 | 10.5% |
| Grocery | 72,32,192.53 | 10.3% |
| Sports | 71,99,363.83 | 10.3% |
| Beauty | 71,10,710.08 | 10.2% |
| Home & Kitchen | 65,47,573.19 | 9.4% |
| Health | 63,97,110.63 | 9.1% |
| Books | 58,82,389.90 | 8.4% |

---

## RFM Segments

| Segment | Customers | Avg Recency | Avg Frequency | Avg Monetary |
|---------|-----------|-------------|---------------|--------------|
| Champions | 264 | 385 days | 7.5 orders | 116,829 |
| Loyal Customers | 200 | 434 days | 5.6 orders | 80,847 |
| Potential Loyalists | 263 | 461 days | 4.3 orders | 53,867 |
| At Risk | 156 | 534 days | 3.2 orders | 39,703 |
| Lost Customers | 113 | 690 days | 2.3 orders | 22,686 |

---

## Payment Analysis

| Payment Method | Total Amount | Share |
|----------------|--------------|-------|
| Net Banking | 125,35,563.94 | 17.9% |
| Wallet | 118,36,061.81 | 16.9% |
| Debit Card | 116,80,350.78 | 16.7% |
| Cash on Delivery | 116,63,132.53 | 16.7% |
| UPI | 112,90,076.30 | 16.1% |
| Credit Card | 109,33,454.71 | 15.6% |

| Status | Count | Share |
|--------|-------|-------|
| Success | 4,278 | 85.6% |
| Refunded | 243 | 4.9% |
| Failed | 241 | 4.8% |
| Pending | 238 | 4.8% |

---

## Revenue Leakage

| Source | Amount |
|--------|--------|
| Payment Discrepancies | 3,02,328.79 |
| Refunds | 34,07,102.88 |
| Total Leakage | 37,09,431.67 |
| Leakage Rate | 5.30% |

---

## Cohort Retention

| Period | Retention |
|--------|-----------|
| Period 0 | 100.0% |
| Period 1 | 20.6% |
| Period 2 | 17.7% |
| Period 3 | 15.1% |
| Period 6 | 16.7% |
| Period 12 | 9.7% |
| Period 24 | 0.2% |
