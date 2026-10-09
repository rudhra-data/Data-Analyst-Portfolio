"""
RETAILEDGE - Exploratory Data Analysis (EDA) Module
====================================================
This module performs comprehensive EDA on the dataset.
"""

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
from project_config import PROCESSED_DATA_PATH, FIGURES_PATH

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

class EDAAnalyzer:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        
    def load_data(self, filename):
        """Load CSV file"""
        filepath = os.path.join(self.data_path, filename)
        return pd.read_csv(filepath)
    
    def save_plot(self, filename):
        """Save plot to output folder"""
        filepath = os.path.join(self.output_path, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"  -> Saved: {filename}")
        plt.close()
    
    def univariate_analysis(self, orders_full, customer_features, product_features):
        """Perform univariate analysis"""
        print("\n--- Univariate Analysis ---")
        
        # 1. Revenue Distribution
        plt.figure(figsize=(12, 6))
        plt.hist(orders_full['line_total'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        plt.axvline(orders_full['line_total'].mean(), color='red', linestyle='--', label=f"Mean: ₹{orders_full['line_total'].mean():,.0f}")
        plt.axvline(orders_full['line_total'].median(), color='green', linestyle='--', label=f"Median: ₹{orders_full['line_total'].median():,.0f}")
        plt.title('Revenue Distribution per Line Item', fontsize=14, fontweight='bold')
        plt.xlabel('Line Total (INR)')
        plt.ylabel('Frequency')
        plt.legend()
        self.save_plot('01_revenue_distribution.png')
        
        # 2. Order Value Distribution
        order_totals = orders_full.groupby('order_id')['line_total'].sum()
        plt.figure(figsize=(12, 6))
        plt.hist(order_totals, bins=50, color='coral', edgecolor='black', alpha=0.7)
        plt.axvline(order_totals.mean(), color='red', linestyle='--', label=f"Mean: ₹{order_totals.mean():,.0f}")
        plt.title('Order Value Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Order Total (INR)')
        plt.ylabel('Frequency')
        plt.legend()
        self.save_plot('02_order_value_distribution.png')
        
        # 3. Customer Spend Distribution
        plt.figure(figsize=(12, 6))
        plt.hist(customer_features['total_revenue'], bins=30, color='mediumpurple', edgecolor='black', alpha=0.7)
        plt.title('Customer Spend Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Total Spend (INR)')
        plt.ylabel('Number of Customers')
        self.save_plot('03_customer_spend_distribution.png')
        
        # 4. Orders by Status
        plt.figure(figsize=(10, 6))
        status_counts = orders_full['status'].value_counts()
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
        status_counts.plot(kind='bar', color=colors[:len(status_counts)], edgecolor='black')
        plt.title('Orders by Status', fontsize=14, fontweight='bold')
        plt.xlabel('Status')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        self.save_plot('04_orders_by_status.png')
        
        # 5. Membership Tier Distribution
        plt.figure(figsize=(8, 8))
        tier_counts = customer_features['membership_tier'].value_counts()
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        tier_counts.plot(kind='pie', autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Customer Distribution by Membership Tier', fontsize=14, fontweight='bold')
        plt.ylabel('')
        self.save_plot('05_membership_distribution.png')
        
        # 6. Category Distribution
        plt.figure(figsize=(12, 6))
        category_counts = orders_full['category'].value_counts()
        category_counts.plot(kind='bar', color='teal', edgecolor='black')
        plt.title('Orders by Category', fontsize=14, fontweight='bold')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        self.save_plot('06_category_distribution.png')
    
    def bivariate_analysis(self, orders_full, customer_features, product_features):
        """Perform bivariate analysis"""
        print("\n--- Bivariate Analysis ---")
        
        # 7. Revenue by Category
        plt.figure(figsize=(12, 6))
        category_revenue = orders_full.groupby('category')['line_total'].sum().sort_values(ascending=False)
        bars = plt.bar(category_revenue.index, category_revenue.values, color='teal', edgecolor='black')
        plt.title('Total Revenue by Category', fontsize=14, fontweight='bold')
        plt.xlabel('Category')
        plt.ylabel('Revenue (INR)')
        plt.xticks(rotation=45)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height, f'₹{height/100000:.1f}L', ha='center', va='bottom')
        self.save_plot('07_revenue_by_category.png')
        
        # 8. Revenue by Region
        plt.figure(figsize=(12, 6))
        region_revenue = orders_full.groupby('region_name')['line_total'].sum().sort_values(ascending=False)
        bars = plt.bar(region_revenue.index, region_revenue.values, color='mediumpurple', edgecolor='black')
        plt.title('Total Revenue by Region', fontsize=14, fontweight='bold')
        plt.xlabel('Region')
        plt.ylabel('Revenue (INR)')
        plt.xticks(rotation=45)
        self.save_plot('08_revenue_by_region.png')
        
        # 9. Average Order Value by Category
        plt.figure(figsize=(12, 6))
        aov_by_category = orders_full.groupby('category').apply(
            lambda x: x.groupby('order_id')['line_total'].sum().mean()
        ).sort_values(ascending=False)
        bars = plt.bar(aov_by_category.index, aov_by_category.values, color='orange', edgecolor='black')
        plt.title('Average Order Value by Category', fontsize=14, fontweight='bold')
        plt.xlabel('Category')
        plt.ylabel('Average Order Value (INR)')
        plt.xticks(rotation=45)
        self.save_plot('09_aov_by_category.png')
        
        # 10. Refund Amount by Category
        plt.figure(figsize=(12, 6))
        refunds = self.load_data('refunds_clean.csv')
        order_items = self.load_data('order_items_clean.csv')
        products = self.load_data('products_clean.csv')
        
        refunds_merged = refunds.merge(order_items[['item_id', 'product_id']], on='item_id', how='left')
        refunds_merged = refunds_merged.merge(products[['product_id', 'category']], on='product_id', how='left')
        category_refunds = refunds_merged.groupby('category')['refund_amount'].sum().sort_values(ascending=False)
        category_refunds.plot(kind='bar', color='salmon', edgecolor='black')
        plt.title('Total Refund Amount by Category', fontsize=14, fontweight='bold')
        plt.xlabel('Category')
        plt.ylabel('Refund Amount (INR)')
        plt.xticks(rotation=45)
        self.save_plot('10_refunds_by_category.png')
        
        # 11. Customer Segment Analysis
        plt.figure(figsize=(12, 6))
        segment_revenue = customer_features.groupby('customer_segment')['total_revenue'].sum().sort_values(ascending=False)
        segment_revenue.plot(kind='bar', color='darkgreen', edgecolor='black')
        plt.title('Revenue by Customer Segment', fontsize=14, fontweight='bold')
        plt.xlabel('Customer Segment')
        plt.ylabel('Total Revenue (INR)')
        plt.xticks(rotation=45)
        self.save_plot('11_revenue_by_segment.png')
        
        # 12. Product Performance
        plt.figure(figsize=(12, 6))
        product_performance = product_features.nlargest(10, 'total_revenue')[['product_name', 'total_revenue']]
        plt.barh(product_performance['product_name'], product_performance['total_revenue'], color='navy', edgecolor='black')
        plt.title('Top 10 Products by Revenue', fontsize=14, fontweight='bold')
        plt.xlabel('Revenue (INR)')
        plt.ylabel('Product')
        self.save_plot('12_top_products.png')
    
    def multivariate_analysis(self, orders_full, customer_features, monthly_features):
        """Perform multivariate analysis"""
        print("\n--- Multivariate Analysis ---")
        
        # 13. Monthly Revenue Trend
        plt.figure(figsize=(14, 6))
        monthly_features['order_month'] = monthly_features['order_month'].astype(str)
        plt.plot(monthly_features['order_month'], monthly_features['total_revenue'], 
                 marker='o', linewidth=2, color='darkgreen', markersize=8)
        plt.fill_between(range(len(monthly_features)), monthly_features['total_revenue'], alpha=0.3, color='green')
        plt.title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Revenue (INR)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        self.save_plot('13_monthly_revenue_trend.png')
        
        # 14. Revenue by Category and Tier
        plt.figure(figsize=(14, 6))
        pivot_table = orders_full.pivot_table(values='line_total', index='category', 
                                               columns='membership_tier', aggfunc='sum')
        pivot_table.plot(kind='bar', figsize=(14, 6))
        plt.title('Revenue by Category and Membership Tier', fontsize=14, fontweight='bold')
        plt.xlabel('Category')
        plt.ylabel('Revenue (INR)')
        plt.xticks(rotation=45)
        plt.legend(title='Membership Tier', bbox_to_anchor=(1.05, 1), loc='upper left')
        self.save_plot('14_category_by_tier.png')
        
        # 15. Correlation Heatmap
        plt.figure(figsize=(10, 8))
        numeric_cols = orders_full[['quantity', 'unit_price', 'discount', 'line_total', 'profit']]
        correlation = numeric_cols.corr()
        mask = np.triu(np.ones_like(correlation, dtype=bool))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, fmt='.2f', 
                    mask=mask, square=True, linewidths=1)
        plt.title('Correlation Heatmap', fontsize=14, fontweight='bold')
        self.save_plot('15_correlation_heatmap.png')
        
        # 16. Recency vs Spend
        plt.figure(figsize=(12, 6))
        plt.scatter(customer_features['recency_days'], customer_features['total_revenue'], 
                    alpha=0.5, color='purple', s=50)
        plt.title('Recency vs Total Spend', fontsize=14, fontweight='bold')
        plt.xlabel('Recency (Days Since Last Order)')
        plt.ylabel('Total Spend (INR)')
        plt.grid(True, alpha=0.3)
        self.save_plot('16_recency_vs_spend.png')
        
        # 17. Segment Distribution by Tier
        plt.figure(figsize=(12, 6))
        segment_tier = pd.crosstab(customer_features['customer_segment'], customer_features['membership_tier'])
        segment_tier.plot(kind='bar', stacked=True, figsize=(12, 6))
        plt.title('Customer Segments by Membership Tier', fontsize=14, fontweight='bold')
        plt.xlabel('Customer Segment')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Membership Tier')
        self.save_plot('17_segment_by_tier.png')
        
        # 18. Profit Margin by Category
        plt.figure(figsize=(12, 6))
        category_margin = orders_full.groupby('category')['profit_margin'].mean().sort_values(ascending=False)
        bars = plt.bar(category_margin.index, category_margin.values, color='forestgreen', edgecolor='black')
        plt.title('Average Profit Margin by Category', fontsize=14, fontweight='bold')
        plt.xlabel('Category')
        plt.ylabel('Profit Margin (%)')
        plt.xticks(rotation=45)
        self.save_plot('18_profit_margin_by_category.png')
    
    def run_full_eda(self):
        """Run complete EDA pipeline"""
        print("\n" + "="*60)
        print("EXPLORATORY DATA ANALYSIS (EDA)")
        print("="*60)
        
        # Load data
        print("\nLoading data...")
        orders_full = self.load_data('orders_full.csv')
        customer_features = self.load_data('customer_features.csv')
        product_features = self.load_data('product_features.csv')
        monthly_features = self.load_data('monthly_features.csv')
        
        # Run analyses
        self.univariate_analysis(orders_full, customer_features, product_features)
        self.bivariate_analysis(orders_full, customer_features, product_features)
        self.multivariate_analysis(orders_full, customer_features, monthly_features)
        
        # Summary
        print("\n" + "="*60)
        print("EDA COMPLETE!")
        print("="*60)
        print(f"\nTotal plots saved: 18")
        print(f"Output folder: {self.output_path}")
        
        return orders_full, customer_features, product_features, monthly_features


if __name__ == "__main__":
    data_path = PROCESSED_DATA_PATH
    output_path = FIGURES_PATH
    
    eda = EDAAnalyzer(data_path, output_path)
    eda.run_full_eda()
