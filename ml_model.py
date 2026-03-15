import sqlite3
import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime, timedelta

class MegaMaxML:
    """Machine Learning models for MegaMax Enterprise"""
    
    def __init__(self, db_path='megamax.db'):
        self.db_path = db_path
        self.conn = None
        self.models_dir = 'saved_models'
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            print(f"📁 Created models directory: {self.models_dir}")
    
    def connect_db(self):
        self.conn = sqlite3.connect(self.db_path)
    
    def close_db(self):
        if self.conn:
            self.conn.close()
    
    def train_sales_forecast(self):
        """Train Prophet model for sales forecasting"""
        print("\n📈 Training Sales Forecast Model...")
        
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
        
        print(f"   Training data: {len(df)} days")
        
        # Train Prophet model
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05
        )
        
        # Add custom seasonalities
        model.add_country_holidays(country_name='Nigeria')
        
        model.fit(df)
        
        # Save model
        model_path = f'{self.models_dir}/prophet_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"   ✅ Model saved to: {model_path}")
        return model
    
    def generate_predictions(self, days=14):
        """Generate predictions for next N days"""
        print(f"\n🔮 Generating {days}-day forecast...")
        
        # Load model
        model_path = f'{self.models_dir}/prophet_model.pkl'
        if not os.path.exists(model_path):
            print("   ⚠️ Model not found. Training first...")
            model = self.train_sales_forecast()
        else:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        
        # Make future dataframe
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        
        # Get predictions
        predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)
        
        # Save to database
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM predictions")  # Clear old predictions
        
        for _, row in predictions.iterrows():
            pred_date = row['ds'].strftime('%Y-%m-%d')
            pred_value = float(row['yhat'])
            
            # Calculate confidence based on prediction interval width
            interval_width = row['yhat_upper'] - row['yhat_lower']
            confidence = max(0, min(100, 100 - (interval_width / row['yhat'] * 30)))
            
            cursor.execute('''
            INSERT INTO predictions (prediction_date, predicted_sales, confidence, model_version)
            VALUES (?, ?, ?, ?)
            ''', (pred_date, pred_value, confidence, 'Prophet v1.0 (MegaMax)'))
        
        self.conn.commit()
        
        print(f"   ✅ Generated predictions for next {days} days")
        print(f"   📅 Next 7 days:")
        for _, row in predictions.head(7).iterrows():
            print(f"      {row['ds'].strftime('%a %d %b')}: ₦{row['yhat']:,.0f}")
        
        return predictions
    
    def segment_products(self):
        """Cluster products into performance segments"""
        print("\n📊 Performing Product Segmentation...")
        
        # Get product performance metrics
        query = """
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            p.unit_cost,
            p.selling_price,
            p.profit_margin,
            p.current_stock,
            COALESCE(AVG(s.quantity), 0) as avg_daily_sales,
            COALESCE(COUNT(s.sale_id), 0) as total_sales_count,
            COALESCE(SUM(s.total_revenue), 0) as total_revenue,
            COALESCE(SUM(s.total_profit), 0) as total_profit
        FROM products p
        LEFT JOIN sales s ON p.product_id = s.product_id
        GROUP BY p.product_id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Features for clustering
        features = ['profit_margin', 'avg_daily_sales', 'total_revenue']
        X = df[features].fillna(0)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-Means clustering
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        df['segment'] = kmeans.fit_predict(X_scaled)
        
        # Map segments to business categories
        segment_names = {
            0: '⭐ STAR (High profit, High sales)',
            1: '💰 CASH COW (High sales, Low profit)',
            2: '❓ QUESTION MARK (High profit, Low sales)',
            3: '🐕 DOG (Low profit, Low sales)'
        }
        df['segment_name'] = df['segment'].map(segment_names)
        
        # Save results
        output_path = f'{self.models_dir}/product_segments.csv'
        df.to_csv(output_path, index=False)
        
        # Print summary
        print(f"   ✅ Product segmentation complete!")
        print(f"   📁 Saved to: {output_path}")
        print(f"\n   📊 Segment Distribution:")
        for seg in range(4):
            count = len(df[df['segment'] == seg])
            name = segment_names[seg].split(' ')[1]
            print(f"      {name}: {count} products")
        
        return df
    
    def detect_anomalies(self):
        """Detect unusual sales patterns"""
        print("\n🚨 Detecting Anomalies...")
        
        # Get daily sales
        query = """
        SELECT 
            date(timestamp) as sale_date,
            SUM(total_revenue) as daily_revenue,
            COUNT(*) as transaction_count
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Simple statistical anomaly detection
        mean = df['daily_revenue'].mean()
        std = df['daily_revenue'].std()
        
        # Flag days with revenue > 2 standard deviations from mean
        df['is_anomaly'] = abs(df['daily_revenue'] - mean) > 2 * std
        df['deviation'] = (df['daily_revenue'] - mean) / std
        
        anomalies = df[df['is_anomaly']].copy()
        
        # Save anomalies
        if len(anomalies) > 0:
            output_path = f'{self.models_dir}/anomalies.csv'
            anomalies.to_csv(output_path, index=False)
            print(f"   ✅ Detected {len(anomalies)} anomaly days")
            print(f"   📁 Saved to: {output_path}")
            
            # Show top anomalies
            print(f"\n   🔍 Top Anomalies:")
            for _, row in anomalies.head(5).iterrows():
                direction = "⬆️ HIGH" if row['daily_revenue'] > mean else "⬇️ LOW"
                print(f"      {row['sale_date']}: {direction} ({row['deviation']:.1f}σ)")
        else:
            print(f"   ✅ No anomalies detected")
        
        return anomalies
    
    def run_all_models(self):
        """Run all ML models"""
        self.connect_db()
        
        print("\n" + "="*50)
        print("🚀 MEGAMAX ENTERPRISE - ML PIPELINE")
        print("="*50)
        
        self.train_sales_forecast()
        predictions = self.generate_predictions(14)
        segments = self.segment_products()
        anomalies = self.detect_anomalies()
        
        self.close_db()
        
        print("\n" + "="*50)
        print("✅ All ML models trained successfully!")
        print("="*50)
        
        return {
            'predictions': predictions,
            'segments': segments,
            'anomalies': anomalies
        }

if __name__ == "__main__":
    ml = MegaMaxML()
    results = ml.run_all_models()