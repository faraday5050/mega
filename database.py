import sqlite3
import os
import hashlib

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    """Create all tables for MegaMax Enterprise"""
    
    # Remove existing database if you want fresh start
    if os.path.exists('megamax.db'):
        os.remove('megamax.db')
        print("🗑️ Removed existing database")
    
    conn = sqlite3.connect('megamax.db')
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        unit_cost REAL NOT NULL,
        selling_price REAL NOT NULL,
        profit_margin REAL NOT NULL,
        current_stock INTEGER DEFAULT 0,
        reorder_level INTEGER DEFAULT 10,
        supplier TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ Created products table")
    
    # Create sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_revenue REAL NOT NULL,
        total_profit REAL NOT NULL,
        payment_method TEXT DEFAULT 'Cash',
        notes TEXT,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    print("✅ Created sales table")
    
    # Create inventory_receipts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_receipts (
        receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_received DATE NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_cost REAL NOT NULL,
        supplier TEXT,
        notes TEXT,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    print("✅ Created inventory_receipts table")
    
    # Create expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date DATE NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'Cash',
        receipt_number TEXT,
        notes TEXT
    )
    ''')
    print("✅ Created expenses table")
    
    # Create predictions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_date DATE NOT NULL,
        predicted_sales REAL NOT NULL,
        confidence REAL NOT NULL,
        model_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ Created predictions table")
    
    # Create users table for login system
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        display_name TEXT NOT NULL,
        role TEXT DEFAULT 'staff',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ Created users table")
    
    # Insert default users with CORRECT password hashes
    users = [
        ('admin', hash_password('admin'), 'Administrator', 'admin'),
        ('owner', hash_password('megamax2026'), 'Business Owner', 'owner'),
        ('manager', hash_password('manager123'), 'Store Manager', 'manager'),
        ('staff', hash_password('staff123'), 'Staff Member', 'staff')
    ]
    
    for user in users:
        try:
            cursor.execute('''
            INSERT INTO users (username, password_hash, display_name, role)
            VALUES (?, ?, ?, ?)
            ''', user)
            print(f"  ✅ Added user: {user[0]}")
        except Exception as e:
            print(f"  ⏭️ User {user[0]} already exists: {e}")
    
    # Commit all changes
    conn.commit()
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\n📊 Tables in database:")
    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
        print(f"   - {table[0]}: {count} records")
    
    conn.close()
    print("\n" + "="*50)
    print("✅ MegaMax Enterprise database created successfully!")
    print("="*50)
    print("\n🔐 LOGIN CREDENTIALS:")
    print("   ─────────────────")
    print("   Admin:   username: admin   | password: admin")
    print("   Owner:   username: owner   | password: megamax2026")
    print("   Manager: username: manager | password: manager123")
    print("   Staff:   username: staff   | password: staff123")
    print("\n📁 Database file: megamax.db")
    print("="*50)

if __name__ == "__main__":
    create_database()