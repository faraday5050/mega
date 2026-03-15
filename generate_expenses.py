import sqlite3
import random
from datetime import datetime, timedelta

def generate_expenses():
    """Generate realistic business expenses for MegaMax Enterprise"""
    conn = sqlite3.connect('megamax.db')
    cursor = conn.cursor()
    
    expense_categories = ['Rent', 'Utilities', 'Staff', 'Transport', 'Marketing', 'Maintenance', 'Tax', 'Insurance']
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 3, 31)
    current_date = start_date
    
    expenses_data = []
    
    print("🚀 Generating expenses data for MegaMax Enterprise...")
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        day_of_month = current_date.day
        
        # Rent on 1st of every month
        if day_of_month == 1:
            expenses_data.append((
                date_str, 'Rent', 'Monthly shop rent', 
                random.randint(45000, 55000), 'Transfer', '', ''
            ))
        
        # Staff salaries on 25th
        if day_of_month == 25:
            expenses_data.append((
                date_str, 'Staff', 'Staff salaries (3 employees)', 
                random.randint(120000, 150000), 'Transfer', '', ''
            ))
        
        # Utilities twice a month
        if day_of_month in [5, 20]:
            expenses_data.append((
                date_str, 'Utilities', 'Electricity bill', 
                random.randint(8000, 18000), 'Cash', '', ''
            ))
        
        # Transport costs 3 times a week
        if current_date.weekday() in [1, 3, 5]:  # Tuesday, Thursday, Saturday
            expenses_data.append((
                date_str, 'Transport', 'Goods delivery & logistics', 
                random.randint(2000, 7000), 'Cash', '', ''
            ))
        
        # Marketing twice a week
        if current_date.weekday() in [2, 5]:  # Wednesday, Saturday
            expenses_data.append((
                date_str, 'Marketing', 'Social media ads & promotions', 
                random.randint(3000, 10000), 'Transfer', '', ''
            ))
        
        # Maintenance once a week
        if current_date.weekday() == 4:  # Friday
            expenses_data.append((
                date_str, 'Maintenance', 'Shop maintenance & repairs', 
                random.randint(2000, 15000), 'Cash', '', ''
            ))
        
        # Tax once a month
        if day_of_month == 15:
            expenses_data.append((
                date_str, 'Tax', 'Monthly tax remittance', 
                random.randint(10000, 20000), 'Transfer', '', ''
            ))
        
        # Insurance quarterly
        if current_date.month in [1, 4, 7, 10] and day_of_month == 10:
            expenses_data.append((
                date_str, 'Insurance', 'Quarterly business insurance', 
                random.randint(25000, 35000), 'Transfer', '', ''
            ))
        
        current_date += timedelta(days=1)
    
    # Insert into database
    for expense in expenses_data:
        cursor.execute('''
        INSERT INTO expenses (expense_date, category, description, amount, payment_method, receipt_number, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', expense)
    
    conn.commit()
    conn.close()
    print(f"✅ MegaMax Enterprise: Generated {len(expenses_data)} expense records!")
    print(f"   💸 Total expenses: ₦{sum(e[3] for e in expenses_data):,.2f}")

if __name__ == "__main__":
    generate_expenses()