import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

print("Generating data for RetailEdge project...")

# ============================================
# 1. dim_regions
# ============================================
print("Creating dim_regions...")

regions_data = {
    'region_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'region_name': ['North', 'South', 'East', 'West', 'Central', 'Northeast', 'Northwest', 'Southeast', 'Southwest', 'Metro'],
    'country': ['India', 'India', 'India', 'India', 'India', 'India', 'India', 'India', 'India', 'India'],
    'tier': ['Tier 1', 'Tier 1', 'Tier 2', 'Tier 2', 'Tier 3', 'Tier 1', 'Tier 3', 'Tier 2', 'Tier 3', 'Tier 1']
}
dim_regions = pd.DataFrame(regions_data)
print(f"  dim_regions: {len(dim_regions)} rows")

# ============================================
# 2. dim_date
# ============================================
print("Creating dim_date...")

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

dim_date_data = []
for date in dates:
    dim_date_data.append({
        'date_id': date.strftime('%Y-%m-%d'),
        'full_date': date,
        'year': date.year,
        'quarter': f"Q{(date.month - 1) // 3 + 1}",
        'month': date.month,
        'month_name': date.strftime('%B'),
        'week': date.isocalendar()[1],
        'day_name': date.strftime('%A'),
        'is_weekend': 1 if date.weekday() >= 5 else 0
    })

dim_date = pd.DataFrame(dim_date_data)
print(f"  dim_date: {len(dim_date)} rows")

# ============================================
# 3. dim_customers
# ============================================
print("Creating dim_customers...")

first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Krishna', 'Ishaan', 'Shaurya',
               'Ananya', 'Diya', 'Priya', 'Neha', 'Anjali', 'Kavya', 'Aisha', 'Riya', 'Shreya', 'Pooja',
               'Rahul', 'Rohit', 'Amit', 'Sanjay', 'Vikram', 'Suresh', 'Rajesh', 'Manoj', 'Deepak', 'Sunil',
               'Meera', 'Nisha', 'Kavita', 'Sunita', 'Rekha', 'Geeta', 'Sita', 'Radha', 'Gita', 'Lata']

last_names = ['Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Patel', 'Reddy', 'Nair', 'Iyer', 'Mishra',
              'Joshi', 'Desai', 'Pandey', 'Tiwari', 'Chauhan', 'Rao', 'Menon', 'Das', 'Banerjee', 'Mukherjee']

membership_tiers = ['Basic', 'Silver', 'Gold', 'Platinum']

customers_data = []
for i in range(1, 1001):
    signup_date = start_date + timedelta(days=random.randint(0, 700))
    
    # Intentional issues: ~5% missing email, ~3% missing city
    email = f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}@email.com" if random.random() > 0.05 else None
    city = random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow']) if random.random() > 0.03 else None
    
    customers_data.append({
        'customer_id': f'CUST{i:05d}',
        'name': f"{random.choice(first_names)} {random.choice(last_names)}",
        'email': email,
        'phone': f"+91{random.randint(7000000000, 9999999999)}",
        'city': city,
        'state': random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Telangana', 'Gujarat', 'Rajasthan', 'UP', 'Kerala']),
        'country': 'India',
        'signup_date': signup_date.strftime('%Y-%m-%d'),
        'membership_tier': random.choice(membership_tiers)
    })

dim_customers = pd.DataFrame(customers_data)
print(f"  dim_customers: {len(dim_customers)} rows")

# ============================================
# 4. dim_products
# ============================================
print("Creating dim_products...")

