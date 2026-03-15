import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import hashlib
import time

# ============================================
# PAGE CONFIG - MUST BE FIRST
# ============================================
st.set_page_config(
    page_title="MegaMax",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# SESSION STATE INIT
# ============================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.display_name = ""
    st.session_state.role = ""
    st.session_state.current_page = "Dashboard"
    st.session_state.sidebar_collapsed = False
    st.session_state.show_password = False

# ============================================
# DATABASE CONNECTION (LIGHTWEIGHT)
# ============================================
@st.cache_resource
def get_connection():
    return sqlite3.connect('megamax.db', check_same_thread=False, timeout=10)

conn = get_connection()

# ============================================
# HELPER FUNCTIONS (OPTIMIZED)
# ============================================
def load_data(query, limit=None):
    """Load data with optional limit for performance"""
    try:
        if limit:
            query += f" LIMIT {limit}"
        return pd.read_sql_query(query, conn)
    except:
        return pd.DataFrame()

def format_naira(amount):
    return f"₦{amount:,.2f}"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================
# LOGIN PAGE (LIGHTWEIGHT)
# ============================================
def login_page():
    st.markdown("""
    <div style='max-width: 400px; margin: 100px auto; padding: 30px; 
                background: #0f1a2f; border-radius: 20px; text-align: center;'>
        <h1 style='color: #60A5FA; font-size: 48px; margin-bottom: 10px;'>M⚡</h1>
        <h2 style='color: white; margin-bottom: 30px;'>MegaMax Enterprise</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.form_submit_button("Sign In", use_container_width=True):
            if username and password:
                user = load_data(f"SELECT * FROM users WHERE username='{username}'")
                if len(user) > 0 and user.iloc[0]['password_hash'] == hash_password(password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.display_name = user.iloc[0]['display_name']
                    st.session_state.role = user.iloc[0]['role']
                    st.rerun()
                else:
                    st.error("Invalid credentials")

# ============================================
# SIDEBAR (LIGHTWEIGHT)
# ============================================
def sidebar():
    with st.sidebar:
        # Logo
        if not st.session_state.sidebar_collapsed:
            st.markdown("## 📊 MegaMax")
        else:
            st.markdown("## 📊")
        
        # Toggle
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("◀" if not st.session_state.sidebar_collapsed else "▶"):
                st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
                st.rerun()
        
        st.divider()
        
        # Navigation
        pages = ["Dashboard", "Record Sale", "Sales History", "Inventory", 
                "Stock Receipts", "Expenses", "AI Predictions", "About"]
        
        for page in pages:
            if st.session_state.sidebar_collapsed:
                if st.button(page[0], key=f"nav_{page}", help=page):
                    st.session_state.current_page = page
                    st.rerun()
            else:
                if st.button(page, key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# ============================================
# DASHBOARD (LIGHTWEIGHT)
# ============================================
def dashboard():
    st.title("📊 Dashboard")
    
    # Get today's metrics (single query)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Load all needed data in one query where possible
    sales_today = load_data(f"""
        SELECT COALESCE(SUM(total_revenue),0) as revenue,
               COALESCE(SUM(total_profit),0) as profit,
               COUNT(*) as transactions
        FROM sales WHERE date(timestamp)='{today}'
    """)
    
    expenses_today = load_data(f"""
        SELECT COALESCE(SUM(amount),0) as total 
        FROM expenses WHERE expense_date='{today}'
    """)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's Revenue", 
                 format_naira(sales_today.iloc[0]['revenue']),
                 "vs yesterday")
    
    with col2:
        profit = sales_today.iloc[0]['profit']
        margin = (profit / sales_today.iloc[0]['revenue'] * 100) if sales_today.iloc[0]['revenue'] > 0 else 0
        st.metric("Today's Profit", format_naira(profit), f"{margin:.1f}% margin")
    
    with col3:
        st.metric("Transactions", sales_today.iloc[0]['transactions'])
    
    with col4:
        net = profit - expenses_today.iloc[0]['total']
        st.metric("Net Profit", format_naira(net))
    
    st.divider()
    
    # Simple chart - last 7 days (limited data)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 7-Day Trend")
        trend = load_data("""
            SELECT date(timestamp) as date, SUM(total_revenue) as revenue
            FROM sales WHERE date(timestamp) >= date('now', '-7 days')
            GROUP BY date(timestamp) ORDER BY date LIMIT 7
        """)
        if not trend.empty:
            fig = px.bar(trend, x='date', y='revenue', title="Daily Sales")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Category Sales")
        cats = load_data("""
            SELECT p.category, SUM(s.total_revenue) as revenue
            FROM sales s JOIN products p ON s.product_id=p.product_id
            WHERE s.timestamp >= date('now', '-30 days')
            GROUP BY p.category LIMIT 6
        """)
        if not cats.empty:
            fig = px.pie(cats, values='revenue', names='category', title="Sales by Category")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# RECORD SALE (LIGHTWEIGHT)
# ============================================
def record_sale():
    st.title("🛒 Record Sale")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        products = load_data("SELECT * FROM products WHERE current_stock>0")
        if not products.empty:
            product = st.selectbox("Product", products['product_name'].tolist())
            pdata = products[products['product_name']==product].iloc[0]
            
            st.info(f"Price: {format_naira(pdata['selling_price'])} | Stock: {int(pdata['current_stock'])}")
            qty = st.number_input("Quantity", 1, int(pdata['current_stock']), 1)
            
            if st.button("Record Sale", use_container_width=True):
                total = qty * pdata['selling_price']
                profit = qty * pdata['profit_margin']
                
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sales (product_id, quantity, unit_price, total_revenue, total_profit)
                    VALUES (?,?,?,?,?)
                """, (int(pdata['product_id']), qty, pdata['selling_price'], total, profit))
                
                cursor.execute("UPDATE products SET current_stock=current_stock-? WHERE product_id=?",
                             (qty, int(pdata['product_id'])))
                conn.commit()
                st.success("Sale recorded!")
                st.balloons()
                time.sleep(1)
                st.rerun()
    
    with col2:
        st.subheader("Recent Sales")
        recent = load_data("""
            SELECT strftime('%H:%M', timestamp) as time, p.product_name, s.quantity, s.total_revenue
            FROM sales s JOIN products p ON s.product_id=p.product_id
            WHERE date(timestamp)=date('now') ORDER BY timestamp DESC LIMIT 5
        """)
        if not recent.empty:
            st.dataframe(recent, width='stretch')
        else:
            st.info("No sales today")

# ============================================
# SALES HISTORY (LIGHTWEIGHT)
# ============================================
def sales_history():
    st.title("📈 Sales History")
    
    # Simple filters
    col1, col2, col3 = st.columns(3)
    with col1:
        days = st.selectbox("Period", [7, 30, 90, 365], index=1)
    with col2:
        category = st.selectbox("Category", ["All"] + load_data("SELECT DISTINCT category FROM products")['category'].tolist())
    
    # Load paginated data
    query = """
        SELECT date(s.timestamp) as date, p.product_name, p.category, 
               s.quantity, s.total_revenue, s.payment_method
        FROM sales s JOIN products p ON s.product_id=p.product_id
        WHERE s.timestamp >= date('now', '-{} days')
    """.format(days)
    
    if category != "All":
        query += f" AND p.category = '{category}'"
    
    query += " ORDER BY s.timestamp DESC LIMIT 100"
    
    sales = load_data(query)
    
    if not sales.empty:
        st.metric("Total Sales", format_naira(sales['total_revenue'].sum()))
        st.dataframe(sales, width='stretch')
        
        csv = sales.to_csv(index=False)
        st.download_button("Download CSV", csv, "sales.csv")
    else:
        st.info("No sales data")

# ============================================
# INVENTORY (LIGHTWEIGHT)
# ============================================
def inventory():
    st.title("📦 Inventory")
    
    inv = load_data("""
        SELECT product_name, category, current_stock, reorder_level,
               selling_price, (current_stock * selling_price) as value
        FROM products ORDER BY current_stock ASC
    """)
    
    if not inv.empty:
        # Alerts
        low = inv[inv['current_stock'] <= inv['reorder_level']]
        if not low.empty:
            for _, row in low.iterrows():
                st.warning(f"⚠️ {row['product_name']}: Only {row['current_stock']} left")
        
        st.dataframe(inv, width='stretch')
        
        # Quick update
        with st.expander("Update Stock"):
            product = st.selectbox("Product", inv['product_name'].tolist())
            new_stock = st.number_input("New Stock", 0, 1000, 0)
            if st.button("Update"):
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET current_stock=? WHERE product_name=?",
                             (new_stock, product))
                conn.commit()
                st.rerun()

