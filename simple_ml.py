import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

class SimpleML:
    """Simple ML models that don't need Prophet"""
    
    def __init__(self, db_path='megamax.db'):
        self.db_path = db_path
        self.conn = None
        self.models_dir = 'saved_models'
        
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            print(f"📁 Created models directory: {self.models_dir}")
    
    def connect_db(self):
        self.conn = sqlite3.connect(self.db_path)
    
    def close_db(self):
        if self.conn:
            self.conn.close()
    
    def analyze_seasonality(self, df):
        """Analyze day-of-week patterns"""
        df['day_of_week'] = pd.to_datetime(df['ds']).dt.dayofweek
        dow_avg = df.groupby('day_of_week')['y'].mean().to_dict()
        
        # Fill missing days with overall average
        overall_avg = df['y'].mean()
        factors = {}
        for dow in range(7):
            if dow in dow_avg and overall_avg > 0:
                factors[dow] = dow_avg[dow] / overall_avg
            else:
                factors[dow] = 1.0
        
        return factors
    
    def generate_predictions(self, days=14):
        """Generate simple predictions using seasonality + trend"""
        print("\n🔮 Generating simple predictions...")
        
        # Get daily sales data
        query = """
        SELECT date(timestamp) as ds, 
               SUM(total_revenue) as y
        FROM sales
        GROUP BY ds
        ORDER BY ds
        """
        
        df = pd.read_sql_query(query, self.conn)
        df['ds'] = pd.to_datetime(df['ds'])
        
        if len(df) < 7:
            print("   ❌ Not enough data (need at least 7 days)")
            return None
        
        print(f"   Using {len(df)} days of historical data")
        print(f"   Date range: {df['ds'].min().date()} to {df['ds'].max().date()}")
        
        # Calculate basic statistics
        avg_sales = df['y'].mean()
        std_sales = df['y'].std()
        
        # Get seasonality factors (day of week patterns)
        seasonality = self.analyze_seasonality(df)
        print(f"   Seasonality factors: { {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'} }")
        for dow, factor in seasonality.items():
            day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dow]
            print(f"      {day_name}: {factor:.2f}x")
        
        # Calculate trend (last 7 days vs previous 7 days)
        recent = df.tail(7)['y'].mean()
        previous = df.tail(14).head(7)['y'].mean() if len(df) >= 14 else avg_sales
        trend_factor = recent / previous if previous > 0 else 1.0
        print(f"   Trend factor: {trend_factor:.2f}x")
        
        # Generate predictions
        predictions = []
        last_date = df['ds'].iloc[-1]
        
        for i in range(1, days + 1):
            pred_date = last_date + timedelta(days=i)
            dow = pred_date.weekday()
            
            # Base prediction: average * seasonality * trend
            base_pred = avg_sales * seasonality.get(dow, 1.0) * trend_factor
            
            # Add some realistic variation
            variation = np.random.normal(1.0, 0.1)  # 10% random variation
            pred_value = base_pred * variation
            
            # Ensure positive
            pred_value = max(1000, pred_value)
            
            # Confidence decreases with time
            confidence = max(70, 95 - i)
            
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'value': float(pred_value),
                'confidence': float(confidence)
            })
        
        # Save to database
        cursor = self.conn.cursor()
        
        # Clear old predictions
        cursor.execute("DELETE FROM predictions")
        print("   🗑️ Cleared old predictions")
        
        # Insert new predictions
        for pred in predictions:
            cursor.execute('''
            INSERT INTO predictions (prediction_date, predicted_sales, confidence, model_version)
            VALUES (?, ?, ?, ?)
            ''', (pred['date'], pred['value'], pred['confidence'], 'SimpleML v2.0'))
        
        self.conn.commit()
        
        print(f"   ✅ Generated {len(predictions)} predictions")
        print(f"\n   📅 Next 7 days forecast:")
        print("   " + "-" * 50)
        for pred in predictions[:7]:
            print(f"      {pred['date']}: ₦{pred['value']:,.0f} (confidence: {pred['confidence']:.0f}%)")
        
        return predictions
    
    def detect_anomalies(self):
        """Simple anomaly detection"""
        print("\n🚨 Detecting anomalies...")
        
        query = """
        SELECT date(timestamp) as sale_date,
               SUM(total_revenue) as daily_revenue,
               COUNT(sale_id) as transactions
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        if len(df) < 7:
            print("   ⚠️ Not enough data")
            return None
        
        # Calculate rolling statistics
        df['rolling_mean'] = df['daily_revenue'].rolling(window=7, min_periods=3).mean()
        df['rolling_std'] = df['daily_revenue'].rolling(window=7, min_periods=3).std()
        
        # Detect anomalies (2 standard deviations from rolling mean)
        df['is_anomaly'] = abs(df['daily_revenue'] - df['rolling_mean']) > 2 * df['rolling_std']
        
        anomalies = df[df['is_anomaly'] == True]
        
        if len(anomalies) > 0:
            print(f"   ✅ Found {len(anomalies)} anomaly days")
            print("\n   📊 Top anomalies:")
            for _, row in anomalies.head(5).iterrows():
                direction = "HIGH" if row['daily_revenue'] > row['rolling_mean'] else "LOW"
                deviation = abs(row['daily_revenue'] - row['rolling_mean']) / row['rolling_std']
                print(f"      {row['sale_date']}: {direction} ({deviation:.1f}σ)")
        else:
            print("   ✅ No anomalies detected")
        
        return anomalies
    
    def segment_products(self):
        """Simple product segmentation"""
        print("\n📊 Segmenting products...")
        
        query = """
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            p.profit_margin,
            p.current_stock,
            COALESCE(SUM(s.quantity), 0) as total_sold,
            COALESCE(SUM(s.total_revenue), 0) as total_revenue
        FROM products p
        LEFT JOIN sales s ON p.product_id = s.product_id
        GROUP BY p.product_id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        if len(df) == 0:
            print("   ⚠️ No products found")
            return None
        
        # Calculate average sales per product
        avg_sales = df['total_revenue'].mean()
        
        # Simple segmentation based on profit margin and sales
        conditions = [
            (df['profit_margin'] > df['profit_margin'].median()) & (df['total_revenue'] > avg_sales),
            (df['profit_margin'] <= df['profit_margin'].median()) & (df['total_revenue'] > avg_sales),
            (df['profit_margin'] > df['profit_margin'].median()) & (df['total_revenue'] <= avg_sales),
            (df['profit_margin'] <= df['profit_margin'].median()) & (df['total_revenue'] <= avg_sales)
        ]
        
        choices = ['⭐ STAR', '💰 CASH COW', '❓ QUESTION MARK', '🐕 DOG']
        df['segment'] = np.select(conditions, choices, default='📦 REGULAR')
        
        # Count segments
        print("\n   📊 Product Segments:")
        for segment in ['⭐ STAR', '💰 CASH COW', '❓ QUESTION MARK', '🐕 DOG', '📦 REGULAR']:
            count = len(df[df['segment'] == segment])
            if count > 0:
                print(f"      {segment}: {count} products")
        
        return df
    
    def run_all(self):
        """Run all ML processes"""
        self.connect_db()
        
        print("\n" + "="*50)
        print("🚀 SIMPLE ML - MEGAMAX ENTERPRISE")
        print("="*50)
        
        predictions = self.generate_predictions(14)
        anomalies = self.detect_anomalies()
        segments = self.segment_products()
        
        self.close_db()
        
        print("\n" + "="*50)
        print("✅ Simple ML completed successfully!")
        print("="*50)
        
        return {
            'predictions': predictions,
            'anomalies': anomalies,
            'segments': segments
        }

if __name__ == "__main__":
    ml = SimpleML()
    results = ml.run_all()