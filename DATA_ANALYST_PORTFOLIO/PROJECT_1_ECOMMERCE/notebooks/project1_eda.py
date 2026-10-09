import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from pathlib import Path

SRC_DIR = str(Path(__file__).resolve().parents[1] / 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from project_config import RAW_DATA_PATH, FIGURES_PATH

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("="*60)
print("RETAILEDGE - PYTHON EDA")
print("="*60)

# ============================================
# STEP 1: LOAD DATA
# ============================================
print("\n--- STEP 1: Loading Data ---")

base_path = RAW_DATA_PATH

customers = pd.read_csv(os.path.join(base_path, 'dim_customers.csv'))
products = pd.read_csv(os.path.join(base_path, 'dim_products.csv'))
regions = pd.read_csv(os.path.join(base_path, 'dim_regions.csv'))
orders = pd.read_csv(os.path.join(base_path, 'fact_orders.csv'))
order_items = pd.read_csv(os.path.join(base_path, 'fact_order_items.csv'))
payments = pd.read_csv(os.path.join(base_path, 'fact_payments.csv'))
refunds = pd.read_csv(os.path.join(base_path, 'fact_refunds.csv'))

print("All files loaded!")

# ============================================
# STEP 2: DATA PROFILING
# ============================================
print("\n--- STEP 2: Data Profiling ---")

dataframes = {
    'customers': customers,
    'products': products,
    'regions': regions,
    'orders': orders,
    'order_items': order_items,
    'payments': payments,
    'refunds': refunds
}

for name, df in dataframes.items():
    print(f"\n{name.upper()}:")
    print(f"  Rows: {len(df)}, Columns: {df.shape[1]}")
    print(f"  Missing: {df.isnull().sum().sum()}")
    print(f"  Duplicates: {df.duplicated().sum()}")

# ============================================
# STEP 3: DATA CLEANING
# ============================================
print("\n--- STEP 3: Data Cleaning ---")

# Handle missing values
customers['email'] = customers['email'].fillna('unknown@email.com')
customers['city'] = customers['city'].fillna('Unknown')
products['selling_price'] = pd.to_numeric(products['selling_price'], errors='coerce').fillna(0)
orders['status'] = orders['status'].fillna('Unknown')

# Remove duplicates
orders = orders.drop_duplicates(subset=['order_id'], keep='first')
order_items = order_items.drop_duplicates(subset=['item_id'], keep='first')
payments = payments.drop_duplicates(subset=['payment_id'], keep='first')
refunds = refunds.drop_duplicates(subset=['refund_id'], keep='first')

# Keep negative quantities as return line items (line_total stays consistent)
returns = order_items[order_items['quantity'] < 0]
print(f"  Return line items (negative quantity): {len(returns)}")

print("Cleaning complete!")
print(f"  Orders after dedup: {len(orders)}")
print(f"  Order items after dedup: {len(order_items)}")

# ============================================
# STEP 4: FEATURE ENGINEERING
# ============================================
print("\n--- STEP 4: Feature Engineering ---")

# Merge orders with order_items
orders_full = order_items.merge(orders, on='order_id', how='left')
orders_full = orders_full.merge(products[['product_id', 'category', 'subcategory']], on='product_id', how='left')
orders_full = orders_full.merge(customers[['customer_id', 'membership_tier', 'city']], on='customer_id', how='left')
orders_full = orders_full.merge(regions[['region_id', 'region_name']], on='region_id', how='left')

# Add order month
orders_full['order_date'] = pd.to_datetime(orders_full['order_date'], errors='coerce')
orders_full['order_month'] = orders_full['order_date'].dt.to_period('M')

# Calculate order total per order
order_totals = orders_full.groupby('order_id')['line_total'].sum().reset_index()
order_totals.columns = ['order_id', 'order_total']

# Merge order totals
orders_full = orders_full.merge(order_totals, on='order_id', how='left')

print("Feature engineering complete!")
print(f"  Merged dataset shape: {orders_full.shape}")

# ============================================
# STEP 5: EDA - UNIVARIATE ANALYSIS
# ============================================
print("\n--- STEP 5: EDA - Univariate Analysis ---")

# Save figures folder
figures_path = FIGURES_PATH
os.makedirs(figures_path, exist_ok=True)

# 1. Revenue Distribution
plt.figure(figsize=(10, 6))
plt.hist(orders_full['line_total'], bins=50, color='steelblue', edgecolor='black')
plt.title('Revenue Distribution', fontsize=14)
plt.xlabel('Line Total (INR)')
plt.ylabel('Frequency')
plt.savefig(os.path.join(figures_path, '01_revenue_distribution.png'))
plt.show()
print("  Plot 1: Revenue Distribution saved")

# 2. Orders by Status
plt.figure(figsize=(10, 6))
status_counts = orders['status'].value_counts()
status_counts.plot(kind='bar', color='coral', edgecolor='black')
plt.title('Orders by Status', fontsize=14)
plt.xlabel('Status')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.savefig(os.path.join(figures_path, '02_orders_by_status.png'))
plt.show()
print("  Plot 2: Orders by Status saved")

# 3. Customers by Membership Tier
plt.figure(figsize=(8, 6))
tier_counts = customers['membership_tier'].value_counts()
tier_counts.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
plt.title('Customer Distribution by Membership Tier', fontsize=14)
plt.ylabel('')
plt.savefig(os.path.join(figures_path, '03_customers_by_tier.png'))
plt.show()
print("  Plot 3: Customers by Tier saved")

# ============================================
# STEP 6: EDA - BIVARIATE ANALYSIS
# ============================================
print("\n--- STEP 6: EDA - Bivariate Analysis ---")

# 4. Revenue by Category
plt.figure(figsize=(12, 6))
category_revenue = orders_full.groupby('category')['line_total'].sum().sort_values(ascending=False)
category_revenue.plot(kind='bar', color='teal', edgecolor='black')
plt.title('Total Revenue by Category', fontsize=14)
plt.xlabel('Category')
plt.ylabel('Revenue (INR)')
plt.xticks(rotation=45)
plt.savefig(os.path.join(figures_path, '04_revenue_by_category.png'))
plt.show()
print("  Plot 4: Revenue by Category saved")

# 5. Revenue by Region
plt.figure(figsize=(12, 6))
region_revenue = orders_full.groupby('region_name')['line_total'].sum().sort_values(ascending=False)
region_revenue.plot(kind='bar', color='mediumpurple', edgecolor='black')
plt.title('Total Revenue by Region', fontsize=14)
plt.xlabel('Region')
plt.ylabel('Revenue (INR)')
plt.xticks(rotation=45)
plt.savefig(os.path.join(figures_path, '05_revenue_by_region.png'))
plt.show()
print("  Plot 5: Revenue by Region saved")

# 6. Refund Amount by Category
plt.figure(figsize=(12, 6))
refunds_merged = refunds.merge(order_items[['item_id', 'product_id']], on='item_id', how='left')
refunds_merged = refunds_merged.merge(products[['product_id', 'category']], on='product_id', how='left')
category_refunds = refunds_merged.groupby('category')['refund_amount'].sum().sort_values(ascending=False)
category_refunds.plot(kind='bar', color='salmon', edgecolor='black')
plt.title('Total Refund Amount by Category', fontsize=14)
plt.xlabel('Category')
plt.ylabel('Refund Amount (INR)')
plt.xticks(rotation=45)
plt.savefig(os.path.join(figures_path, '06_refunds_by_category.png'))
plt.show()
print("  Plot 6: Refunds by Category saved")

# ============================================
# STEP 7: EDA - MULTIVARIATE ANALYSIS
# ============================================
print("\n--- STEP 7: EDA - Multivariate Analysis ---")

# 7. Monthly Revenue Trend
plt.figure(figsize=(14, 6))
monthly_revenue = orders_full.groupby('order_month')['line_total'].sum()
monthly_revenue.plot(kind='line', marker='o', color='darkgreen', linewidth=2)
plt.title('Monthly Revenue Trend', fontsize=14)
plt.xlabel('Month')
plt.ylabel('Revenue (INR)')
plt.xticks(rotation=45)
plt.savefig(os.path.join(figures_path, '07_monthly_revenue_trend.png'))
plt.show()
print("  Plot 7: Monthly Revenue Trend saved")

# 8. Revenue by Category and Membership Tier
plt.figure(figsize=(14, 6))
pivot_table = orders_full.pivot_table(values='line_total', index='category', columns='membership_tier', aggfunc='sum')
pivot_table.plot(kind='bar', figsize=(14, 6))
plt.title('Revenue by Category and Membership Tier', fontsize=14)
plt.xlabel('Category')
plt.ylabel('Revenue (INR)')
plt.xticks(rotation=45)
plt.legend(title='Membership Tier')
plt.savefig(os.path.join(figures_path, '08_category_by_tier.png'))
plt.show()
print("  Plot 8: Category by Tier saved")

# 9. Correlation Heatmap
plt.figure(figsize=(10, 8))
numeric_cols = orders_full[['quantity', 'unit_price', 'discount', 'line_total', 'order_total']]
correlation = numeric_cols.corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('Correlation Heatmap', fontsize=14)
plt.savefig(os.path.join(figures_path, '09_correlation_heatmap.png'))
plt.show()
print("  Plot 9: Correlation Heatmap saved")

# ============================================
# STEP 8: SUMMARY STATISTICS
# ============================================
print("\n--- STEP 8: Summary Statistics ---")

print("\nRevenue Statistics:")
print(f"  Total Revenue: ₹{orders_full['line_total'].sum():,.2f}")
print(f"  Average Order Value: ₹{orders_full.groupby('order_id')['line_total'].sum().mean():,.2f}")
print(f"  Median Order Value: ₹{orders_full.groupby('order_id')['line_total'].sum().median():,.2f}")
print(f"  Max Order Value: ₹{orders_full.groupby('order_id')['line_total'].sum().max():,.2f}")
print(f"  Min Order Value: ₹{orders_full.groupby('order_id')['line_total'].sum().min():,.2f}")

print("\nRefund Statistics:")
print(f"  Total Refunds: ₹{refunds['refund_amount'].sum():,.2f}")
print(f"  Refund Rate: {refunds['refund_amount'].sum() / orders_full['line_total'].sum() * 100:.2f}%")

print("\nCustomer Statistics:")
print(f"  Total Customers (registered): {len(customers):,}")
print(f"  Customers with orders: {orders['customer_id'].nunique():,}")
print(f"  Total Orders: {len(orders)}")
print(f"  Orders per Customer: {len(orders) / orders['customer_id'].nunique():.2f}")

# ============================================
# STEP 9: KEY INSIGHTS
# ============================================
print("\n" + "="*60)
print("KEY INSIGHTS")
print("="*60)

total_revenue = orders_full['line_total'].sum()
total_refunds = refunds['refund_amount'].sum()
category_revenue = orders_full.groupby('category')['line_total'].sum().sort_values(ascending=False)

order_tot = order_items.groupby('order_id')['line_total'].sum()
pay_tot = payments.groupby('order_id')['amount_paid'].sum()
recon = pd.concat([order_tot.rename('order_total'), pay_tot.rename('payment_total')], axis=1).fillna(0)
mismatch = (recon['order_total'] - recon['payment_total']).abs() > 0.01

tier_spend = orders_full.groupby('membership_tier')['line_total'].sum() / orders_full.groupby('membership_tier')['customer_id'].nunique()

print(f"""
1. REVENUE INSIGHTS:
   - Total Revenue: ₹{total_revenue/1e7:.2f} Crore
   - Top Category: {category_revenue.index[0]} (₹{category_revenue.iloc[0]/1e5:.1f} Lakh)
   - Bottom Category: {category_revenue.index[-1]} (₹{category_revenue.iloc[-1]/1e5:.1f} Lakh)

2. CUSTOMER INSIGHTS:
   - {orders['customer_id'].nunique():,} customers placed orders
   - Highest spend/customer tier: {tier_spend.idxmax()} (₹{tier_spend.max():,.0f})
   - Lowest spend/customer tier: {tier_spend.idxmin()} (₹{tier_spend.min():,.0f})

3. PAYMENT INSIGHTS:
   - {int(mismatch.sum()):,} orders have payment mismatches ({mismatch.mean()*100:.2f}%)
   - Payment match rate: {(1 - mismatch.mean())*100:.2f}%

4. REFUND INSIGHTS:
   - Total Refund Rate: {total_refunds/total_revenue*100:.2f}%
   - Total Refund Amount: ₹{total_refunds/1e5:.2f} Lakh

5. REGIONAL INSIGHTS:
   - Top region: {orders_full.groupby('region_name')['line_total'].sum().idxmax()}
   - Lowest region: {orders_full.groupby('region_name')['line_total'].sum().idxmin()}
""")

print("="*60)
print("EDA COMPLETE!")
print("="*60)