# ============================================
# STOCK RECEIPTS (LIGHTWEIGHT)
# ============================================
def stock_receipts():
    st.title("🚚 Stock Receipts")
    
    with st.expander("Receive New Stock", expanded=True):
        products = load_data("SELECT * FROM products")
        if not products.empty:
            product = st.selectbox("Product", products['product_name'].tolist())
            pdata = products[products['product_name']==product].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                qty = st.number_input("Quantity", 1, 1000, 10)
            with col2:
                supplier = st.text_input("Supplier", pdata['supplier'])
            
            if st.button("Record Receipt"):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO inventory_receipts (date_received, product_id, quantity, total_cost, supplier)
                    VALUES (date('now'), ?, ?, ?, ?)
                """, (int(pdata['product_id']), qty, qty * pdata['unit_cost'], supplier))
                
                cursor.execute("UPDATE products SET current_stock=current_stock+? WHERE product_id=?",
                             (qty, int(pdata['product_id'])))
                conn.commit()
                st.success("Stock received!")
                st.rerun()
    
    # Recent receipts
    receipts = load_data("""
        SELECT date_received, p.product_name, ir.quantity, ir.total_cost, ir.supplier
        FROM inventory_receipts ir JOIN products p ON ir.product_id=p.product_id
        ORDER BY date_received DESC LIMIT 20
    """)
    if not receipts.empty:
        st.dataframe(receipts, width='stretch')

# ============================================
# EXPENSES (LIGHTWEIGHT)
# ============================================
def expenses():
    st.title("💰 Expenses")
    
    with st.expander("Add Expense"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            cat = st.selectbox("Category", ['Rent', 'Utilities', 'Salaries', 'Marketing', 'Other'])
        with col2:
            desc = st.text_input("Description")
            amount = st.number_input("Amount (₦)", 0, 1000000, 0)
        
        if st.button("Save Expense"):
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (expense_date, category, description, amount)
                VALUES (?, ?, ?, ?)
            """, (date.strftime('%Y-%m-%d'), cat, desc, amount))
            conn.commit()
            st.success("Expense saved!")
            st.rerun()
    
    # View expenses
    month = st.selectbox("Month", ['2026-01', '2026-02', '2026-03'])
    exp = load_data(f"SELECT * FROM expenses WHERE strftime('%Y-%m', expense_date)='{month}'")
    
    if not exp.empty:
        st.metric("Total", format_naira(exp['amount'].sum()))
        st.dataframe(exp, width='stretch')

