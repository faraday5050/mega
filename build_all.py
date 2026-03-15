"""
MEGAMAX ENTERPRISE - MASTER BUILD SCRIPT
Run this script to build the entire application from scratch
"""

import os
import time
import subprocess
import sys

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {text}")
    print("="*60)

def print_step(step, text):
    """Print step information"""
    print(f"\n📌 STEP {step}: {text}")
    print("-"*40)

def run_script(script_name):
    """Run a Python script and check for errors"""
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("⚠️ Warnings/Errors:")
        print(result.stderr)
    return result.returncode == 0

def main():
    """Build the complete MegaMax Enterprise application"""
    
    print_header("MEGAMAX ENTERPRISE - COMPLETE BUILD SYSTEM")
    print("Building your professional business intelligence application...\n")
    
    # Step 1: Create database
    print_step(1, "Creating Database Schema")
    if not run_script('database.py'):
        print("❌ Failed to create database")
        return
    time.sleep(1)
    
    # Step 2: Add products
    print_step(2, "Adding Product Catalog")
    if not run_script('products_data.py'):
        print("❌ Failed to add products")
        return
    time.sleep(1)
    
    # Step 3: Generate sales data
    print_step(3, "Generating 90 Days of Sales History")
    if not run_script('generate_sales_data.py'):
        print("❌ Failed to generate sales data")
        return
    time.sleep(1)
    
    # Step 4: Generate expenses
    print_step(4, "Generating Business Expenses")
    if not run_script('generate_expenses.py'):
        print("❌ Failed to generate expenses")
        return
    time.sleep(1)
    
    # Step 5: Train ML models
    print_step(5, "Training Machine Learning Models")
    if not run_script('ml_model.py'):
        print("❌ Failed to train ML models")
        return
    time.sleep(1)
    
    # Final summary
    print_header("BUILD COMPLETE! 🎉")
    print("""
    ✅ MegaMax Enterprise is ready!
    
    📁 Project Structure:
    ├── megamax.db              - Main database
    ├── app.py                  - Main application
    ├── database.py             - Database schema
    ├── products_data.py        - Product catalog
    ├── generate_sales_data.py  - Sales data generator
    ├── generate_expenses.py    - Expenses generator
    ├── ml_model.py             - Machine learning models
    ├── requirements.txt        - Python dependencies
    └── saved_models/           - Trained ML models
    
    🚀 To launch the application:
    ----------------------------
    streamlit run app.py
    
    🔐 Login Credentials:
    --------------------
    Admin:   admin / admin
    Owner:   owner / megamax2026
    Manager: manager / manager123
    Staff:   staff / staff123
    
    Good luck with the competition! 🏆
    """)

if __name__ == "__main__":
    main()