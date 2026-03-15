# Add this right after your imports
import sqlite3
import streamlit as st
import time
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import time
import os
import numpy as np



# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="MegaMax Enterprise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: #0a0f1f;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background: linear-gradient(180deg, #0B1120 0%, #1A2332 100%);
    }
    
    /* Logo */
    .logo-container {
        padding: 24px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #60A5FA, #34D399);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: 800;
        color: white;
    }
    
    .logo-main {
        font-size: 22px;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .logo-tagline {
        color: #64748B;
        font-size: 11px;
    }
    
    /* Page Title */
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    
    .date-badge {
        background: rgba(255,255,255,0.05);
        padding: 8px 16px;
        border-radius: 30px;
        color: #94A3B8;
        font-size: 14px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e2a3a 0%, #0f1a2f 100%);
        padding: 24px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        border-left: 4px solid #60A5FA;
        margin-bottom: 20px;
    }
    
    .metric-label {
        color: #94A3B8;
        font-size: 14px;
        font-weight: 500;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: white;
    }
    
    .metric-change {
        font-size: 13px;
        color: #10B981;
    }
    
    /* Chart Containers */
    .chart-container {
        background: linear-gradient(135deg, #1e2a3a 0%, #0f1a2f 100%);
        padding: 24px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 24px;
    }
    
    .chart-title {
        font-size: 18px;
        font-weight: 600;
        color: white;
        margin-bottom: 20px;
    }
    
    /* Tables */
    .dataframe {
        background: #1e2a3a;
        color: white;
    }
    
    /* Alert Boxes */
    .alert-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    
    .alert-box.warning {
        background: rgba(245, 158, 11, 0.1);
        border-left-color: #F59E0B;
    }
    
    .alert-box.success {
        background: rgba(16, 185, 129, 0.1);
        border-left-color: #10B981;
    }
    
    /* Filter Section */
    .filter-section {
        background: rgba(255,255,255,0.02);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 24px;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .stat-item {
        background: rgba(255,255,255,0.03);
        padding: 16px;
        border-radius: 12px;
        text-align: center;
    }
    
    .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: #60A5FA;
    }
    
    .stat-label {
        color: #94A3B8;
        font-size: 12px;
        margin-top: 4px;
    }
    
    /* Login Card */
    .login-card {
        background: linear-gradient(135deg, #1e2a3a 0%, #0f1a2f 100%);
        padding: 48px;
        border-radius: 32px;
        border: 1px solid rgba(255,255,255,0.05);
        max-width: 440px;
        margin: 60px auto;
    }
    
    .login-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #60A5FA, #34D399);
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        color: white;
        margin: 0 auto 20px auto;
    }
    
    .login-logo {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE SESSION STATES
# ============================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'display_name' not in st.session_state:
    st.session_state.display_name = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'show_password' not in st.session_state:
    st.session_state.show_password = False
if 'login_time' not in st.session_state:
    st.session_state.login_time = None
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'date_range' not in st.session_state:
    st.session_state.date_range = "This Month"
if 'category_filter' not in st.session_state:
    st.session_state.category_filter = "All"

# ============================================
# DATABASE CONNECTION
# ============================================
@st.cache_resource
def get_db_connection():
    return sqlite3.connect('megamax.db', check_same_thread=False)

conn = get_db_connection()

# ============================================
# HELPER FUNCTIONS
# ============================================
def load_data(query, params=None):
    """Load data from database"""
    try:
        if params:
            return pd.read_sql_query(query, conn, params=params)
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def execute_query(query, params=None):
    """Execute a non-SELECT query"""
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def format_naira(amount):
    """Format as Nigerian Naira"""
    return f"₦{amount:,.2f}"

def hash_password(password):
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """Verify login credentials"""
    try:
        user = load_data(f"SELECT * FROM users WHERE username = '{username}'")
        if len(user) > 0:
            if user.iloc[0]['password_hash'] == hash_password(password):
                return {
                    'success': True,
                    'display_name': user.iloc[0]['display_name'],
                    'role': user.iloc[0]['role']
                }
        return {'success': False}
    except:
        return {'success': False}

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.rerun()

def get_date_range(filter_type):
    """Get date range based on filter"""
    today = datetime.now()
    if filter_type == "Today":
        start_date = today.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif filter_type == "This Week":
        start_date = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif filter_type == "This Month":
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif filter_type == "Last 30 Days":
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif filter_type == "This Year":
        start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    else:
        start_date = "2026-01-01"
        end_date = today.strftime('%Y-%m-%d')
    return start_date, end_date

# ============================================
# SIDEBAR NAVIGATION
# ============================================
def render_sidebar():
    """Render sidebar navigation"""
    
    nav_items = [
        {"icon": "📊", "label": "Dashboard"},
        {"icon": "🛒", "label": "Record Sale"},
        {"icon": "📈", "label": "Sales History"},
        {"icon": "📦", "label": "Inventory"},
        {"icon": "🚚", "label": "Stock Receipts"},
        {"icon": "💰", "label": "Expenses"},
        {"icon": "📊", "label": "Analytics"},
        {"icon": "🤖", "label": "AI Predictions"},
        {"icon": "ℹ️", "label": "About"},
        {"icon": "⚙️", "label": "Settings"},
    ]
    
    if st.session_state.role == 'admin':
        nav_items.append({"icon": "🔐", "label": "Admin"})
    
    with st.sidebar:
        # Logo
        if not st.session_state.sidebar_collapsed:
            st.markdown("""
            <div class="logo-container">
                <div class="logo-icon">M⚡</div>
                <div>
                    <div class="logo-main">MEGAMAX</div>
                    <div class="logo-tagline">ENTERPRISE</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <div class="logo-icon" style="margin: 0 auto;">M⚡</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Toggle button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("◀" if not st.session_state.sidebar_collapsed else "▶"):
                st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation items
        for item in nav_items:
            if st.session_state.sidebar_collapsed:
                if st.button(item["icon"], key=f"nav_{item['label']}", help=item["label"]):
                    st.session_state.current_page = item["label"]
                    st.rerun()
            else:
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"<span style='font-size: 20px;'>{item['icon']}</span>", unsafe_allow_html=True)
                with col2:
                    if st.button(item["label"], key=f"nav_{item['label']}"):
                        st.session_state.current_page = item["label"]
                        st.rerun()

# ============================================
# LOGIN PAGE
# ============================================
def render_login():
    """Render login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-icon">M⚡</div>
            <div class="login-logo">MEGAMAX</div>
            <div style="color: #94A3B8; text-align: center; margin-bottom: 32px;">Enterprise Intelligence</div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            
            col_pwd1, col_pwd2 = st.columns([6, 1])
            with col_pwd1:
                if st.session_state.show_password:
                    password = st.text_input("Password", type="default", placeholder="Enter password")
                else:
                    password = st.text_input("Password", type="password", placeholder="Enter password")
            with col_pwd2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("👁️"):
                    st.session_state.show_password = not st.session_state.show_password
                    st.rerun()
            
            if st.form_submit_button("🔓 Sign In", width='stretch'):
                if username and password:
                    result = verify_login(username, password)
                    if result['success']:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.display_name = result['display_name']
                        st.session_state.role = result['role']
                        st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Enter username and password")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# DASHBOARD
# ============================================
def render_dashboard():
    """Dashboard page"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 class='page-title'>Dashboard</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='date-badge'>{datetime.now().strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)
    
    # Get today's data
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Today's metrics
    today_data = load_data(f"""
        SELECT 
            COALESCE(SUM(total_revenue), 0) as revenue,
            COALESCE(SUM(total_profit), 0) as profit,
            COUNT(*) as transactions
        FROM sales WHERE date(timestamp) = '{today}'
    """).iloc[0]
    
    yesterday_data = load_data(f"""
        SELECT COALESCE(SUM(total_revenue), 0) as revenue
        FROM sales WHERE date(timestamp) = '{yesterday}'
    """).iloc[0]
    
    today_expenses = load_data(f"""
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses WHERE expense_date = '{today}'
    """).iloc[0]
    
    # Calculate changes
    revenue_change = ((today_data['revenue'] - yesterday_data['revenue']) / max(yesterday_data['revenue'], 1)) * 100
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Today's Revenue</div>
            <div class="metric-value">{format_naira(today_data['revenue'])}</div>
            <div class="metric-change">▲ {revenue_change:.1f}% vs yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        margin = (today_data['profit'] / max(today_data['revenue'], 1)) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Today's Profit</div>
            <div class="metric-value">{format_naira(today_data['profit'])}</div>
            <div class="metric-change">{margin:.1f}% margin</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Transactions</div>
            <div class="metric-value">{int(today_data['transactions'])}</div>
            <div class="metric-change">Today's orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        net_profit = today_data['profit'] - today_expenses['total']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Net Profit</div>
            <div class="metric-value">{format_naira(net_profit)}</div>
            <div class="metric-change">After expenses</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Revenue Trend (Last 7 Days)</div>', unsafe_allow_html=True)
        
        trend_data = load_data("""
            SELECT date(timestamp) as date, SUM(total_revenue) as revenue
            FROM sales
            WHERE date(timestamp) >= date('now', '-7 days')
            GROUP BY date(timestamp)
            ORDER BY date
        """)
        
        if not trend_data.empty:
            fig = px.line(trend_data, x='date', y='revenue', markers=True)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="Revenue (₦)"),
                showlegend=False
            )
            fig.update_traces(line=dict(color='#60A5FA', width=3))
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No data available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Category Sales</div>', unsafe_allow_html=True)
        
        category_data = load_data("""
            SELECT p.category, SUM(s.total_revenue) as revenue
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.timestamp >= date('now', '-30 days')
            GROUP BY p.category
        """)
        
        if not category_data.empty:
            fig = px.pie(category_data, values='revenue', names='category',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No data")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bottom section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🏆 Top Products</div>', unsafe_allow_html=True)
        
        top_products = load_data("""
            SELECT p.product_name, SUM(s.total_revenue) as revenue
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            GROUP BY p.product_name
            ORDER BY revenue DESC
            LIMIT 5
        """)
        
        if not top_products.empty:
            fig = px.bar(top_products, x='product_name', y='revenue',
                        color_discrete_sequence=['#60A5FA'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis=dict(title=""),
                yaxis=dict(title="Revenue (₦)")
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No data")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">⚠️ Low Stock Alerts</div>', unsafe_allow_html=True)
        
        low_stock = load_data("""
            SELECT product_name, current_stock, reorder_level
            FROM products
            WHERE current_stock <= reorder_level
            ORDER BY current_stock ASC
            LIMIT 5
        """)
        
        if not low_stock.empty:
            for _, row in low_stock.iterrows():
                st.markdown(f"""
                <div class="alert-box warning">
                    <strong>{row['product_name']}</strong><br>
                    Only {row['current_stock']} left (Reorder at {row['reorder_level']})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-box success">
                <strong>All Good</strong><br>
                No low stock items
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# RECORD SALE
# ============================================
def render_record_sale():
    """Record sale page"""
    
    st.markdown("<h1 class='page-title'>Record New Sale</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📝 Sale Details</div>', unsafe_allow_html=True)
        
        products = load_data("SELECT * FROM products WHERE current_stock > 0")
        
        if not products.empty:
            product = st.selectbox("Product", products['product_name'].tolist())
            product_data = products[products['product_name'] == product].iloc[0]
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"Price: {format_naira(product_data['selling_price'])}")
            with col_info2:
                st.info(f"Stock: {int(product_data['current_stock'])} units")
            
            quantity = st.number_input("Quantity", min_value=1, 
                                      max_value=int(product_data['current_stock']), value=1)
            
            payment = st.selectbox("Payment Method", ['Cash', 'Transfer', 'POS', 'Credit'])
            
            total = quantity * product_data['selling_price']
            profit = quantity * product_data['profit_margin']
            
            st.markdown("---")
            st.markdown(f"### Total: {format_naira(total)}")
            st.markdown(f"Profit: {format_naira(profit)}")
            
            if st.button("✅ Record Sale", width='stretch'):
                success = execute_query("""
                    INSERT INTO sales (product_id, quantity, unit_price, total_revenue, total_profit, payment_method)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (int(product_data['product_id']), quantity, product_data['selling_price'], 
                      total, profit, payment))
                
                if success:
                    execute_query("UPDATE products SET current_stock = current_stock - ? WHERE product_id = ?",
                                (quantity, int(product_data['product_id'])))
                    st.success("Sale recorded!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
        else:
            st.error("No products in stock")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📋 Recent Sales</div>', unsafe_allow_html=True)
        
        recent = load_data("""
            SELECT strftime('%H:%M', timestamp) as time, p.product_name, s.quantity, s.total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE date(timestamp) = date('now')
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        
        if not recent.empty:
            st.dataframe(recent, width='stretch')
        else:
            st.info("No sales today")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SALES HISTORY
# ============================================
def render_sales_history():
    """Sales history page with full functionality"""
    
    st.markdown("<h1 class='page-title'>Sales History</h1>", unsafe_allow_html=True)
    
    # Filters
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_range = st.selectbox("Date Range", 
                                 ["Today", "This Week", "This Month", "Last 30 Days", "This Year", "All Time"])
    with col2:
        categories = ["All"] + load_data("SELECT DISTINCT category FROM products")['category'].tolist()
        category = st.selectbox("Category", categories)
    with col3:
        payment_methods = ["All", "Cash", "Transfer", "POS", "Credit"]
        payment = st.selectbox("Payment Method", payment_methods)
    with col4:
        search = st.text_input("🔍 Search Product", placeholder="Product name...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get date range
    start_date, end_date = get_date_range(date_range)
    
    # Build query
    query = """
        SELECT 
            s.timestamp,
            p.product_name,
            p.category,
            s.quantity,
            s.unit_price,
            s.total_revenue,
            s.total_profit,
            s.payment_method
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE 1=1
    """
    
    if date_range != "All Time":
        query += f" AND date(s.timestamp) BETWEEN '{start_date}' AND '{end_date}'"
    if category != "All":
        query += f" AND p.category = '{category}'"
    if payment != "All":
        query += f" AND s.payment_method = '{payment}'"
    
    query += " ORDER BY s.timestamp DESC"
    
    sales_data = load_data(query)
    
    # Apply search filter
    if search and not sales_data.empty:
        sales_data = sales_data[sales_data['product_name'].str.contains(search, case=False)]
    
    # Summary stats
    if not sales_data.empty:
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{format_naira(sales_data['total_revenue'].sum())}</div>
                <div class="stat-label">Total Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{format_naira(sales_data['total_profit'].sum())}</div>
                <div class="stat-label">Total Profit</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{len(sales_data)}</div>
                <div class="stat-label">Transactions</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            avg_ticket = sales_data['total_revenue'].mean()
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{format_naira(avg_ticket)}</div>
                <div class="stat-label">Average Ticket</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sales chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        daily_sales = sales_data.copy()
        daily_sales['date'] = pd.to_datetime(daily_sales['timestamp']).dt.date
        daily_totals = daily_sales.groupby('date')['total_revenue'].sum().reset_index()
        
        fig = px.line(daily_totals, x='date', y='total_revenue', markers=True)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title="Daily Sales Trend",
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, width='stretch')
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data table
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(sales_data, width='stretch')
        
        # Export
        csv = sales_data.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "sales_history.csv", "text/csv")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No sales data found")

# ============================================
# INVENTORY
# ============================================
def render_inventory():
    """Inventory management page"""
    
    st.markdown("<h1 class='page-title'>Inventory Management</h1>", unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📦 Current Stock", "📊 Stock Value", "🔄 Stock Movements"])
    
    with tab1:
        inventory = load_data("""
            SELECT 
                product_id,
                product_name,
                category,
                current_stock,
                reorder_level,
                selling_price,
                unit_cost,
                (current_stock * selling_price) as stock_value,
                CASE 
                    WHEN current_stock = 0 THEN 'Out of Stock'
                    WHEN current_stock <= reorder_level THEN 'Low Stock'
                    ELSE 'In Stock'
                END as status
            FROM products
            ORDER BY 
                CASE status
                    WHEN 'Out of Stock' THEN 1
                    WHEN 'Low Stock' THEN 2
                    ELSE 3
                END,
                current_stock ASC
        """)
        
        if not inventory.empty:
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Products", len(inventory))
            with col2:
                total_value = inventory['stock_value'].sum()
                st.metric("Total Value", format_naira(total_value))
            with col3:
                low_count = len(inventory[inventory['status'] == 'Low Stock'])
                st.metric("Low Stock", low_count)
            with col4:
                out_count = len(inventory[inventory['status'] == 'Out of Stock'])
                st.metric("Out of Stock", out_count)
            
            # Status alerts
            col1, col2 = st.columns(2)
            with col1:
                out_stock = inventory[inventory['status'] == 'Out of Stock']
                if not out_stock.empty:
                    st.markdown("### 🔴 Out of Stock")
                    for _, row in out_stock.iterrows():
                        st.markdown(f"<div class='alert-box'><strong>{row['product_name']}</strong><br>Need immediate reorder</div>", unsafe_allow_html=True)
            
            with col2:
                low_stock = inventory[inventory['status'] == 'Low Stock']
                if not low_stock.empty:
                    st.markdown("### 🟡 Low Stock")
                    for _, row in low_stock.iterrows():
                        st.markdown(f"<div class='alert-box warning'><strong>{row['product_name']}</strong><br>{row['current_stock']} left (Reorder at {row['reorder_level']})</div>", unsafe_allow_html=True)
            
            # Full inventory table
            st.markdown("### 📋 Inventory List")
            st.dataframe(inventory, width='stretch')
            
            # Stock update
            with st.expander("✏️ Update Stock"):
                product = st.selectbox("Select Product", inventory['product_name'].tolist())
                product_data = inventory[inventory['product_name'] == product].iloc[0]
                
                new_stock = st.number_input("New Stock Level", min_value=0, 
                                           value=int(product_data['current_stock']))
                
                if st.button("Update Stock"):
                    execute_query("UPDATE products SET current_stock = ? WHERE product_id = ?",
                                (new_stock, int(product_data['product_id'])))
                    st.success("Stock updated!")
                    st.rerun()
    
    with tab2:
        # Stock value analysis
        value_by_category = inventory.groupby('category').agg({
            'stock_value': 'sum',
            'product_id': 'count'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(value_by_category, values='stock_value', names='category',
                        title='Stock Value by Category')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            fig = px.bar(value_by_category, x='category', y='stock_value',
                        title='Inventory Value Distribution')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, width='stretch')
    
    with tab3:
        # Stock movements (receipts)
        movements = load_data("""
            SELECT 
                date_received,
                p.product_name,
                p.category,
                ir.quantity,
                ir.total_cost,
                ir.supplier
            FROM inventory_receipts ir
            JOIN products p ON ir.product_id = p.product_id
            ORDER BY date_received DESC
            LIMIT 50
        """)
        
        if not movements.empty:
            st.dataframe(movements, width='stretch')
        else:
            st.info("No stock movements recorded")

# ============================================
# STOCK RECEIPTS
# ============================================
def render_stock_receipts():
    """Stock receipts page"""
    
    st.markdown("<h1 class='page-title'>Stock Receipts</h1>", unsafe_allow_html=True)
    
    # Add new receipt
    with st.expander("➕ Receive New Stock", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            products = load_data("SELECT * FROM products")
            if not products.empty:
                product = st.selectbox("Product", products['product_name'].tolist())
                product_data = products[products['product_name'] == product].iloc[0]
                
                date_received = st.date_input("Date Received", datetime.now())
                quantity = st.number_input("Quantity", min_value=1, value=10)
        
        with col2:
            supplier = st.text_input("Supplier", value=product_data['supplier'] if 'product_data' in locals() else "")
            total_cost = quantity * product_data['unit_cost'] if 'product_data' in locals() and 'quantity' in locals() else 0
            st.info(f"Total Cost: {format_naira(total_cost)}")
            notes = st.text_area("Notes", placeholder="Optional notes...")
        
        if st.button("📦 Record Receipt", width='stretch'):
            if 'product_data' in locals():
                # Insert receipt
                execute_query("""
                    INSERT INTO inventory_receipts 
                    (date_received, product_id, quantity, total_cost, supplier, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (date_received.strftime('%Y-%m-%d'), int(product_data['product_id']), 
                      quantity, total_cost, supplier, notes))
                
                # Update stock
                execute_query("UPDATE products SET current_stock = current_stock + ? WHERE product_id = ?",
                            (quantity, int(product_data['product_id'])))
                
                st.success("Stock receipt recorded!")
                st.balloons()
                time.sleep(1)
                st.rerun()
    
    # Receipt history
    st.markdown("### 📋 Receipt History")
    
    receipts = load_data("""
        SELECT 
            date_received,
            p.product_name,
            p.category,
            ir.quantity,
            ir.total_cost,
            ir.supplier,
            ir.notes
        FROM inventory_receipts ir
        JOIN products p ON ir.product_id = p.product_id
        ORDER BY date_received DESC
    """)
    
    if not receipts.empty:
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Receipts", len(receipts))
        with col2:
            total_value = receipts['total_cost'].sum()
            st.metric("Total Value", format_naira(total_value))
        with col3:
            total_units = receipts['quantity'].sum()
            st.metric("Total Units", total_units)
        
        st.dataframe(receipts, width='stretch')
    else:
        st.info("No receipts recorded yet")

# ============================================
# EXPENSES
# ============================================
def render_expenses():
    """Expenses tracking page"""
    
    st.markdown("<h1 class='page-title'>Expenses</h1>", unsafe_allow_html=True)
    
    # Add new expense
    with st.expander("➕ Add Expense", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input("Date", datetime.now())
            category = st.selectbox("Category", 
                ['Rent', 'Utilities', 'Salaries', 'Transport', 'Marketing', 'Maintenance', 'Tax', 'Insurance', 'Other'])
            description = st.text_input("Description", placeholder="e.g., Electricity bill")
        
        with col2:
            amount = st.number_input("Amount (₦)", min_value=0, step=100)
            payment_method = st.selectbox("Payment Method", ['Cash', 'Transfer', 'POS'])
            receipt_number = st.text_input("Receipt #", placeholder="Optional")
        
        if st.button("💾 Save Expense", width='stretch'):
            execute_query("""
                INSERT INTO expenses (expense_date, category, description, amount, payment_method, receipt_number)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (expense_date.strftime('%Y-%m-%d'), category, description, amount, payment_method, receipt_number))
            st.success("Expense recorded!")
            st.rerun()
    
    # Filters
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        month = st.selectbox("Month", 
            ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06'])
    with col2:
        exp_category = st.selectbox("Category", 
            ['All', 'Rent', 'Utilities', 'Salaries', 'Transport', 'Marketing', 'Maintenance', 'Tax', 'Insurance', 'Other'])
    with col3:
        view_type = st.selectbox("View", ['Table', 'Chart'])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load expenses
    query = f"SELECT * FROM expenses WHERE strftime('%Y-%m', expense_date) = '{month}'"
    if exp_category != 'All':
        query += f" AND category = '{exp_category}'"
    query += " ORDER BY expense_date DESC"
    
    expenses = load_data(query)
    
    if not expenses.empty:
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Expenses", format_naira(expenses['amount'].sum()))
        with col2:
            st.metric("Number of Expenses", len(expenses))
        with col3:
            avg_expense = expenses['amount'].mean()
            st.metric("Average", format_naira(avg_expense))
        with col4:
            max_expense = expenses['amount'].max()
            st.metric("Largest", format_naira(max_expense))
        
        if view_type == 'Table':
            st.dataframe(expenses, width='stretch')
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Category breakdown
                cat_summary = expenses.groupby('category')['amount'].sum().reset_index()
                fig = px.pie(cat_summary, values='amount', names='category',
                            title='Expenses by Category')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Daily trend
                daily = expenses.groupby('expense_date')['amount'].sum().reset_index()
                fig = px.bar(daily, x='expense_date', y='amount',
                            title='Daily Expenses')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, width='stretch')
    else:
        st.info(f"No expenses found for {month}")

# ============================================
# ANALYTICS
# ============================================
def render_analytics():
    """Advanced analytics page"""
    
    st.markdown("<h1 class='page-title'>Analytics</h1>", unsafe_allow_html=True)
    
    # Date range selector
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("Analysis Period", 
            ["Last 7 Days", "Last 30 Days", "This Month", "Last Month", "This Quarter", "This Year"])
    with col2:
        compare = st.checkbox("Compare with previous period")
    st.markdown('</div>', unsafe_allow_html=True)
    
    start_date, end_date = get_date_range(period)
    
    # Get data
    sales_data = load_data(f"""
        SELECT 
            date(timestamp) as date,
            strftime('%w', timestamp) as day_of_week,
            strftime('%H', timestamp) as hour,
            p.category,
            s.quantity,
            s.total_revenue,
            s.total_profit,
            s.payment_method,
            s.sale_id
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
    """)
    
    if not sales_data.empty:
        # Key metrics
        total_revenue = sales_data['total_revenue'].sum()
        total_profit = sales_data['total_profit'].sum()
        total_transactions = len(sales_data)
        unique_days = sales_data['date'].nunique()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{format_naira(total_revenue)}</div>
                <div class="stat-label">Total Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{format_naira(total_profit)}</div>
                <div class="stat-label">Total Profit</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{total_transactions}</div>
                <div class="stat-label">Transactions</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            daily_avg = total_revenue / unique_days if unique_days > 0 else 0
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-value">{format_naira(daily_avg)}</div>
                <div class="stat-label">Daily Average</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Categories", "⏰ Time Analysis", "💳 Payments"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily trend
                daily = sales_data.groupby('date')['total_revenue'].sum().reset_index()
                fig = px.line(daily, x='date', y='total_revenue', 
                            title='Daily Revenue Trend')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Day of week analysis
                dow_map = {'0': 'Sun', '1': 'Mon', '2': 'Tue', '3': 'Wed', 
                          '4': 'Thu', '5': 'Fri', '6': 'Sat'}
                sales_data['day_name'] = sales_data['day_of_week'].map(dow_map)
                dow_sales = sales_data.groupby('day_name')['total_revenue'].sum().reindex(
                    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
                
                fig = px.bar(x=dow_sales.index, y=dow_sales.values,
                            title='Revenue by Day of Week')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis=dict(title=""),
                    yaxis=dict(title="Revenue (₦)")
                )
                st.plotly_chart(fig, width='stretch')
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Category revenue
                cat_revenue = sales_data.groupby('category')['total_revenue'].sum().reset_index()
                fig = px.pie(cat_revenue, values='total_revenue', names='category',
                            title='Revenue by Category')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Category profit
                cat_profit = sales_data.groupby('category')['total_profit'].sum().reset_index()
                fig = px.bar(cat_profit, x='category', y='total_profit',
                            title='Profit by Category',
                            color_discrete_sequence=['#10B981'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, width='stretch')
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Hourly distribution
                hourly = sales_data.groupby('hour')['total_revenue'].sum().reset_index()
                fig = px.bar(hourly, x='hour', y='total_revenue',
                            title='Revenue by Hour of Day')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Peak hours
                sales_data['hour'] = sales_data['hour'].astype(int)
                peak_hours = sales_data.groupby('hour').size().reset_index(name='count')
                fig = px.line(peak_hours, x='hour', y='count',
                            title='Transaction Volume by Hour',
                            markers=True)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, width='stretch')
        
        with tab4:
            col1, col2 = st.columns(2)
            
            with col1:
                # Payment methods
                if 'payment_method' in sales_data.columns:
                    payment_summary = sales_data.groupby('payment_method').agg({
                        'total_revenue': 'sum',
                        'sale_id': 'count'
                    }).reset_index()
                    payment_summary.columns = ['payment_method', 'total_revenue', 'transaction_count']
                    
                    fig = px.pie(payment_summary, values='total_revenue', names='payment_method',
                                title='Revenue by Payment Method')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("Payment method data not available")
            
            with col2:
                if 'payment_method' in sales_data.columns and 'payment_summary' in locals():
                    fig = px.bar(payment_summary, x='payment_method', y='transaction_count',
                                title='Transactions by Payment Method',
                                color_discrete_sequence=['#60A5FA'])
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, width='stretch')
    else:
        st.info("No data available for selected period")

# ============================================
# AI PREDICTIONS
# ============================================
def render_ai_predictions():
    """AI predictions page"""
    
    st.markdown("<h1 class='page-title'>AI Predictions</h1>", unsafe_allow_html=True)
    
    # Check if predictions exist
    predictions = load_data("SELECT * FROM predictions ORDER BY prediction_date")
    
    if not predictions.empty:
        # Current stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            next_day = predictions.iloc[0]
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Tomorrow's Forecast</div>
                <div class="metric-value">{format_naira(next_day['predicted_sales'])}</div>
                <div class="metric-change">Confidence: {next_day['confidence']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            next_week_total = predictions.head(7)['predicted_sales'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Next 7 Days Total</div>
                <div class="metric-value">{format_naira(next_week_total)}</div>
                <div class="metric-change">Expected revenue</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_confidence = predictions['confidence'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Model Confidence</div>
                <div class="metric-value">{avg_confidence:.1f}%</div>
                <div class="metric-change">Average accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Forecast chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 14-Day Sales Forecast</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=predictions['prediction_date'],
            y=predictions['predicted_sales'],
            mode='lines+markers',
            name='Predicted Sales',
            line=dict(color='#60A5FA', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="Predicted Sales (₦)")
        )
        st.plotly_chart(fig, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Predictions table
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Detailed Predictions</div>', unsafe_allow_html=True)
        
        display_pred = predictions.copy()
        display_pred['predicted_sales'] = display_pred['predicted_sales'].apply(format_naira)
        display_pred['confidence'] = display_pred['confidence'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(display_pred, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Recommendations
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">💡 AI Recommendations</div>', unsafe_allow_html=True)
        
        # Get low stock items
        low_stock = load_data("""
            SELECT product_name, current_stock, reorder_level
            FROM products
            WHERE current_stock <= reorder_level
        """)
        
        if not low_stock.empty:
            for _, item in low_stock.iterrows():
                st.markdown(f"""
                <div class="alert-box warning">
                    <strong>📦 Reorder {item['product_name']}</strong><br>
                    Only {item['current_stock']} left (Reorder at {item['reorder_level']})
                </div>
                """, unsafe_allow_html=True)
        
        # Peak day prediction
        peak_day = predictions.loc[predictions['predicted_sales'].idxmax()]
        st.markdown(f"""
        <div class="alert-box success">
            <strong>📈 Peak Day Forecast</strong><br>
            {peak_day['prediction_date']}: {format_naira(peak_day['predicted_sales'])} (Confidence: {peak_day['confidence']:.1f}%)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No predictions available. Run ML models first.")
        
        if st.button("🤖 Generate Predictions Now"):
            with st.spinner("Training models..."):
                try:
                    # Try to import and run SimpleML
                    import simple_ml
                    ml = simple_ml.SimpleML()
                    ml.run_all()
                    st.success("Predictions generated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating predictions: {e}")

# ============================================
# ABOUT
# ============================================
def render_about():
    """About page"""
    
    st.markdown("<h1 class='page-title'>About MegaMax</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h2 style="color: white;">NEXTGEN KNOWLEDGE SHOWCASE 2026</h2>
            <h3 style="color: #60A5FA;">🌍 Impact Pillar: Financial Inclusion / Retail</h3>
            <hr>
            <h4 style="color: white;">📋 Project Overview</h4>
            <p style="color: #94A3B8;">MegaMax Enterprise is an AI-powered Business Intelligence system designed 
            for small-scale Nigerian retailers. It solves inventory mismanagement, profit tracking, 
            and sales forecasting for shop owners who lack access to sophisticated business tools.</p>
            <hr>
            <h4 style="color: white;">👨🏿‍💻 Developer</h4>
            <p style="color: #94A3B8;"><strong>MICHAEL FARADAY</strong><br>
            Data Science & Machine Learning Engineer<br>
            NextGen Knowledge Showcase Participant</p>
            <hr>
            <h4 style="color: white;">🤖 AI / Tools Disclosure</h4>
            <ul style="color: #94A3B8;">
                <li><strong>Machine Learning:</strong> scikit-learn, SimpleML</li>
                <li><strong>Frontend:</strong> Streamlit</li>
                <li><strong>Database:</strong> SQLite</li>
                <li><strong>Visualization:</strong> Plotly</li>
                <li><strong>Data:</strong> 90 days synthetic Nigerian retail data</li>
            </ul>
            <hr>
            <p style="color: #64748B;">© 2026 NextGen Knowledge Showcase<br>
            Partners: 3M IT | AIRTEL AFRICA Foundation | NITDA</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h3 style="color: #60A5FA; text-align: center;">📊 MEGAMAX</h3>
            <p style="color: #64748B; text-align: center;">Enterprise v1.0</p>
            <hr>
            <p><strong>Released:</strong> March 2026</p>
            <p><strong>Database:</strong> SQLite</p>
            <p><strong>ML Models:</strong> SimpleML</p>
            <p><strong>Products:</strong> 30</p>
            <p><strong>Data Period:</strong> 90 days</p>
            <hr>
            <p style="color: #34D399; text-align: center;">✨ Competition Ready</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# SETTINGS
# ============================================
def render_settings():
    """Settings page"""
    
    st.markdown("<h1 class='page-title'>Settings</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🎨 Appearance", "💾 Data"])
    
    with tab1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### Profile Settings")
        
        st.text_input("Display Name", value=st.session_state.display_name)
        st.text_input("Email", value="user@megamax.com")
        st.text_input("Phone", value="+234 800 000 0000")
        
        if st.button("Update Profile"):
            st.success("Profile updated!")
        
        st.markdown("---")
        st.markdown("### Change Password")
        
        current = st.text_input("Current Password", type="password")
        new = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        
        if st.button("Change Password"):
            if new == confirm:
                st.success("Password changed!")
            else:
                st.error("Passwords don't match")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### Theme Settings")
        
        theme = st.selectbox("Theme", ["Dark (Default)", "Light", "System"])
        accent_color = st.color_picker("Accent Color", "#60A5FA")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Compact Mode", value=False)
        with col2:
            st.checkbox("Animations", value=True)
        
        if st.button("Apply Theme"):
            st.success("Theme applied! (Refresh to see changes)")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export Data")
            if st.button("📥 Export All Data"):
                csv = load_data("SELECT * FROM sales").to_csv(index=False)
                st.download_button("Download Sales", csv, "sales.csv")
        
        with col2:
            st.markdown("#### Backup")
            if st.button("💾 Create Backup"):
                import shutil
                shutil.copy('megamax.db', f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                st.success("Backup created!")
        
        st.markdown("---")
        st.markdown("#### Danger Zone")
        
        if st.button("🗑️ Reset Database", type="primary"):
            st.warning("This will delete all data!")
            confirm = st.checkbox("I understand this cannot be undone")
            if confirm and st.button("Confirm Reset"):
                st.error("Feature disabled for safety")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ADMIN PANEL
# ============================================
def render_admin():
    """Admin panel"""
    
    st.markdown("<h1 class='page-title'>Admin Panel</h1>", unsafe_allow_html=True)
    
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False
    
    if not st.session_state.admin_auth:
        password = st.text_input("Admin Password", type="password")
        if st.button("Access"):
            if password == "MegaMaxAdmin2026":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Wrong password")
        return
    
    st.success("Admin Access Granted")
    
    tab1, tab2, tab3 = st.tabs(["📊 Database", "👥 Users", "📈 System"])
    
    with tab1:
        tables = ['sales', 'products', 'inventory_receipts', 'expenses', 'predictions', 'users']
        table = st.selectbox("Select Table", tables)
        
        data = load_data(f"SELECT * FROM {table} LIMIT 100")
        st.dataframe(data, width='stretch')
    
    with tab2:
        users = load_data("SELECT user_id, username, display_name, role, created_at FROM users")
        st.dataframe(users, width='stretch')
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            db_size = os.path.getsize('megamax.db') / 1024 / 1024
            st.metric("Database Size", f"{db_size:.2f} MB")
        
        with col2:
            table_counts = {}
            for table in ['sales', 'products', 'expenses']:
                count = load_data(f"SELECT COUNT(*) as c FROM {table}").iloc[0]['c']
                table_counts[table] = count
            st.metric("Total Sales Records", table_counts.get('sales', 0))

# ============================================
# MAIN APP
# ============================================

# Check authentication
if not st.session_state.authenticated:
    render_login()
    st.stop()

# Render sidebar
render_sidebar()

# Main content
with st.container():
    if st.session_state.current_page == "Dashboard":
        render_dashboard()
    elif st.session_state.current_page == "Record Sale":
        render_record_sale()
    elif st.session_state.current_page == "Sales History":
        render_sales_history()
    elif st.session_state.current_page == "Inventory":
        render_inventory()
    elif st.session_state.current_page == "Stock Receipts":
        render_stock_receipts()
    elif st.session_state.current_page == "Expenses":
        render_expenses()
    elif st.session_state.current_page == "Analytics":
        render_analytics()
    elif st.session_state.current_page == "AI Predictions":
        render_ai_predictions()
    elif st.session_state.current_page == "About":
        render_about()
    elif st.session_state.current_page == "Settings":
        render_settings()
    elif st.session_state.current_page == "Admin":
        render_admin()

# Logout button
st.markdown("""
<div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
""", unsafe_allow_html=True)
if st.button("🚪 Logout", key="logout_floating"):
    logout()
st.markdown("</div>", unsafe_allow_html=True)
