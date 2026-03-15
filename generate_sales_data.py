import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sales_data():
    """Generate 90 days of realistic sales data for MegaMax Enterprise"""
    conn = sqlite3.connect('megamax.db')
    
    # Get all products
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 3, 31)
    current_date = start_date
    
    sales_data = []
    
    # Special dates (holidays, events)
    special_dates = {
        '2026-01-01': 2.5,  # New Year (250% sales)
        '2026-01-18': 1.8,  # Black Friday
        '2026-02-14': 2.0,  # Valentine's Day
        '2026-03-17': 1.5,  # St. Patrick's Day
        '2026-03-25': 1.8,  # Month-end (salary)
        '2026-03-31': 1.6,  # End of quarter
    }
    
    print("🚀 Generating 90 days of sales data for MegaMax Enterprise...")
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
        day_of_month = current_date.day
        
        # Base multiplier for this day
        multiplier = 1.0
        
        # Weekend effect
        if day_of_week == 5:  # Saturday
            multiplier *= 1.5
        elif day_of_week == 6:  # Sunday
            multiplier *= 0.6
        
        # Month-end effect (salary days)
        if day_of_month >= 25 and day_of_month <= 28:
            multiplier *= 1.6
        
        # Month-start effect (fresh stock, salaries)
        if day_of_month <= 5:
            multiplier *= 1.3
        
        # Holiday effect
        if date_str in special_dates:
            multiplier *= special_dates[date_str]
        
        # Weather effect (random hot days increase cold drinks)
        is_hot_day = random.random() < 0.3  # 30% chance of hot day
        is_rainy_day = random.random() < 0.2  # 20% chance of rainy day
        
        if is_hot_day:
            multiplier *= 1.2
        if is_rainy_day:
            multiplier *= 0.8  # Less foot traffic when raining
        
        # Generate 8-20 transactions per day
        num_transactions = random.randint(8, 20)
        
        for _ in range(num_transactions):
            # Pick random product with bias towards fast movers
            if random.random() < 0.6:  # 60% chance of picking from FMCG or Beverages
                category_bias = random.choice(['FMCG', 'Beverages', 'Snacks'])
                product_pool = products_df[products_df['category'] == category_bias]
                if len(product_pool) > 0:
                    product = product_pool.sample(1).iloc[0]
                else:
                    product = products_df.sample(1).iloc[0]
            else:
                product = products_df.sample(1).iloc[0]
            
            # Adjust quantity based on product category and conditions
            if product['category'] == 'Perishable':
                quantity = random.randint(1, 3)
            elif product['category'] == 'Beverages' and is_hot_day:
                quantity = random.randint(2, 6)  # More drinks on hot days
            elif product['category'] == 'Seasonal' and day_of_month >= 25:
                quantity = random.randint(1, 2)  # Seasonal items at month-end
            elif product['category'] == 'Electronics':
                quantity = random.randint(1, 2)  # Electronics sell slowly
            else:
                quantity = random.randint(1, 5)
            
            # Calculate values
            unit_price = product['selling_price']
            total_revenue = quantity * unit_price
            total_profit = quantity * product['profit_margin']
            
            # Random time during business hours (7am - 9pm)
            hour = random.randint(7, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            timestamp = current_date.replace(hour=hour, minute=minute, second=second)
            
            # Payment method distribution
            payment_method = random.choices(
                ['Cash', 'Transfer', 'POS', 'Credit'],
                weights=[0.5, 0.3, 0.15, 0.05]
            )[0]
            
            sales_data.append([
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                int(product['product_id']),
                quantity,
                unit_price,
                total_revenue,
                total_profit,
                payment_method,
                ''
            ])
        
        # Progress indicator
        if current_date.day == 1:
            print(f"  📅 Generated data for {current_date.strftime('%B %Y')}")
        
        current_date += timedelta(days=1)
    
    # Insert into database
    cursor = conn.cursor()
    for sale in sales_data:
        cursor.execute('''
        INSERT INTO sales 
        (timestamp, product_id, quantity, unit_price, total_revenue, total_profit, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sale)
    
    conn.commit()
    conn.close()
    print(f"\n✅ MegaMax Enterprise: Generated {len(sales_data)} sales transactions over 90 days!")
    print(f"   📊 Total sales value: ₦{sum(s[4] for s in sales_data):,.2f}")
    print(f"   💰 Total profit: ₦{sum(s[5] for s in sales_data):,.2f}")

if __name__ == "__main__":
    generate_sales_data()