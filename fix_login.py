import sqlite3
import hashlib
import os

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def fix_database():
    print("="*50)
    print("🔧 FIXING MEGAMAX DATABASE LOGIN")
    print("="*50)
    
    # Check if database exists
    if not os.path.exists('megamax.db'):
        print("❌ megamax.db not found!")
        return
    
    # Connect to database
    conn = sqlite3.connect('megamax.db')
    cursor = conn.cursor()
    
    # Check current tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\n📊 Current tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Drop and recreate users table to ensure correct structure
    print("\n🔄 Recreating users table...")
    cursor.execute("DROP TABLE IF EXISTS users")
    
    cursor.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        display_name TEXT NOT NULL,
        role TEXT DEFAULT 'staff',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ Users table created")
    
    # Add users with correct passwords
    users = [
        ('admin', hash_password('admin'), 'Administrator', 'admin'),
        ('owner', hash_password('megamax2026'), 'Business Owner', 'owner'),
        ('manager', hash_password('manager123'), 'Store Manager', 'manager'),
        ('staff', hash_password('staff123'), 'Staff Member', 'staff')
    ]
    
    print("\n👤 Adding users:")
    for username, pw_hash, display, role in users:
        try:
            cursor.execute('''
            INSERT INTO users (username, password_hash, display_name, role)
            VALUES (?, ?, ?, ?)
            ''', (username, pw_hash, display, role))
            print(f"   ✅ {username} added")
        except Exception as e:
            print(f"   ❌ {username}: {e}")
    
    # Verify users were added
    cursor.execute("SELECT username, password_hash, display_name, role FROM users")
    saved_users = cursor.fetchall()
    
    print("\n📋 Users in database now:")
    for user in saved_users:
        print(f"   - {user[0]}: {user[2]} ({user[3]})")
        print(f"     Hash: {user[1][:20]}...")
    
    # Test admin login
    test_user = 'admin'
    test_pass = 'admin'
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (test_user,))
    result = cursor.fetchone()
    
    if result:
        stored = result[0]
        calculated = hash_password(test_pass)
        print(f"\n🔐 Testing login: {test_user}/{test_pass}")
        print(f"   Stored hash:    {stored}")
        print(f"   Calculated hash: {calculated}")
        print(f"   Match: {stored == calculated}")
        
        if stored == calculated:
            print("✅ LOGIN WILL WORK!")
        else:
            print("❌ LOGIN WILL FAIL - hashes don't match")
    else:
        print(f"❌ User {test_user} not found")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ DATABASE FIXED!")
    print("="*50)
    print("\nTry logging in with:")
    print("   admin / admin")
    print("   owner / megamax2026")
    print("   manager / manager123")
    print("   staff / staff123")

if __name__ == "__main__":
    fix_database()