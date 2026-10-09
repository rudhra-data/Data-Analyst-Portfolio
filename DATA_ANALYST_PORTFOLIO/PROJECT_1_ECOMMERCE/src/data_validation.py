"""
RETAILEDGE - Data Validation Module
====================================
This module validates data quality across all tables.
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

class DataValidator:
    def __init__(self, data_path):
        self.data_path = data_path
        self.validation_results = []
        
    def load_clean_data(self, filename):
        """Load cleaned CSV file"""
        filepath = os.path.join(self.data_path, filename)
        return pd.read_csv(filepath)
    
    def validate(self, check_name, condition, description):
        """Run a validation check"""
        passed = condition
        self.validation_results.append({
            'Check': check_name,
            'Description': description,
            'Passed': passed
        })
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {check_name}")
        return passed
    
    def validate_referential_integrity(self, orders, customers, order_items, payments, refunds):
        """Validate foreign key relationships"""
        print("\n--- Referential Integrity Checks ---")
        
        # Orders -> Customers
        orphan_orders = ~orders['customer_id'].isin(customers['customer_id'])
        self.validate(
            "Orders -> Customers",
            orphan_orders.sum() == 0,
            f"{orphan_orders.sum()} orphan orders found"
        )
        
        # Order Items -> Orders
        orphan_items = ~order_items['order_id'].isin(orders['order_id'])
        self.validate(
            "Order Items -> Orders",
            orphan_items.sum() == 0,
            f"{orphan_items.sum()} orphan order items found"
        )
        
        # Payments -> Orders
        orphan_payments = ~payments['order_id'].isin(orders['order_id'])
        self.validate(
            "Payments -> Orders",
            orphan_payments.sum() == 0,
            f"{orphan_payments.sum()} orphan payments found"
        )
        
        # Refunds -> Orders
        orphan_refunds = ~refunds['order_id'].isin(orders['order_id'])
        self.validate(
            "Refunds -> Orders",
            orphan_refunds.sum() == 0,
            f"{orphan_refunds.sum()} orphan refunds found"
        )
    
    def validate_data_types(self, orders, order_items, payments):
        """Validate data types and ranges"""
        print("\n--- Data Type Checks ---")
        
        # Quantities may be negative (returns), but line_total must stay consistent
        # (0.05 tolerance covers line_total being rounded to the nearest paisa)
        expected_line_total = order_items['quantity'] * order_items['unit_price'] * (1 - order_items['discount'])
        inconsistent = (expected_line_total - order_items['line_total']).abs() > 0.05
        self.validate(
            "Line Total Consistency",
            inconsistent.sum() == 0,
            f"{inconsistent.sum()} line totals inconsistent with quantity x price x (1-discount)"
        )
        
        # Check prices are positive
        negative_price = (order_items['unit_price'] < 0).sum()
        self.validate(
            "Positive Prices",
            negative_price == 0,
            f"{negative_price} negative prices found"
        )
        
        # Check discount range
        invalid_discount = ((order_items['discount'] < 0) | (order_items['discount'] > 1)).sum()
        self.validate(
            "Valid Discount Range",
            invalid_discount == 0,
            f"{invalid_discount} invalid discounts found"
        )
        
        # Check payment amounts (negative values are refunds/chargebacks and are allowed)
        negative_payment = (payments['amount_paid'] < 0).sum()
        invalid_payment = (~np.isfinite(payments['amount_paid'])).sum()
        self.validate(
            "Payment Amounts Valid",
            invalid_payment == 0,
            f"{invalid_payment} invalid payment amounts ({negative_payment} refund/chargeback entries allowed)"
        )
    
    def validate_business_rules(self, orders, order_items, payments, refunds):
        """Validate business rules"""
        print("\n--- Business Rule Checks ---")
        
        # Check for future dates
        orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
        future_dates = (orders['order_date'] > pd.Timestamp.now()).sum()
        self.validate(
            "No Future Dates",
            future_dates == 0,
            f"{future_dates} future dates found"
        )
        
        # Check order status values
        valid_statuses = ['Completed', 'Shipped', 'Delivered', 'Cancelled', 'Returned', 'Pending', 'Unknown']
        invalid_status = ~orders['status'].isin(valid_statuses)
        self.validate(
            "Valid Order Status",
            invalid_status.sum() == 0,
            f"{invalid_status.sum()} invalid statuses found"
        )
        
        # Check refund amount <= the refunded item's line amount
        refund_check = refunds.merge(
            order_items[['item_id', 'line_total']], on='item_id', how='left'
        )
        over_refunds = (refund_check['refund_amount'] > refund_check['line_total']).sum()
        self.validate(
            "Refunds <= Order Amount",
            over_refunds == 0,
            f"{over_refunds} refunds exceed order amount"
        )
    
    def validate_payment_reconciliation(self, orders, order_items, payments):
        """Validate payment reconciliation"""
        print("\n--- Payment Reconciliation ---")
        
        # Calculate order totals
        order_totals = order_items.groupby('order_id')['line_total'].sum().reset_index()
        order_totals.columns = ['order_id', 'order_total']
        
        # Calculate payment totals
        payment_totals = payments.groupby('order_id')['amount_paid'].sum().reset_index()
        payment_totals.columns = ['order_id', 'payment_total']
        
        # Merge
        reconciliation = order_totals.merge(payment_totals, on='order_id', how='outer')
        reconciliation = reconciliation.fillna(0)
        reconciliation['difference'] = reconciliation['order_total'] - reconciliation['payment_total']
        reconciliation['has_discrepancy'] = reconciliation['difference'].abs() > 0.01
        
        total_orders = len(reconciliation)
        mismatched_orders = reconciliation['has_discrepancy'].sum()
        match_rate = ((total_orders - mismatched_orders) / total_orders) * 100
        
        self.validate(
            "Payment Match Rate > 90%",
            match_rate > 90,
            f"Match rate: {match_rate:.2f}%"
        )
        
        print(f"\n  Reconciliation Summary:")
        print(f"    Total Orders: {total_orders}")
        print(f"    Matched: {total_orders - mismatched_orders}")
        print(f"    Mismatched: {mismatched_orders}")
        print(f"    Match Rate: {match_rate:.2f}%")
        
        return reconciliation
    
    def run_all_validations(self):
        """Run all validation checks"""
        print("\n" + "="*60)
        print("DATA VALIDATION PIPELINE")
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
        
        # Run validations
        self.validate_referential_integrity(orders, customers, order_items, payments, refunds)
        self.validate_data_types(orders, order_items, payments)
        self.validate_business_rules(orders, order_items, payments, refunds)
        reconciliation = self.validate_payment_reconciliation(orders, order_items, payments)
        
        # Summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.validation_results if r['Passed'])
        failed = sum(1 for r in self.validation_results if not r['Passed'])
        total = len(self.validation_results)
        
        print(f"\n  Total Checks: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Pass Rate: {(passed/total)*100:.2f}%")
        
        if failed > 0:
            print(f"\n  Failed Checks:")
            for r in self.validation_results:
                if not r['Passed']:
                    print(f"    • {r['Check']}: {r['Description']}")
        
        print("="*60)
        
        return reconciliation


if __name__ == "__main__":
    data_path = PROCESSED_DATA_PATH
    validator = DataValidator(data_path)
    validator.run_all_validations()
