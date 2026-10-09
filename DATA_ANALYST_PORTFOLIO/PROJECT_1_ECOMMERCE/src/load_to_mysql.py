import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

SRC_DIR = str(Path(__file__).resolve().parent)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
from project_config import PROJECT_ROOT, RAW_DATA_PATH

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

print("Loading data into MySQL database...")

# ============================================
# DATABASE CONNECTION
# ============================================
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE', 'retailedge_db')
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# ============================================
# LOAD CSV FILES (FULL PATHS)
# ============================================
print("Loading CSV files...")

base_path = RAW_DATA_PATH

customers = pd.read_csv(os.path.join(base_path, 'dim_customers.csv'))
products = pd.read_csv(os.path.join(base_path, 'dim_products.csv'))
regions = pd.read_csv(os.path.join(base_path, 'dim_regions.csv'))
date = pd.read_csv(os.path.join(base_path, 'dim_date.csv'))
orders = pd.read_csv(os.path.join(base_path, 'fact_orders.csv'))
order_items = pd.read_csv(os.path.join(base_path, 'fact_order_items.csv'))
payments = pd.read_csv(os.path.join(base_path, 'fact_payments.csv'))
refunds = pd.read_csv(os.path.join(base_path, 'fact_refunds.csv'))

# Handle NaN values - convert to appropriate defaults
customers = customers.fillna('')
products['selling_price'] = pd.to_numeric(products['selling_price'], errors='coerce').fillna(0)
products = products.fillna('')
orders = orders.fillna('')
order_items = order_items.fillna('')
payments = payments.fillna('')
refunds = refunds.fillna('')

# Remove duplicates (keep first occurrence)
print("Removing duplicates...")
orders = orders.drop_duplicates(subset=['order_id'], keep='first')
order_items = order_items.drop_duplicates(subset=['item_id'], keep='first')
payments = payments.drop_duplicates(subset=['payment_id'], keep='first')
refunds = refunds.drop_duplicates(subset=['refund_id'], keep='first')
print(f"After dedup: orders={len(orders)}, order_items={len(order_items)}, payments={len(payments)}, refunds={len(refunds)}")

print("All CSV files loaded!")

# ============================================
# INSERT DATA FUNCTION
# ============================================
def insert_data(connection, table_name, df, columns):
    cursor = connection.cursor()
    
    # Create placeholder string
    placeholders = ', '.join(['%s'] * len(columns))
    cols = ', '.join(columns)
    
    # Create insert query
    query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
    
    # Convert dataframe to list of tuples
    data = [tuple(row) for row in df[columns].values]
    
    # Insert data
    cursor.executemany(query, data)
    connection.commit()
    
    print(f"Inserted {cursor.rowcount} rows into {table_name}")
    cursor.close()

# ============================================
# INSERT DATA INTO TABLES
# ============================================
connection = create_connection()

if connection:
    try:
        # Clear existing data first (order matters due to foreign keys)
        print("\nClearing existing data...")
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE fact_refunds")
        cursor.execute("TRUNCATE TABLE fact_payments")
        cursor.execute("TRUNCATE TABLE fact_order_items")
        cursor.execute("TRUNCATE TABLE fact_orders")
        cursor.execute("TRUNCATE TABLE dim_date")
        cursor.execute("TRUNCATE TABLE dim_products")
        cursor.execute("TRUNCATE TABLE dim_regions")
        cursor.execute("TRUNCATE TABLE dim_customers")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        connection.commit()
        cursor.close()
        print("All tables cleared!")
        
        # Insert dim_customers
        print("\nInserting dim_customers...")
        insert_data(connection, 'dim_customers', customers, 
                   ['customer_id', 'name', 'email', 'phone', 'city', 'state', 'country', 'signup_date', 'membership_tier'])
        
        # Insert dim_products
        print("Inserting dim_products...")
        insert_data(connection, 'dim_products', products,
                   ['product_id', 'product_name', 'category', 'subcategory', 'cost_price', 'selling_price', 'seller_id'])
        
        # Insert dim_regions
        print("Inserting dim_regions...")
        insert_data(connection, 'dim_regions', regions,
                   ['region_id', 'region_name', 'country', 'tier'])
        
        # Insert dim_date
        print("Inserting dim_date...")
        insert_data(connection, 'dim_date', date,
                   ['date_id', 'full_date', 'year', 'quarter', 'month', 'month_name', 'week', 'day_name', 'is_weekend'])
        
        # Insert fact_orders
        print("Inserting fact_orders...")
        insert_data(connection, 'fact_orders', orders,
                   ['order_id', 'customer_id', 'order_date', 'region_id', 'status', 'shipping_address'])
        
        # Insert fact_order_items
        print("Inserting fact_order_items...")
        insert_data(connection, 'fact_order_items', order_items,
                   ['item_id', 'order_id', 'product_id', 'quantity', 'unit_price', 'discount', 'line_total'])
        
        # Insert fact_payments
        print("Inserting fact_payments...")
        insert_data(connection, 'fact_payments', payments,
                   ['payment_id', 'order_id', 'payment_date', 'payment_method', 'amount_paid', 'status'])
        
        # Insert fact_refunds
        print("Inserting fact_refunds...")
        insert_data(connection, 'fact_refunds', refunds,
                   ['refund_id', 'order_id', 'item_id', 'refund_date', 'refund_amount', 'reason', 'status'])
        
        print("\n" + "="*50)
        print("ALL DATA LOADED SUCCESSFULLY!")
        print("="*50)
        
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        connection.close()
        print("Connection closed.")
