import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

SRC_DIR = str(Path(__file__).resolve().parent)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from project_config import RAW_DATA_PATH, EXCEL_PATH

print("Creating Excel Validation Workbook...")

# ============================================
# LOAD ALL CSV FILES
# ============================================
print("Loading CSV files...")

customers = pd.read_csv(RAW_DATA_PATH / 'dim_customers.csv')
products = pd.read_csv(RAW_DATA_PATH / 'dim_products.csv')
regions = pd.read_csv(RAW_DATA_PATH / 'dim_regions.csv')
orders = pd.read_csv(RAW_DATA_PATH / 'fact_orders.csv')
order_items = pd.read_csv(RAW_DATA_PATH / 'fact_order_items.csv')
payments = pd.read_csv(RAW_DATA_PATH / 'fact_payments.csv')
refunds = pd.read_csv(RAW_DATA_PATH / 'fact_refunds.csv')

print("All files loaded!")

# ============================================
# SHEET 1: DATA SUMMARY
# ============================================
print("Creating Sheet 1: Data Summary...")

summary_data = {
    'Table': ['dim_customers', 'dim_products', 'dim_regions', 'fact_orders', 'fact_order_items', 'fact_payments', 'fact_refunds'],
    'Total Rows': [len(customers), len(products), len(regions), len(orders), len(order_items), len(payments), len(refunds)],
    'Total Columns': [customers.shape[1], products.shape[1], regions.shape[1], orders.shape[1], order_items.shape[1], payments.shape[1], refunds.shape[1]],
    'Memory (KB)': [
        round(customers.memory_usage(deep=True).sum() / 1024, 2),
        round(products.memory_usage(deep=True).sum() / 1024, 2),
        round(regions.memory_usage(deep=True).sum() / 1024, 2),
        round(orders.memory_usage(deep=True).sum() / 1024, 2),
        round(order_items.memory_usage(deep=True).sum() / 1024, 2),
        round(payments.memory_usage(deep=True).sum() / 1024, 2),
        round(refunds.memory_usage(deep=True).sum() / 1024, 2)
    ]
}
df_summary = pd.DataFrame(summary_data)

# ============================================
# SHEET 2: MISSING VALUES
# ============================================
print("Creating Sheet 2: Missing Values...")

missing_data = []
for name, df in [('dim_customers', customers), ('dim_products', products), ('fact_orders', orders), 
                  ('fact_order_items', order_items), ('fact_payments', payments), ('fact_refunds', refunds)]:
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            missing_data.append({
                'Table': name,
                'Column': col,
                'Missing Count': null_count,
                'Missing %': round((null_count / len(df)) * 100, 2)
            })

df_missing = pd.DataFrame(missing_data)

# ============================================
# SHEET 3: DUPLICATE CHECK
# ============================================
print("Creating Sheet 3: Duplicate Check...")

duplicate_data = []
for name, df in [('fact_orders', orders), ('fact_order_items', order_items), ('fact_payments', payments)]:
    dup_count = df.duplicated().sum()
    duplicate_data.append({
        'Table': name,
        'Total Rows': len(df),
        'Duplicate Rows': dup_count,
        'Duplicate %': round((dup_count / len(df)) * 100, 2)
    })

df_duplicates = pd.DataFrame(duplicate_data)

# ============================================
# SHEET 4: INVALID VALUES
# ============================================
print("Creating Sheet 4: Invalid Values...")

invalid_data = []

# Check negative quantities in order_items
neg_qty = order_items[order_items['quantity'] < 0]
invalid_data.append({
    'Check': 'Negative Quantities',
    'Table': 'fact_order_items',
    'Issue Count': len(neg_qty),
    'Description': 'Orders with quantity < 0'
})

# Check future dates in orders
orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
future_dates = orders[orders['order_date'] > datetime.now()]
invalid_data.append({
    'Check': 'Future Dates',
    'Table': 'fact_orders',
    'Issue Count': len(future_dates),
    'Description': 'Orders with date in future'
})

# Check missing status in orders
missing_status = orders[orders['status'].isnull()]
invalid_data.append({
    'Check': 'Missing Status',
    'Table': 'fact_orders',
    'Issue Count': len(missing_status),
    'Description': 'Orders with NULL status'
})

# Check refund amount > order amount
refunds_merged = refunds.merge(order_items, on='item_id', how='left', suffixes=('_refund', '_item'))
over_refund = refunds_merged[refunds_merged['refund_amount'] > refunds_merged['line_total']]
invalid_data.append({
    'Check': 'Refund > Order Amount',
    'Table': 'fact_refunds',
    'Issue Count': len(over_refund),
    'Description': 'Refunds exceeding order item amount'
})

df_invalid = pd.DataFrame(invalid_data)

# ============================================
# SHEET 5: RECONCILIATION
# ============================================
print("Creating Sheet 5: Reconciliation...")

# Calculate totals
total_order_value = order_items.groupby('order_id')['line_total'].sum().reset_index()
total_order_value.columns = ['order_id', 'order_total']

total_payment = payments.groupby('order_id')['amount_paid'].sum().reset_index()
total_payment.columns = ['order_id', 'payment_total']

total_refund = refunds.groupby('order_id')['refund_amount'].sum().reset_index()
total_refund.columns = ['order_id', 'refund_total']

# Merge all
recon = total_order_value.merge(total_payment, on='order_id', how='outer')
recon = recon.merge(total_refund, on='order_id', how='outer')
recon = recon.fillna(0)

