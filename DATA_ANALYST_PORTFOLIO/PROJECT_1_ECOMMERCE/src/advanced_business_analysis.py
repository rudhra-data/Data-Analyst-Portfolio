"""
RETAILEDGE - Advanced Business Analysis (Day 8)
=================================================
Revenue Analysis, Customer Segmentation, Cohort Analysis, Revenue Leakage
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

SRC_DIR = str(Path(__file__).resolve().parent)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from project_config import PROCESSED_DATA_PATH, BUSINESS_ANALYSIS_PATH

class AdvancedBusinessAnalysis:
    """Advanced business analytics for RetailEdge"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.output_path = BUSINESS_ANALYSIS_PATH
        
        # Create output directory
        import os
        os.makedirs(self.output_path, exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load all cleaned data"""
        print("\nLoading data...")
        self.orders = pd.read_csv(f"{self.data_path}\\orders_clean.csv", parse_dates=['order_date'])
        self.order_items = pd.read_csv(f"{self.data_path}\\order_items_clean.csv")
        self.payments = pd.read_csv(f"{self.data_path}\\payments_clean.csv")
        self.refunds = pd.read_csv(f"{self.data_path}\\refunds_clean.csv")
        self.customers = pd.read_csv(f"{self.data_path}\\customers_clean.csv", parse_dates=['signup_date'])
        self.products = pd.read_csv(f"{self.data_path}\\products_clean.csv")
        
        # Merge orders with customer info
        order_totals = self.order_items.groupby('order_id')['line_total'].sum().reset_index()
        order_totals.columns = ['order_id', 'order_total']
        
        self.orders = self.orders.merge(order_totals, on='order_id', how='left')
        self.orders['order_total'] = self.orders['order_total'].fillna(0)
        
        self.orders_full = self.orders.merge(
            self.customers[['customer_id', 'membership_tier', 'signup_date']], 
            on='customer_id', how='left'
        )
        
        # Merge order items with product info
        self.items_full = self.order_items.merge(
            self.products[['product_id', 'category', 'selling_price']], 
            on='product_id', how='left', suffixes=('_item', '_product')
        )
        
        print(f"  Loaded {len(self.orders)} orders")
        print(f"  Loaded {len(self.order_items)} order items")
        print(f"  Loaded {len(self.customers)} customers")
    
    def revenue_analysis(self):
        """Comprehensive revenue analysis"""
        print("\n" + "="*70)
        print("REVENUE ANALYSIS")
        print("="*70)
        
        # Total metrics (order_total already calculated in load_data)
        total_revenue = self.orders['order_total'].sum()
        total_orders = len(self.orders)
        avg_order_value = self.orders['order_total'].mean()
        total_payments = self.payments['amount_paid'].sum()
        total_refunds = self.refunds['refund_amount'].sum()
        net_revenue = total_revenue - total_refunds
        
        print(f"\n--- Revenue Summary ---")
        print(f"  Total Revenue: INR {total_revenue:,.2f}")
        print(f"  Total Payments: INR {total_payments:,.2f}")
        print(f"  Total Refunds: INR {total_refunds:,.2f}")
        print(f"  Net Revenue: INR {net_revenue:,.2f}")
        print(f"  Total Orders: {total_orders:,}")
        print(f"  Average Order Value: INR {avg_order_value:,.2f}")
        
        # Revenue by category
        revenue_by_category = self.items_full.groupby('category').agg(
            revenue=('line_total', 'sum'),
            items_sold=('quantity', 'sum'),
            avg_item_value=('line_total', 'mean')
        ).sort_values('revenue', ascending=False)
        
        print(f"\n--- Revenue by Category ---")
        for cat, row in revenue_by_category.head(5).iterrows():
            pct = (row['revenue'] / total_revenue) * 100
            print(f"  {cat}: INR {row['revenue']:,.2f} ({pct:.1f}%)")
        
        # Revenue by region
        revenue_by_region = self.orders.groupby('region_id').agg(
            revenue=('order_total', 'sum'),
            orders=('order_id', 'count'),
            avg_order=('order_total', 'mean')
        ).sort_values('revenue', ascending=False)
        
        print(f"\n--- Revenue by Region ---")
        for reg, row in revenue_by_region.iterrows():
            pct = (row['revenue'] / total_revenue) * 100
            print(f"  Region {reg}: INR {row['revenue']:,.2f} ({pct:.1f}%)")
        
        # Monthly revenue trend
        self.orders['order_month'] = self.orders['order_date'].dt.to_period('M')
        monthly_revenue = self.orders.groupby('order_month').agg(
            revenue=('order_total', 'sum'),
            orders=('order_id', 'count')
        )
        
        print(f"\n--- Monthly Revenue Trend ---")
        for month, row in monthly_revenue.iterrows():
            print(f"  {month}: INR {row['revenue']:,.2f} ({row['orders']:,} orders)")
        
        return {
            'total_revenue': total_revenue,
            'net_revenue': net_revenue,
            'revenue_by_category': revenue_by_category,
            'revenue_by_region': revenue_by_region,
            'monthly_revenue': monthly_revenue
        }
    
    def customer_analysis(self):
        """Customer segmentation and behavior analysis"""
        print("\n" + "="*70)
        print("CUSTOMER ANALYSIS")
        print("="*70)
        
        # Customer metrics
        customer_metrics = self.orders.groupby('customer_id').agg(
            total_orders=('order_id', 'count'),
            total_spend=('order_total', 'sum'),
            avg_order_value=('order_total', 'mean'),
            last_order_date=('order_date', 'max'),
            first_order_date=('order_date', 'min')
        )
        
        # Calculate tenure
        customer_metrics['tenure_days'] = (datetime.now() - customer_metrics['first_order_date']).dt.days
        
        # Membership tier distribution
        tier_dist = self.customers['membership_tier'].value_counts()
        print(f"\n--- Membership Tier Distribution ---")
        for tier, count in tier_dist.items():
            pct = (count / len(self.customers)) * 100
            print(f"  {tier}: {count:,} customers ({pct:.1f}%)")
        
        # Tier performance
        tier_performance = self.orders_full.groupby('membership_tier').agg(
            revenue=('order_total', 'sum'),
            avg_order=('order_total', 'mean'),
            orders=('order_id', 'count')
        ).sort_values('revenue', ascending=False)
        
        print(f"\n--- Tier Performance ---")
        for tier, row in tier_performance.iterrows():
            print(f"  {tier}: INR {row['revenue']:,.2f} revenue, INR {row['avg_order']:,.2f} avg order")
        
        # Top customers
        top_customers = customer_metrics.sort_values('total_spend', ascending=False).head(10)
        print(f"\n--- Top 10 Customers by Spend ---")
        for idx, (cid, row) in enumerate(top_customers.iterrows(), 1):
            print(f"  {idx}. Customer {cid}: INR {row['total_spend']:,.2f} ({row['total_orders']} orders)")
        
        return customer_metrics
    
    def rfm_segmentation(self):
        """RFM (Recency, Frequency, Monetary) segmentation"""
        print("\n" + "="*70)
        print("RFM SEGMENTATION")
        print("="*70)
        
        # Calculate RFM metrics
        current_date = self.orders['order_date'].max()
        
        rfm = self.orders.groupby('customer_id').agg(
            recency=('order_date', lambda x: (current_date - x.max()).days),
            frequency=('order_id', 'count'),
            monetary=('order_total', 'sum')
        )
        
        # Create RFM scores (1-5)
        rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1], duplicates='drop')
        rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop')
        rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5], duplicates='drop')
        
        # Combined RFM score
        rfm['rfm_score'] = rfm['recency_score'].astype(int) + rfm['frequency_score'].astype(int) + rfm['monetary_score'].astype(int)
        
        # Segment customers
        def segment_customer(row):
            if row['rfm_score'] >= 12:
                return 'Champions'
            elif row['rfm_score'] >= 10:
                return 'Loyal Customers'
            elif row['rfm_score'] >= 7:
                return 'Potential Loyalists'
            elif row['rfm_score'] >= 5:
                return 'At Risk'
            else:
                return 'Lost Customers'
        
        rfm['segment'] = rfm.apply(segment_customer, axis=1)
        
        # Segment summary
        segment_summary = rfm.groupby('segment').agg(
            customers=('frequency', 'count'),
            avg_recency=('recency', 'mean'),
            avg_frequency=('frequency', 'mean'),
            avg_monetary=('monetary', 'mean')
        ).sort_values('avg_monetary', ascending=False)
        
        print(f"\n--- RFM Segment Summary ---")
        for seg, row in segment_summary.iterrows():
            print(f"\n  {seg}:")
            print(f"    Customers: {row['customers']:,}")
            print(f"    Avg Recency: {row['avg_recency']:.0f} days")
            print(f"    Avg Frequency: {row['avg_frequency']:.1f} orders")
            print(f"    Avg Monetary: INR {row['avg_monetary']:,.2f}")
        
        return rfm, segment_summary
    
    def cohort_analysis(self):
        """Cohort analysis for retention"""
        print("\n" + "="*70)
        print("COHORT ANALYSIS")
        print("="*70)
        
        # Create cohort month
        self.orders['order_month'] = self.orders['order_date'].dt.to_period('M')
        
        # Get first order for each customer
        first_orders = self.orders.groupby('customer_id')['order_date'].min().reset_index()
        first_orders.columns = ['customer_id', 'first_order_date']
        first_orders['cohort_month'] = first_orders['first_order_date'].dt.to_period('M')
        
        # Merge with orders
        orders_with_cohort = self.orders.merge(first_orders[['customer_id', 'cohort_month']], on='customer_id')
        
        # Calculate period number (months since first order)
        orders_with_cohort['period_number'] = (
            orders_with_cohort['order_date'].dt.to_period('M') - orders_with_cohort['cohort_month']
        ).apply(lambda x: x.n)
        
        # Create cohort table
        cohort_table = orders_with_cohort.groupby(['cohort_month', 'period_number']).agg(
            customers=('customer_id', 'nunique')
        ).reset_index()
        
        # Pivot table
        cohort_pivot = cohort_table.pivot(index='cohort_month', columns='period_number', values='customers')
        
        # Calculate retention rates
        cohort_sizes = cohort_pivot[0]
        retention_table = cohort_pivot.divide(cohort_sizes, axis=0) * 100
        
        print(f"\n--- Cohort Retention Table (Top 5 cohorts) ---")
        print(retention_table.head().round(1).to_string())
        
        # Average retention by period (cohorts with no activity in a period are 0%, not skipped)
        avg_retention = retention_table.fillna(0).mean()
        print(f"\n--- Average Retention by Period ---")
        for period, rate in avg_retention.items():
            if not np.isnan(rate):
                print(f"  Period {period}: {rate:.1f}%")
        
        return cohort_table, retention_table
    
    def revenue_leakage_analysis(self):
        """Identify revenue leakage sources"""
        print("\n" + "="*70)
        print("REVENUE LEAKAGE ANALYSIS")
        print("="*70)
        
        # Payment reconciliation
        payment_reconciliation = self.orders.merge(
            self.payments[['order_id', 'amount_paid']], 
            on='order_id', how='left'
        )
        payment_reconciliation['payment_gap'] = payment_reconciliation['order_total'] - payment_reconciliation['amount_paid'].fillna(0)
        
        # Identify mismatched orders (tolerance matches SQL/Python validation: 0.01)
        mismatched_payments = payment_reconciliation[
            abs(payment_reconciliation['payment_gap']) > 0.01
        ]
        
        print(f"\n--- Payment Reconciliation ---")
        print(f"  Total Orders: {len(self.orders):,}")
        print(f"  Matched Orders: {len(self.orders) - len(mismatched_payments):,}")
        print(f"  Mismatched Orders: {len(mismatched_payments):,}")
        print(f"  Match Rate: {((len(self.orders) - len(mismatched_payments)) / len(self.orders) * 100):.2f}%")
        
        # Leakage types
        overpaid = mismatched_payments[mismatched_payments['payment_gap'] < 0]
        underpaid = mismatched_payments[mismatched_payments['payment_gap'] > 0]
        
        print(f"\n--- Leakage Breakdown ---")
        print(f"  Overpaid Orders (Revenue Loss): {len(overpaid):,}")
        print(f"  Total Overpaid Amount: INR {abs(overpaid['payment_gap'].sum()):,.2f}")
        print(f"  Underpaid Orders (Revenue Risk): {len(underpaid):,}")
        print(f"  Total Underpaid Amount: INR {underpaid['payment_gap'].sum():,.2f}")
        
        # Refund analysis
        refund_analysis = self.refunds.merge(
            self.order_items[['item_id', 'order_id', 'line_total']], 
            on='item_id', how='left'
        )
        refund_analysis['refund_ratio'] = refund_analysis['refund_amount'] / refund_analysis['line_total']
        
        excessive_refunds = refund_analysis[refund_analysis['refund_ratio'] > 0.5]
        
        print(f"\n--- Refund Analysis ---")
        print(f"  Total Refunds: {len(self.refunds):,}")
        print(f"  Total Refund Amount: INR {self.refunds['refund_amount'].sum():,.2f}")
        print(f"  Excessive Refunds (>50%): {len(excessive_refunds):,}")
        
        # Calculate total leakage: absolute payment gap (over + under) + refunds
        total_payment_discrepancy = abs(overpaid['payment_gap'].sum()) + underpaid['payment_gap'].sum()
        total_leakage = total_payment_discrepancy + self.refunds['refund_amount'].sum()
        
        print(f"\n--- Total Revenue Leakage ---")
        print(f"  Payment Discrepancies: INR {total_payment_discrepancy:,.2f}")
        print(f"  Refunds: INR {self.refunds['refund_amount'].sum():,.2f}")
        print(f"  Total Leakage: INR {total_leakage:,.2f}")
        
        return {
            'mismatched_payments': mismatched_payments,
            'overpaid': overpaid,
            'underpaid': underpaid,
            'total_leakage': total_leakage
        }
    
    def product_analysis(self):
        """Product performance analysis"""
        print("\n" + "="*70)
        print("PRODUCT ANALYSIS")
        print("="*70)
        
        # Product performance
        product_perf = self.items_full.groupby(['product_id', 'category']).agg(
            quantity_sold=('quantity', 'sum'),
            revenue=('line_total', 'sum'),
            avg_selling_price=('line_total', 'mean')
        ).sort_values('revenue', ascending=False)
        
        # Top 10 products
        print(f"\n--- Top 10 Products by Revenue ---")
        for idx, ((pid, cat), row) in enumerate(product_perf.head(10).iterrows(), 1):
            print(f"  {idx}. {cat} (ID: {pid}): INR {row['revenue']:,.2f} ({row['quantity_sold']:,} units)")
        
        # Bottom 10 products
        print(f"\n--- Bottom 10 Products by Revenue ---")
        for idx, ((pid, cat), row) in enumerate(product_perf.tail(10).iterrows(), 1):
            print(f"  {idx}. {cat} (ID: {pid}): INR {row['revenue']:,.2f} ({row['quantity_sold']:,} units)")
        
        # Category performance
        category_perf = self.items_full.groupby('category').agg(
            products=('product_id', 'nunique'),
            quantity_sold=('quantity', 'sum'),
            revenue=('line_total', 'sum')
        ).sort_values('revenue', ascending=False)
        
        print(f"\n--- Category Performance ---")
        for cat, row in category_perf.iterrows():
            print(f"  {cat}: INR {row['revenue']:,.2f} revenue, {row['products']:,} products")
        
        return product_perf, category_perf
    
    def payment_analysis(self):
        """Payment method analysis"""
        print("\n" + "="*70)
        print("PAYMENT ANALYSIS")
        print("="*70)
        
        # Payment method distribution
        payment_dist = self.payments['payment_method'].value_counts()
        print(f"\n--- Payment Method Distribution ---")
        for method, count in payment_dist.items():
            pct = (count / len(self.payments)) * 100
            print(f"  {method}: {count:,} payments ({pct:.1f}%)")
        
        # Payment status
        payment_status = self.payments['status'].value_counts()
        print(f"\n--- Payment Status ---")
        for status, count in payment_status.items():
            pct = (count / len(self.payments)) * 100
            print(f"  {status}: {count:,} payments ({pct:.1f}%)")
        
        # Payment by method
        payment_by_method = self.payments.groupby('payment_method').agg(
            total_amount=('amount_paid', 'sum'),
            avg_amount=('amount_paid', 'mean'),
            count=('payment_id', 'count')
        ).sort_values('total_amount', ascending=False)
        
        print(f"\n--- Payment Amount by Method ---")
        for method, row in payment_by_method.iterrows():
            print(f"  {method}: INR {row['total_amount']:,.2f} total, INR {row['avg_amount']:,.2f} avg")
        
        return payment_by_method
    
    def save_results(self, revenue_results, customer_metrics, rfm_results, leakage_results):
        """Save all analysis results"""
        print("\n" + "="*70)
        print("SAVING RESULTS")
        print("="*70)
        
        # Save revenue analysis
        revenue_results['revenue_by_category'].to_csv(f"{self.output_path}\\revenue_by_category.csv")
        revenue_results['revenue_by_region'].to_csv(f"{self.output_path}\\revenue_by_region.csv")
        print("  Saved revenue_by_category.csv")
        print("  Saved revenue_by_region.csv")
        
        # Save customer metrics
        customer_metrics.to_csv(f"{self.output_path}\\customer_metrics.csv")
        print("  Saved customer_metrics.csv")
        
        # Save RFM results
        rfm_results.to_csv(f"{self.output_path}\\rfm_segmentation.csv")
        print("  Saved rfm_segmentation.csv")
        
        # Save leakage analysis
        leakage_results['mismatched_payments'].to_csv(f"{self.output_path}\\payment_discrepancies.csv")
        print("  Saved payment_discrepancies.csv")
    
    def run_full_analysis(self):
        """Run complete business analysis"""
        print("\n" + "="*70)
        print("RETAILEDGE - ADVANCED BUSINESS ANALYSIS")
        print("="*70)
        
        # Run all analyses
        revenue_results = self.revenue_analysis()
        customer_metrics = self.customer_analysis()
        rfm, segment_summary = self.rfm_segmentation()
        cohort_table, retention_table = self.cohort_analysis()
        leakage_results = self.revenue_leakage_analysis()
        product_perf, category_perf = self.product_analysis()
        payment_by_method = self.payment_analysis()
        
        # Save results
        self.save_results(revenue_results, customer_metrics, rfm, leakage_results)
        
        # Summary
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE!")
        print("="*70)
        print(f"\nTotal Revenue: INR {revenue_results['total_revenue']:,.2f}")
        print(f"Net Revenue: INR {revenue_results['net_revenue']:,.2f}")
        print(f"Revenue Leakage: INR {leakage_results['total_leakage']:,.2f}")
        print(f"Leakage Rate: {(leakage_results['total_leakage'] / revenue_results['total_revenue'] * 100):.2f}%")
        print(f"\nResults saved to: {self.output_path}")
        
        return {
            'revenue': revenue_results,
            'customer_metrics': customer_metrics,
            'rfm': rfm,
            'segment_summary': segment_summary,
            'leakage': leakage_results
        }


def main():
    """Main function"""
    data_path = PROCESSED_DATA_PATH
    analysis = AdvancedBusinessAnalysis(data_path)
    results = analysis.run_full_analysis()
    return results


if __name__ == "__main__":
    main()