categories = {
    'Electronics': ['Smartphone', 'Laptop', 'Tablet', 'Headphones', 'Smartwatch', 'Camera', 'Speaker', 'Monitor', 'Keyboard', 'Mouse'],
    'Fashion': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Watch', 'Sunglasses', 'Backpack', 'Belt', 'Hat', 'Scarf'],
    'Home & Kitchen': ['Blender', 'Mixer', 'Cookware Set', 'Knife Set', 'Coffee Maker', 'Toaster', 'Vacuum Cleaner', 'Iron', 'Fan', 'Light'],
    'Beauty': ['Face Wash', 'Moisturizer', 'Sunscreen', 'Shampoo', 'Conditioner', 'Perfume', 'Lipstick', 'Foundation', 'Serum', 'Cream'],
    'Sports': ['Cricket Bat', 'Football', 'Tennis Racket', 'Yoga Mat', 'Dumbbells', 'Resistance Bands', 'Running Shoes', 'Bottle', 'Bag', 'Gloves'],
    'Books': ['Fiction', 'Non-Fiction', 'Self-Help', 'Textbook', 'Comics', 'Biography', 'Science', 'History', 'Romance', 'Thriller'],
    'Grocery': ['Rice', 'Wheat', 'Oil', 'Sugar', 'Salt', 'Spices', 'Tea', 'Coffee', 'Snacks', 'Biscuits'],
    'Health': ['Vitamins', 'Protein Powder', 'Bandages', 'Thermometer', 'BP Monitor', 'Pulse Oximeter', 'First Aid Kit', 'Masks', 'Sanitizer', 'Gloves'],
    'Toys': ['Board Game', 'Puzzle', 'Remote Car', 'Doll', 'Building Blocks', 'Lego Set', 'Outdoor Game', 'Stuffed Toy', 'Drum', 'Puzzle Book'],
    'Automotive': ['Car Cover', 'Floor Mat', 'Air Freshener', 'Phone Mount', 'Dash Cam', 'Seat Cover', 'Wiper Blades', 'Toolkit', 'Tyre Inflator', 'Jump Starter']
}

products_data = []
product_id = 1
for category, items in categories.items():
    for item in items:
        for variant in range(1, 4):  # 3 variants per item
            cost = round(random.uniform(100, 5000), 2)
            selling = round(cost * random.uniform(1.2, 2.5), 2)
            
            # Intentional issue: ~2% missing selling_price
            if random.random() < 0.02:
                selling = None
            
            products_data.append({
                'product_id': f'PROD{product_id:05d}',
                'product_name': f"{item} Variant {variant}",
                'category': category,
                'subcategory': item,
                'cost_price': cost,
                'selling_price': selling,
                'seller_id': f'SELL{random.randint(1, 50):03d}'
            })
            product_id += 1

dim_products = pd.DataFrame(products_data)
print(f"  dim_products: {len(dim_products)} rows")

# ============================================
# 5. fact_orders
# ============================================
print("Creating fact_orders...")

statuses = ['Completed', 'Shipped', 'Delivered', 'Cancelled', 'Returned', 'Pending']

orders_data = []
for i in range(1, 5001):
    order_date = start_date + timedelta(days=random.randint(0, 700))
    customer_id = f'CUST{random.randint(1, 1000):05d}'
    region_id = random.randint(1, 10)
    
    # Intentional issues: ~2% missing status, ~1% future dates
    status = random.choice(statuses) if random.random() > 0.02 else None
    
    order_date_str = order_date.strftime('%Y-%m-%d')
    if random.random() < 0.01:  # 1% future dates (invalid)
        order_date_str = (order_date + timedelta(days=365)).strftime('%Y-%m-%d')
    
    orders_data.append({
        'order_id': f'ORD{i:06d}',
        'customer_id': customer_id,
        'order_date': order_date_str,
        'region_id': region_id,
        'status': status,
        'shipping_address': f"Address {random.randint(1, 1000)}, City {random.randint(1, 20)}"
    })

fact_orders = pd.DataFrame(orders_data)

# Add ~3% duplicate orders (intentional issue)
duplicate_indices = random.sample(range(len(fact_orders)), int(len(fact_orders) * 0.03))
fact_orders = pd.concat([fact_orders, fact_orders.iloc[duplicate_indices]], ignore_index=True)

print(f"  fact_orders: {len(fact_orders)} rows (including ~3% duplicates)")

# ============================================
# 6. fact_order_items
# ============================================
print("Creating fact_order_items...")

order_items_data = []
item_id = 1

for order in fact_orders['order_id'].unique():
    num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
    
    for _ in range(num_items):
        product_id = f'PROD{random.randint(1, len(products_data)):05d}'
        quantity = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        
        # Get product price (handle None)
        prod_idx = int(product_id.replace('PROD', '')) - 1
        unit_price = dim_products.iloc[prod_idx]['selling_price']
        if pd.isna(unit_price):
            unit_price = random.uniform(200, 3000)
        
        discount = round(random.uniform(0, 0.3), 2) if random.random() > 0.7 else 0
        
        # Intentional issue: ~1% negative quantities
        if random.random() < 0.01:
            quantity = -abs(quantity)
        
        line_total = round(quantity * unit_price * (1 - discount), 2)
        
        order_items_data.append({
            'item_id': f'ITEM{item_id:07d}',
            'order_id': order,
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'discount': discount,
            'line_total': line_total
        })
        item_id += 1

