"""
RETAILEDGE - Power BI Data Preparation (Day 9)
=================================================
Prepare data for Power BI import with proper schema
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

SRC_DIR = str(Path(__file__).resolve().parent)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from project_config import PROCESSED_DATA_PATH, POWERBI_DATA_PATH

class PowerBIPreparation:
    """Prepare data for Power BI star schema"""
    
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        
    def load_data(self):
        """Load all cleaned data"""
        print("\nLoading data...")
        self.orders = pd.read_csv(f"{self.data_path}\\orders_clean.csv", parse_dates=['order_date'])
        self.order_items = pd.read_csv(f"{self.data_path}\\order_items_clean.csv")
        self.payments = pd.read_csv(f"{self.data_path}\\payments_clean.csv")
        self.refunds = pd.read_csv(f"{self.data_path}\\refunds_clean.csv")
        self.customers = pd.read_csv(f"{self.data_path}\\customers_clean.csv", parse_dates=['signup_date'])
        self.products = pd.read_csv(f"{self.data_path}\\products_clean.csv")
        self.regions = pd.read_csv(f"{self.data_path}\\regions_clean.csv")
        
        # Calculate order totals
        order_totals = self.order_items.groupby('order_id')['line_total'].sum().reset_index()
        order_totals.columns = ['order_id', 'total_amount']
        self.orders = self.orders.merge(order_totals, on='order_id', how='left')
        self.orders['total_amount'] = self.orders['total_amount'].fillna(0)
        
        print(f"  Loaded {len(self.orders)} orders")
        print(f"  Loaded {len(self.order_items)} order items")
        print(f"  Loaded {len(self.customers)} customers")
    
    def create_date_dimension(self):
        """Create date dimension table"""
        print("\nCreating date dimension...")
        
        # Get min and max dates
        min_date = self.orders['order_date'].min()
        max_date = self.orders['order_date'].max()
        
        # Create date range
        dates = pd.date_range(start=min_date, end=max_date, freq='D')
        
        date_dim = pd.DataFrame({
            'date_key': dates.strftime('%Y%m%d').astype(int),
            'full_date': dates,
            'year': dates.year,
            'month': dates.month,
            'month_name': dates.strftime('%B'),
            'quarter': dates.quarter,
            'week_of_year': dates.isocalendar().week.astype(int),
            'day_of_week': dates.dayofweek,
            'day_name': dates.strftime('%A'),
            'is_weekend': dates.dayofweek >= 5
        })
        
        # Save
        date_dim.to_csv(f"{self.output_path}\\dim_date.csv", index=False)
        print(f"  Created {len(date_dim)} date records")
        
        return date_dim
    
    def create_customer_dimension(self):
        """Create customer dimension table"""
        print("\nCreating customer dimension...")
        
        customer_dim = self.customers.copy()
        
        # Calculate tenure
        reference_date = pd.Timestamp('2025-01-01')
        customer_dim['tenure_days'] = (reference_date - customer_dim['signup_date']).dt.days
        
        # Calculate order counts and total spend
        customer_stats = self.orders.groupby('customer_id').agg(
            total_orders=('order_id', 'count'),
            total_spend=('total_amount', 'sum'),
            first_order=('order_date', 'min'),
            last_order=('order_date', 'max')
        ).reset_index()
        
        customer_dim = customer_dim.merge(customer_stats, on='customer_id', how='left')
        customer_dim['total_orders'] = customer_dim['total_orders'].fillna(0)
        customer_dim['total_spend'] = customer_dim['total_spend'].fillna(0)
        
        # Save
        customer_dim.to_csv(f"{self.output_path}\\dim_customer.csv", index=False)
        print(f"  Created {len(customer_dim)} customer records")
        
        return customer_dim
    
    def create_product_dimension(self):
        """Create product dimension table"""
        print("\nCreating product dimension...")
        
        product_dim = self.products.copy()
        
        # Calculate product stats
        product_stats = self.order_items.groupby('product_id').agg(
            total_sold=('quantity', 'sum'),
            total_revenue=('line_total', 'sum'),
            times_ordered=('order_id', 'nunique')
        ).reset_index()
        
        product_dim = product_dim.merge(product_stats, on='product_id', how='left')
        product_dim['total_sold'] = product_dim['total_sold'].fillna(0)
        product_dim['total_revenue'] = product_dim['total_revenue'].fillna(0)
        
        # Save
        product_dim.to_csv(f"{self.output_path}\\dim_product.csv", index=False)
        print(f"  Created {len(product_dim)} product records")
        
        return product_dim
    
    def create_region_dimension(self):
        """Create region dimension table"""
        print("\nCreating region dimension...")
        
        region_dim = self.regions.copy()
        
        # Calculate region stats
        region_stats = self.orders.groupby('region_id').agg(
            total_orders=('order_id', 'count'),
            total_revenue=('total_amount', 'sum')
        ).reset_index()
        
        region_dim = region_dim.merge(region_stats, on='region_id', how='left')
        
        # Save
        region_dim.to_csv(f"{self.output_path}\\dim_region.csv", index=False)
        print(f"  Created {len(region_dim)} region records")
        
        return region_dim
    
    def create_order_facts(self):
        """Create order fact table"""
        print("\nCreating order facts...")
        
        # Merge orders with items
        order_facts = self.order_items.merge(
            self.orders[['order_id', 'customer_id', 'order_date', 'region_id', 'status']],
            on='order_id', how='left'
        )
        
        # Add date key
        order_facts['date_key'] = order_facts['order_date'].dt.strftime('%Y%m%d').astype(int)
        
        # Calculate profit (assuming cost_price exists)
        if 'cost_price' in self.products.columns:
            order_facts = order_facts.merge(
                self.products[['product_id', 'cost_price']], 
                on='product_id', how='left'
            )
            order_facts['cost'] = order_facts['quantity'] * order_facts['cost_price']
            order_facts['profit'] = order_facts['line_total'] - order_facts['cost']
        
        # Select columns for fact table
        fact_columns = ['item_id', 'order_id', 'product_id', 'customer_id', 
                       'date_key', 'region_id', 'quantity', 'unit_price', 
                       'discount', 'line_total', 'profit']
        
        order_facts = order_facts[fact_columns]
        
        # Save
        order_facts.to_csv(f"{self.output_path}\\fact_order_items.csv", index=False)
        print(f"  Created {len(order_facts)} order item records")
        
        return order_facts
    
    def create_payment_facts(self):
        """Create payment fact table"""
        print("\nCreating payment facts...")
        
        payment_facts = self.payments.copy()
        
        # Add order details
        payment_facts = payment_facts.merge(
            self.orders[['order_id', 'order_date', 'total_amount']],
            on='order_id', how='left'
        )
        
        # Add date key
        payment_facts['date_key'] = payment_facts['order_date'].dt.strftime('%Y%m%d').astype(int)
        
        # Calculate payment gap
        payment_facts['payment_gap'] = payment_facts['total_amount'] - payment_facts['amount_paid']
        
        # Save
        payment_facts.to_csv(f"{self.output_path}\\fact_payments.csv", index=False)
        print(f"  Created {len(payment_facts)} payment records")
        
        return payment_facts
    
    def create_refund_facts(self):
        """Create refund fact table"""
        print("\nCreating refund facts...")
        
        refund_facts = self.refunds.copy()
        
        # Add order details
        refund_facts = refund_facts.merge(
            self.orders[['order_id', 'order_date', 'total_amount']],
            on='order_id', how='left'
        )
        
        # Add item details
        refund_facts = refund_facts.merge(
            self.order_items[['item_id', 'product_id', 'line_total']],
            on='item_id', how='left'
        )
        
        # Add date key
        refund_facts['date_key'] = refund_facts['order_date'].dt.strftime('%Y%m%d').astype(int)
        
        # Calculate refund ratio
        refund_facts['refund_ratio'] = refund_facts['refund_amount'] / refund_facts['line_total']
        
        # Save
        refund_facts.to_csv(f"{self.output_path}\\fact_refunds.csv", index=False)
        print(f"  Created {len(refund_facts)} refund records")
        
        return refund_facts
    
    def run_preparation(self):
        """Run complete data preparation"""
        print("\n" + "="*70)
        print("POWER BI DATA PREPARATION")
        print("="*70)
        
        # Load data
        self.load_data()
        
        # Create dimensions
        self.create_date_dimension()
        self.create_customer_dimension()
        self.create_product_dimension()
        self.create_region_dimension()
        
        # Create facts
        self.create_order_facts()
        self.create_payment_facts()
        self.create_refund_facts()
        
        print("\n" + "="*70)
        print("PREPARATION COMPLETE!")
        print("="*70)
        print(f"\nFiles saved to: {self.output_path}")
        print("\nImport these files into Power BI:")
        print("  1. dim_date.csv")
        print("  2. dim_customer.csv")
        print("  3. dim_product.csv")
        print("  4. dim_region.csv")
        print("  5. fact_order_items.csv")
        print("  6. fact_payments.csv")
        print("  7. fact_refunds.csv")


def main():
    """Main function"""
    data_path = PROCESSED_DATA_PATH
    output_path = POWERBI_DATA_PATH
    
    # Create output directory
    import os
    os.makedirs(output_path, exist_ok=True)
    
    # Run preparation
    prep = PowerBIPreparation(data_path, output_path)
    prep.run_preparation()


if __name__ == "__main__":
    main()
