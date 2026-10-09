"""
RETAILEDGE - Feature Engineering Module
========================================
This module creates analytical features for business analysis.
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

SRC_DIR = str(Path(__file__).resolve().parent)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from project_config import PROCESSED_DATA_PATH

class FeatureEngineer:
    def __init__(self, data_path):
        self.data_path = data_path
        
    def load_clean_data(self, filename):
        """Load cleaned CSV file"""
        filepath = os.path.join(self.data_path, filename)
        return pd.read_csv(filepath)
    
    def create_order_features(self, orders, order_items, products, customers, regions):
        """Create comprehensive order-level features"""
        print("\nCreating order features...")
        
        # Merge all tables
        orders_full = order_items.merge(orders, on='order_id', how='left')
        orders_full = orders_full.merge(products[['product_id', 'category', 'subcategory', 'cost_price']], 
                                        on='product_id', how='left')
        orders_full = orders_full.merge(customers[['customer_id', 'membership_tier', 'city', 'signup_date']], 
                                        on='customer_id', how='left')
        orders_full = orders_full.merge(regions[['region_id', 'region_name', 'tier']], 
                                        on='region_id', how='left')
        
        # Convert dates
        orders_full['order_date'] = pd.to_datetime(orders_full['order_date'], errors='coerce')
        orders_full['signup_date'] = pd.to_datetime(orders_full['signup_date'], errors='coerce')
        
        # Time features
        orders_full['order_year'] = orders_full['order_date'].dt.year
        orders_full['order_month'] = orders_full['order_date'].dt.month
        orders_full['order_day'] = orders_full['order_date'].dt.day
        orders_full['order_weekday'] = orders_full['order_date'].dt.day_name()
        orders_full['order_quarter'] = orders_full['order_date'].dt.quarter
        
        # Profit calculation
        orders_full['profit'] = orders_full['line_total'] - (orders_full['cost_price'] * orders_full['quantity'])
        orders_full['profit_margin'] = (orders_full['profit'] / orders_full['line_total']) * 100
        
        # Customer tenure (days since signup)
        orders_full['customer_tenure'] = (orders_full['order_date'] - orders_full['signup_date']).dt.days
        
        print(f"  Created {len(orders_full.columns)} features")
        return orders_full
    
    def create_customer_features(self, customers, orders, order_items):
        """Create customer-level features"""
        print("\nCreating customer features...")
        
        # Merge orders with items
        orders_items = orders.merge(order_items, on='order_id', how='left')
        
        # Customer aggregations
        customer_features = orders_items.groupby('customer_id').agg(
            total_orders=('order_id', 'nunique'),
            total_items=('item_id', 'count'),
            total_revenue=('line_total', 'sum'),
            avg_order_value=('line_total', 'mean'),
            first_order_date=('order_date', 'min'),
            last_order_date=('order_date', 'max')
        ).reset_index()
        
        # Calculate customer lifetime (days)
        customer_features['first_order_date'] = pd.to_datetime(customer_features['first_order_date'])
        customer_features['last_order_date'] = pd.to_datetime(customer_features['last_order_date'])
        customer_features['customer_lifetime_days'] = (
            customer_features['last_order_date'] - customer_features['first_order_date']
        ).dt.days
        
        # Recency (days since last order, relative to the latest order in the data)
        # Using the dataset max (not today) keeps RFM reproducible over time.
        reference_date = customer_features['last_order_date'].max()
        customer_features['recency_days'] = (
            reference_date - customer_features['last_order_date']
        ).dt.days
        
        # Frequency (orders per month)
        customer_features['frequency'] = customer_features['total_orders'] / (
            customer_features['customer_lifetime_days'] / 30
        ).clip(lower=1)
        
        # Merge with customer info
        customer_features = customer_features.merge(
            customers[['customer_id', 'name', 'membership_tier', 'city']], 
            on='customer_id', how='left'
        )
        
        print(f"  Created features for {len(customer_features)} customers")
        return customer_features
    
    def create_rfm_segments(self, customer_features):
        """Create RFM segments (5-point scoring, Matches advanced_business_analysis)"""
        print("\nCreating RFM segments...")
        
        # Calculate RFM scores (1-5). Recency is inverted so 5 = most recent.
        customer_features['recency_score'] = pd.qcut(
            customer_features['recency_days'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop'
        ).astype(int)
        
        customer_features['frequency_score'] = pd.qcut(
            customer_features['total_orders'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop'
        ).astype(int)
        
        customer_features['monetary_score'] = pd.qcut(
            customer_features['total_revenue'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop'
        ).astype(int)
        
        # RFM Score
        customer_features['rfm_score'] = (
            customer_features['recency_score'] + 
            customer_features['frequency_score'] + 
            customer_features['monetary_score']
        )
        
        # Customer segments
        def assign_segment(row):
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
        
        customer_features['customer_segment'] = customer_features.apply(assign_segment, axis=1)
        
        segment_counts = customer_features['customer_segment'].value_counts()
        print(f"  Segment Distribution:")
        for segment, count in segment_counts.items():
            print(f"    {segment}: {count}")
        
        return customer_features
    
    def create_product_features(self, products, order_items, refunds):
        """Create product-level features"""
        print("\nCreating product features...")
        
        # Product aggregations from order items
        product_features = order_items.groupby('product_id').agg(
            total_quantity=('quantity', 'sum'),
            total_revenue=('line_total', 'sum'),
            avg_selling_price=('unit_price', 'mean'),
            order_count=('order_id', 'nunique')
        ).reset_index()
        
        # Merge with product info
        product_features = product_features.merge(
            products[['product_id', 'product_name', 'category', 'subcategory', 'cost_price']], 
            on='product_id', how='left'
        )
        
        # Calculate profit
        product_features['total_cost'] = product_features['cost_price'] * product_features['total_quantity']
        product_features['total_profit'] = product_features['total_revenue'] - product_features['total_cost']
        product_features['profit_margin'] = (product_features['total_profit'] / product_features['total_revenue']) * 100
        
        # Refund rate per product
        refund_counts = refunds.groupby('item_id').size().reset_index(name='refund_count')
        refund_counts = refund_counts.merge(order_items[['item_id', 'product_id']], on='item_id', how='left')
        product_features = product_features.merge(
            refund_counts.groupby('product_id')['refund_count'].sum().reset_index(),
            on='product_id', how='left'
        )
        product_features['refund_count'] = product_features['refund_count'].fillna(0)
        product_features['refund_rate'] = (product_features['refund_count'] / product_features['total_quantity']) * 100
        
        print(f"  Created features for {len(product_features)} products")
        return product_features
    
    def create_monthly_features(self, orders_full):
        """Create monthly aggregation features"""
        print("\nCreating monthly features...")
        
        # Monthly aggregations (group by calendar month, YYYY-MM, not month number
        # so that Jan-2023 and Jan-2024 are kept separate)
        orders_full = orders_full.copy()
        orders_full['order_month'] = orders_full['order_date'].dt.strftime('%Y-%m')
        monthly_features = orders_full.groupby('order_month').agg(
            total_orders=('order_id', 'nunique'),
            total_revenue=('line_total', 'sum'),
            total_profit=('profit', 'sum'),
            unique_customers=('customer_id', 'nunique')
        ).reset_index().sort_values('order_month')
        
        # Growth calculations
        monthly_features['revenue_growth'] = monthly_features['total_revenue'].pct_change() * 100
        monthly_features['profit_growth'] = monthly_features['total_profit'].pct_change() * 100
        
        # Average order value
        monthly_features['avg_order_value'] = monthly_features['total_revenue'] / monthly_features['total_orders']
        
        print(f"  Created features for {len(monthly_features)} months")
        return monthly_features
    
    def engineer_all(self):
        """Run complete feature engineering pipeline"""
        print("\n" + "="*60)
        print("FEATURE ENGINEERING PIPELINE")
        print("="*60)
        
        # Load cleaned data
        print("\nLoading cleaned data...")
        customers = self.load_clean_data('customers_clean.csv')
        products = self.load_clean_data('products_clean.csv')
        regions = self.load_clean_data('regions_clean.csv')
        orders = self.load_clean_data('orders_clean.csv')
        order_items = self.load_clean_data('order_items_clean.csv')
        payments = self.load_clean_data('payments_clean.csv')
        refunds = self.load_clean_data('refunds_clean.csv')
        
        # Create features
        orders_full = self.create_order_features(orders, order_items, products, customers, regions)
        customer_features = self.create_customer_features(customers, orders, order_items)
        customer_features = self.create_rfm_segments(customer_features)
        product_features = self.create_product_features(products, order_items, refunds)
        monthly_features = self.create_monthly_features(orders_full)
        
        # Save features
        print("\nSaving engineered features...")
        output_path = PROCESSED_DATA_PATH
        
        orders_full.to_csv(os.path.join(output_path, 'orders_full.csv'), index=False)
        customer_features.to_csv(os.path.join(output_path, 'customer_features.csv'), index=False)
        product_features.to_csv(os.path.join(output_path, 'product_features.csv'), index=False)
        monthly_features.to_csv(os.path.join(output_path, 'monthly_features.csv'), index=False)
        
        print("\n" + "="*60)
        print("FEATURE ENGINEERING COMPLETE!")
        print("="*60)
        
        return orders_full, customer_features, product_features, monthly_features


if __name__ == "__main__":
    data_path = PROCESSED_DATA_PATH
    engineer = FeatureEngineer(data_path)
    engineer.engineer_all()
