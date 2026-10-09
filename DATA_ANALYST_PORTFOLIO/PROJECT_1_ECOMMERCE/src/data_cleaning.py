"""
RETAILEDGE - Data Cleaning Module
==================================
This module handles all data cleaning operations.
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

SRC_DIR = str(Path(__file__).resolve().parent)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from project_config import RAW_DATA_PATH, PROCESSED_DATA_PATH

class DataCleaner:
    def __init__(self, data_path):
        self.data_path = data_path
        self.cleaning_log = []
        
    def load_data(self, filename):
        """Load CSV file"""
        filepath = os.path.join(self.data_path, filename)
        df = pd.read_csv(filepath)
        self.log(f"Loaded {filename}: {len(df)} rows, {df.shape[1]} columns")
        return df
    
    def log(self, message):
        """Log cleaning operations"""
        self.cleaning_log.append(message)
        print(f"  -> {message}")
    
    def check_missing(self, df, name):
        """Check and report missing values"""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        missing_report = pd.DataFrame({
            'Column': missing.index,
            'Missing Count': missing.values,
            'Missing %': missing_pct.values
        })
        missing_report = missing_report[missing_report['Missing Count'] > 0]
        
        if len(missing_report) > 0:
            self.log(f"{name} has {len(missing_report)} columns with missing values")
            return missing_report
        else:
            self.log(f"{name} has no missing values")
            return None
    
    def check_duplicates(self, df, name, key_columns=None):
        """Check and report duplicates"""
        if key_columns:
            dup_count = df.duplicated(subset=key_columns).sum()
        else:
            dup_count = df.duplicated().sum()
        
        if dup_count > 0:
            self.log(f"{name} has {dup_count} duplicate records")
            return dup_count
        else:
            self.log(f"{name} has no duplicates")
            return 0
    
    def remove_duplicates(self, df, name, key_columns):
        """Remove duplicate records"""
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=key_columns, keep='first')
        removed = initial_count - len(df_clean)
        self.log(f"Removed {removed} duplicates from {name}")
        return df_clean
    
    def fix_missing_customers(self, df):
        """Fix missing values in customers table"""
        df['email'] = df['email'].fillna('unknown@email.com')
        df['city'] = df['city'].fillna('Unknown')
        self.log("Fixed missing emails and cities in customers")
        return df
    
    def fix_missing_products(self, df):
        """Fix missing values in products table"""
        df['selling_price'] = pd.to_numeric(df['selling_price'], errors='coerce')
        df['selling_price'] = df['selling_price'].fillna(df['cost_price'] * 1.5)
        self.log("Fixed missing selling prices in products")
        return df
    
    def fix_missing_orders(self, df):
        """Fix missing values in orders table"""
        df['status'] = df['status'].fillna('Unknown')
        self.log("Fixed missing status in orders")
        return df
    
    def fix_negative_quantities(self, df):
        """Handle return line items (negative quantity).

        A negative quantity represents a product return. We keep it signed so
        that line_total stays consistent with quantity * unit_price * (1 - discount),
        and only repair any rows where line_total disagrees with that formula.
        """
        return_mask = df['quantity'] < 0
        expected = df['quantity'] * df['unit_price'] * (1 - df['discount'])
        inconsistent = ((expected - df['line_total']).abs() > 0.01) & return_mask
        repaired = int(inconsistent.sum())
        df.loc[inconsistent, 'line_total'] = expected[inconsistent].round(2)
        self.log(f"Identified {int(return_mask.sum())} return line items (negative quantity); repaired {repaired} line totals")
        return df
    
    def validate_dates(self, df):
        """Validate and fix dates"""
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        future_dates = (df['order_date'] > pd.Timestamp.now()).sum()
        self.log(f"Found {future_dates} future dates in orders")
        return df
    
    def clean_all(self):
        """Run complete cleaning pipeline"""
        print("\n" + "="*60)
        print("DATA CLEANING PIPELINE")
        print("="*60)
        
        # Load data
        print("\nLoading data...")
        customers = self.load_data('dim_customers.csv')
        products = self.load_data('dim_products.csv')
        regions = self.load_data('dim_regions.csv')
        orders = self.load_data('fact_orders.csv')
        order_items = self.load_data('fact_order_items.csv')
        payments = self.load_data('fact_payments.csv')
        refunds = self.load_data('fact_refunds.csv')
        
        # Check missing values
        print("\nChecking missing values...")
        self.check_missing(customers, 'customers')
        self.check_missing(products, 'products')
        self.check_missing(orders, 'orders')
        self.check_missing(order_items, 'order_items')
        
        # Check duplicates
        print("\nChecking duplicates...")
        self.check_duplicates(orders, 'orders', ['order_id'])
        self.check_duplicates(order_items, 'order_items', ['item_id'])
        self.check_duplicates(payments, 'payments', ['payment_id'])
        self.check_duplicates(refunds, 'refunds', ['refund_id'])
        
        # Fix missing values
        print("\nFixing missing values...")
        customers = self.fix_missing_customers(customers)
        products = self.fix_missing_products(products)
        orders = self.fix_missing_orders(orders)
        
        # Remove duplicates
        print("\nRemoving duplicates...")
        orders = self.remove_duplicates(orders, 'orders', ['order_id'])
        order_items = self.remove_duplicates(order_items, 'order_items', ['item_id'])
        payments = self.remove_duplicates(payments, 'payments', ['payment_id'])
        refunds = self.remove_duplicates(refunds, 'refunds', ['refund_id'])
        
        # Fix invalid values
        print("\nFixing invalid values...")
        order_items = self.fix_negative_quantities(order_items)
        orders = self.validate_dates(orders)
        
        # Save cleaned data
        print("\nSaving cleaned data...")
        cleaned_path = PROCESSED_DATA_PATH
        os.makedirs(cleaned_path, exist_ok=True)
        
        customers.to_csv(os.path.join(cleaned_path, 'customers_clean.csv'), index=False)
        products.to_csv(os.path.join(cleaned_path, 'products_clean.csv'), index=False)
        regions.to_csv(os.path.join(cleaned_path, 'regions_clean.csv'), index=False)
        orders.to_csv(os.path.join(cleaned_path, 'orders_clean.csv'), index=False)
        order_items.to_csv(os.path.join(cleaned_path, 'order_items_clean.csv'), index=False)
        payments.to_csv(os.path.join(cleaned_path, 'payments_clean.csv'), index=False)
        refunds.to_csv(os.path.join(cleaned_path, 'refunds_clean.csv'), index=False)
        
        self.log("All cleaned data saved to processed folder")
        
        # Print summary
        print("\n" + "="*60)
        print("CLEANING SUMMARY")
        print("="*60)
        for log in self.cleaning_log:
            print(f"  • {log}")
        print("="*60)
        
        return customers, products, regions, orders, order_items, payments, refunds


if __name__ == "__main__":
    data_path = RAW_DATA_PATH
    cleaner = DataCleaner(data_path)
    cleaner.clean_all()