# Calculate differences
recon['payment_diff'] = recon['order_total'] - recon['payment_total']
recon['has_discrepancy'] = recon['payment_diff'].abs() > 0.01
recon['discrepancy_type'] = recon['payment_diff'].apply(
    lambda x: 'Underpayment' if x > 0.01 else ('Overpayment' if x < -0.01 else 'Matched')
)

# Summary
recon_summary = {
    'Metric': [
        'Total Orders',
        'Total Order Value',
        'Total Payments',
        'Total Refunds',
        'Net Revenue (Payments - Refunds)',
        'Orders with Discrepancy',
        'Discrepancy Amount',
        'Discrepancy %'
    ],
    'Value': [
        len(recon),
        round(recon['order_total'].sum(), 2),
        round(recon['payment_total'].sum(), 2),
        round(recon['refund_total'].sum(), 2),
        round(recon['payment_total'].sum() - recon['refund_total'].sum(), 2),
        recon['has_discrepancy'].sum(),
        round(recon[recon['has_discrepancy']]['payment_diff'].abs().sum(), 2),
        round((recon['has_discrepancy'].sum() / len(recon)) * 100, 2)
    ]
}
df_recon_summary = pd.DataFrame(recon_summary)

# ============================================
# SHEET 6: PIVOT BY CATEGORY
# ============================================
print("Creating Sheet 6: Pivot by Category...")

# Merge order_items with products to get category
items_with_category = order_items.merge(products[['product_id', 'category']], on='product_id', how='left')

# Pivot by category
pivot_category = items_with_category.groupby('category').agg(
    Total_Items=('item_id', 'count'),
    Total_Quantity=('quantity', 'sum'),
    Total_Revenue=('line_total', 'sum'),
    Avg_Order_Value=('line_total', 'mean')
).round(2).reset_index()

pivot_category.columns = ['Category', 'Total Items', 'Total Quantity', 'Total Revenue', 'Avg Order Value']
pivot_category = pivot_category.sort_values('Total Revenue', ascending=False)

# ============================================
# SHEET 7: PIVOT BY REGION
# ============================================
print("Creating Sheet 7: Pivot by Region...")

# Merge orders with regions
orders_with_region = orders.merge(regions[['region_id', 'region_name']], on='region_id', how='left')
orders_with_region = orders_with_region.merge(
    order_items.groupby('order_id')['line_total'].sum().reset_index(), 
    on='order_id', how='left'
)

pivot_region = orders_with_region.groupby('region_name').agg(
    Total_Orders=('order_id', 'count'),
    Total_Revenue=('line_total', 'sum'),
    Avg_Order_Value=('line_total', 'mean')
).round(2).reset_index()

pivot_region.columns = ['Region', 'Total Orders', 'Total Revenue', 'Avg Order Value']
pivot_region = pivot_region.sort_values('Total Revenue', ascending=False)

# ============================================
# SHEET 8: PAYMENT METHOD ANALYSIS
# ============================================
print("Creating Sheet 8: Payment Method Analysis...")

payment_analysis = payments.groupby('payment_method').agg(
    Total_Transactions=('payment_id', 'count'),
    Total_Amount=('amount_paid', 'sum'),
    Avg_Payment=('amount_paid', 'mean'),
    Failed_Count=('status', lambda x: (x == 'Failed').sum())
).round(2).reset_index()

payment_analysis.columns = ['Payment Method', 'Total Transactions', 'Total Amount', 'Avg Payment', 'Failed Count']
payment_analysis['Failure Rate %'] = round((payment_analysis['Failed Count'] / payment_analysis['Total Transactions']) * 100, 2)

# ============================================
# SAVE TO EXCEL
# ============================================
print("\nSaving Excel file...")

excel_path = EXCEL_PATH / 'retailedge_validation.xlsx'

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_summary.to_excel(writer, sheet_name='Data Summary', index=False)
    df_missing.to_excel(writer, sheet_name='Missing Values', index=False)
    df_duplicates.to_excel(writer, sheet_name='Duplicate Check', index=False)
    df_invalid.to_excel(writer, sheet_name='Invalid Values', index=False)
    df_recon_summary.to_excel(writer, sheet_name='Reconciliation', index=False)
    pivot_category.to_excel(writer, sheet_name='Pivot by Category', index=False)
    pivot_region.to_excel(writer, sheet_name='Pivot by Region', index=False)
    payment_analysis.to_excel(writer, sheet_name='Payment Analysis', index=False)

print(f"\nExcel file saved to: {excel_path}")

# ============================================
# PRINT SUMMARY
# ============================================
print("\n" + "="*60)
print("EXCEL VALIDATION WORKBOOK CREATED SUCCESSFULLY!")
print("="*60)

print("\n--- SHEETS CREATED ---")
print("1. Data Summary")
print("2. Missing Values")
print("3. Duplicate Check")
print("4. Invalid Values")
print("5. Reconciliation")
print("6. Pivot by Category")
print("7. Pivot by Region")
print("8. Payment Analysis")

print("\n--- KEY FINDINGS ---")
print(f"Total Missing Values Found: {df_missing['Missing Count'].sum()}")
print(f"Total Duplicates Found: {df_duplicates['Duplicate Rows'].sum()}")
print(f"Total Invalid Values Found: {df_invalid['Issue Count'].sum()}")
print(f"Orders with Payment Discrepancy: {recon['has_discrepancy'].sum()} ({round((recon['has_discrepancy'].sum()/len(recon))*100, 2)}%)")

print("\nExcel validation workbook complete!")