# ============================================
# AI PREDICTIONS (LIGHTWEIGHT)
# ============================================
def ai_predictions():
    st.title("🤖 AI Predictions")
    
    preds = load_data("SELECT * FROM predictions ORDER BY prediction_date LIMIT 14")
    
    if not preds.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tomorrow", format_naira(preds.iloc[0]['predicted_sales']))
        with col2:
            st.metric("Next 7 Days", format_naira(preds.head(7)['predicted_sales'].sum()))
        with col3:
            st.metric("Confidence", f"{preds['confidence'].mean():.1f}%")
        
        fig = px.line(preds, x='prediction_date', y='predicted_sales', 
                     title="14-Day Forecast")
        st.plotly_chart(fig, use_container_width=True)
        
        # Simple recommendations
        low = load_data("SELECT product_name FROM products WHERE current_stock <= reorder_level LIMIT 3")
        if not low.empty:
            st.warning(f"Reorder: {', '.join(low['product_name'].tolist())}")
    else:
        if st.button("Generate Predictions"):
            import simple_ml
            simple_ml.SimpleML().run_all()
            st.rerun()

# ============================================
# ABOUT (LIGHTWEIGHT)
# ============================================
def about():
    st.title("ℹ️ About")
    st.markdown("""
    ## MegaMax Enterprise
    ### NextGen Knowledge Showcase 2026
    
    **Developer:** MICHAEL FARADAY  
    **Impact Pillar:** Financial Inclusion / Retail  
    
    **Features:**
    - Dashboard with real-time metrics
    - Sales recording and history
    - Inventory management
    - Expense tracking
    - AI-powered sales predictions
    
    **AI Disclosure:** Uses SimpleML for forecasting (no Prophet)
    
    © 2026 NextGen Knowledge Showcase
    Partners: 3M IT | AIRTEL AFRICA | NITDA
    """)

# ============================================
# MAIN APP
# ============================================
if not st.session_state.authenticated:
    login_page()
else:
    sidebar()
    
    # Page router
    if st.session_state.current_page == "Dashboard":
        dashboard()
    elif st.session_state.current_page == "Record Sale":
        record_sale()
    elif st.session_state.current_page == "Sales History":
        sales_history()
    elif st.session_state.current_page == "Inventory":
        inventory()
    elif st.session_state.current_page == "Stock Receipts":
        stock_receipts()
    elif st.session_state.current_page == "Expenses":
        expenses()
    elif st.session_state.current_page == "AI Predictions":
        ai_predictions()
    elif st.session_state.current_page == "About":
        about()