fact_order_items = pd.DataFrame(order_items_data)
print(f"  fact_order_items: {len(fact_order_items)} rows")

# ============================================
# 7. fact_payments
# ============================================
print("Creating fact_payments...")

payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash on Delivery', 'Wallet']
payment_statuses = ['Success', 'Failed', 'Pending', 'Refunded']

payments_data = []
payment_id = 1

for order_id in fact_orders['order_id'].unique():
    # Get order total
    order_items = fact_order_items[fact_order_items['order_id'] == order_id]
    order_total = order_items['line_total'].sum()
    
    # Intentional issues: ~5% payment amount mismatch
    if random.random() < 0.05:
        amount_paid = round(order_total * random.uniform(0.85, 1.15), 2)  # 85-115% of order
    else:
        amount_paid = order_total
    
    payment_date_offset = random.randint(0, 3)
    payment_date = (datetime.strptime(fact_orders[fact_orders['order_id'] == order_id].iloc[0]['order_date'], '%Y-%m-%d') + timedelta(days=payment_date_offset)).strftime('%Y-%m-%d')
    
    payments_data.append({
        'payment_id': f'PAY{payment_id:07d}',
        'order_id': order_id,
        'payment_date': payment_date,
        'payment_method': random.choice(payment_methods),
        'amount_paid': amount_paid,
        'status': random.choices(payment_statuses, weights=[85, 5, 5, 5])[0]
    })
    payment_id += 1

fact_payments = pd.DataFrame(payments_data)
print(f"  fact_payments: {len(fact_payments)} rows")

# ============================================
# 8. fact_refunds
# ============================================
print("Creating fact_refunds...")

refund_reasons = ['Damaged', 'Wrong Item', 'Quality Issue', 'Not as Described', 'Changed Mind', 'Late Delivery']

refunds_data = []
refund_id = 1

# ~10% of orders have refunds
orders_with_refunds = random.sample(list(fact_orders['order_id'].unique()), int(len(fact_orders['order_id'].unique()) * 0.10))

for order_id in orders_with_refunds:
    order_items = fact_order_items[fact_order_items['order_id'] == order_id]
    
    if len(order_items) > 0:
        refund_item = order_items.sample(1).iloc[0]
        
        # Intentional issue: ~3% refund amount > order item amount
        if random.random() < 0.03:
            refund_amount = round(refund_item['line_total'] * random.uniform(1.1, 1.3), 2)
        else:
            refund_amount = refund_item['line_total']
        
        refund_date_offset = random.randint(5, 30)
        order_date = fact_orders[fact_orders['order_id'] == order_id].iloc[0]['order_date']
        refund_date = (datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=refund_date_offset)).strftime('%Y-%m-%d')
        
        refunds_data.append({
            'refund_id': f'REF{refund_id:06d}',
            'order_id': order_id,
            'item_id': refund_item['item_id'],
            'refund_date': refund_date,
            'refund_amount': refund_amount,
            'reason': random.choice(refund_reasons),
            'status': random.choice(['Approved', 'Pending', 'Rejected'])
        })
        refund_id += 1

fact_refunds = pd.DataFrame(refunds_data)
print(f"  fact_refunds: {len(fact_refunds)} rows")

# ============================================
# SAVE ALL FILES
# ============================================
print("\nSaving files to data/raw/...")

dim_regions.to_csv('data/raw/dim_regions.csv', index=False)
dim_date.to_csv('data/raw/dim_date.csv', index=False)
dim_customers.to_csv('data/raw/dim_customers.csv', index=False)
dim_products.to_csv('data/raw/dim_products.csv', index=False)
fact_orders.to_csv('data/raw/fact_orders.csv', index=False)
fact_order_items.to_csv('data/raw/fact_order_items.csv', index=False)
fact_payments.to_csv('data/raw/fact_payments.csv', index=False)
fact_refunds.to_csv('data/raw/fact_refunds.csv', index=False)

print("\nAll files saved successfully!")
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"dim_regions:      {len(dim_regions):>6} rows")
print(f"dim_date:         {len(dim_date):>6} rows")
print(f"dim_customers:    {len(dim_customers):>6} rows")
print(f"dim_products:     {len(dim_products):>6} rows")
print(f"fact_orders:      {len(fact_orders):>6} rows")
print(f"fact_order_items: {len(fact_order_items):>6} rows")
print(f"fact_payments:    {len(fact_payments):>6} rows")
print(f"fact_refunds:     {len(fact_refunds):>6} rows")
print("="*50)
print("\nData generation complete!")
