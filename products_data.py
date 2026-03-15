import sqlite3

def add_products():
    """Add all products to MegaMax database"""
    conn = sqlite3.connect('megamax.db')
    cursor = conn.cursor()
    
    products = [
        # FMCG Category
        ('Indomie Noodles (pack)', 'FMCG', 640, 760, 120, 50, 15, 'Dangote Foods'),
        ('Closeup Toothpaste 100g', 'FMCG', 350, 450, 100, 48, 10, 'PZ Cussons'),
        ('Omo Detergent 500g', 'FMCG', 1200, 1500, 300, 30, 8, 'Unilever'),
        ('Mama Cooking Oil 1L', 'FMCG', 1800, 2200, 400, 25, 5, 'Mama Gold'),
        ('Coke Soft Drink 50cl', 'FMCG', 180, 250, 70, 60, 20, 'NBC'),
        
        # Perishable Goods
        ('Fresh Bread (loaf)', 'Perishable', 500, 700, 200, 12, 5, 'Local Bakery'),
        ('Tomatoes (1kg)', 'Perishable', 800, 1200, 400, 8, 3, 'Farm Fresh'),
        ('Onions (1kg)', 'Perishable', 600, 900, 300, 15, 5, 'Farm Fresh'),
        ('Fresh Eggs (crate)', 'Perishable', 2500, 3200, 700, 10, 3, 'Poultry Farm'),
        ('Yogurt 50cl', 'Perishable', 400, 600, 200, 20, 5, 'Hollandia'),
        
        # Beverages
        ('Sachet Water (pack)', 'Beverages', 150, 250, 100, 100, 30, 'Pure Water'),
        ('Malt Drink', 'Beverages', 250, 400, 150, 40, 10, 'Guinness'),
        ('Energy Drink', 'Beverages', 400, 600, 200, 25, 8, 'Red Bull'),
        ('Tea (packet)', 'Beverages', 500, 800, 300, 15, 5, 'Lipton'),
        ('Zobo Drink 1L', 'Beverages', 300, 500, 200, 10, 3, 'Homemade'),
        
        # Electronics
        ('Phone Charger', 'Electronics', 1500, 3000, 1500, 8, 2, 'China Import'),
        ('Power Bank', 'Electronics', 8000, 12000, 4000, 5, 1, 'Samsung'),
        ('Bluetooth Speaker', 'Electronics', 7000, 10000, 3000, 4, 1, 'Oraimo'),
        ('Phone Case', 'Electronics', 800, 2000, 1200, 15, 3, 'Accessories'),
        ('Flash Drive 32GB', 'Electronics', 3500, 5500, 2000, 6, 2, 'Kingston'),
        
        # Snacks
        ('Biscuits (pack)', 'Snacks', 150, 250, 100, 45, 10, 'McVities'),
        ('Chocolate Bar', 'Snacks', 250, 400, 150, 30, 8, 'Cadbury'),
        ('Groundnut (sachet)', 'Snacks', 80, 150, 70, 60, 15, 'Local'),
        ('Cake (slice)', 'Snacks', 300, 500, 200, 12, 4, 'Local Bakery'),
        ('Chewing Gum', 'Snacks', 50, 100, 50, 80, 20, 'Wrigleys'),
        
        # Seasonal Items
        ('Rice 50kg bag', 'Seasonal', 45000, 52000, 7000, 5, 1, 'Mama Gold'),
        ('Palm Oil 25L', 'Seasonal', 35000, 40000, 5000, 3, 1, 'Local'),
        ('Soft Drinks (crate)', 'Seasonal', 1800, 2500, 700, 8, 2, 'NBC'),
        ('Party Cups (pack)', 'Seasonal', 600, 1000, 400, 10, 3, 'Event Supply'),
        ('Chin Chin 1kg', 'Seasonal', 1200, 1800, 600, 7, 2, 'Local Snacks')
    ]
    
    for product in products:
        try:
            cursor.execute('''
            INSERT INTO products 
            (product_name, category, unit_cost, selling_price, profit_margin, 
             current_stock, reorder_level, supplier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', product)
            print(f"  ✅ Added: {product[0]}")
        except Exception as e:
            print(f"  ⏭️ Skipped: {product[0]} (already exists)")
    
    conn.commit()
    conn.close()
    print(f"\n✅ MegaMax Enterprise: 30 products added successfully!")

if __name__ == "__main__":
    add_products()