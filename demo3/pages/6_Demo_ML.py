import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

def load_data():
    """Load and prepare the data"""
    try:
        sales_orders = pd.read_csv('data/sales_orders.csv')
        order_items = pd.read_csv('data/order_items.csv')
        sales_orders['order_date'] = pd.to_datetime(sales_orders['order_date'])
        return {'sales_orders': sales_orders, 'order_items': order_items}
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def engineer_features(df):
    """Create time-based features"""
    features_df = df.copy()
    
    # Basic time features
    features_df['day_of_week'] = features_df['order_date'].dt.dayofweek
    features_df['month'] = features_df['order_date'].dt.month
    features_df['day_of_month'] = features_df['order_date'].dt.day
    features_df['is_weekend'] = features_df['day_of_week'].isin([5, 6]).astype(int)
    features_df['is_month_start'] = features_df['day_of_month'].isin([1, 2, 3]).astype(int)
    features_df['is_month_end'] = features_df['day_of_month'].isin([28, 29, 30, 31]).astype(int)
    features_df['year'] = features_df['order_date'].dt.year
    features_df['quarter'] = features_df['order_date'].dt.quarter
    
    # Lag features
    for lag in [1, 2, 3, 7, 14]:
        features_df[f'sales_lag_{lag}'] = features_df['total_sales'].shift(lag)
        features_df[f'orders_lag_{lag}'] = features_df['num_orders'].shift(lag)
    
    # Rolling features
    for window in [7, 14, 30]:
        features_df[f'sales_rolling_mean_{window}'] = features_df['total_sales'].rolling(window=window).mean()
        features_df[f'sales_rolling_std_{window}'] = features_df['total_sales'].rolling(window=window).std()
    
    #NaN
    for col in features_df.columns:
        if 'lag' in col or 'rolling' in col:
            features_df[col] = features_df[col].fillna(features_df[col].mean())
            
    return features_df

def sales_prediction():
    st.header("📈 Sales Prediction with Actual Data Comparison")
    
    data = load_data()
    if not data:
        return
    sales_data = data['order_items'].merge(
        data['sales_orders'][['order_id', 'order_date', 'department', 'customer_id']],
        on='order_id'
    )
    
    # Daily aggregation
    daily_sales = sales_data.groupby('order_date').agg({
        'line_total': ['sum', 'mean', 'count'],
        'quantity': 'sum',
        'customer_id': 'nunique'
    }).reset_index()
    
    daily_sales.columns = ['order_date', 'total_sales', 'avg_sale', 'num_orders', 'total_quantity', 'unique_customers']
    daily_sales = daily_sales.sort_values('order_date')
    
    cutoff_date = pd.Timestamp('2024-07-01')
    
    daily_sales = engineer_features(daily_sales)
    
    #outliers
    train_data = daily_sales[daily_sales['order_date'] < cutoff_date].copy()
    z_scores = np.abs(stats.zscore(train_data['total_sales']))
    train_data = train_data[z_scores < 3].copy()

    features = [
        'day_of_week', 'month', 'day_of_month', 'is_weekend',
        'is_month_start', 'is_month_end', 'num_orders',
        'year', 'quarter', 'total_quantity', 'unique_customers',
        'sales_lag_1', 'sales_lag_2', 'sales_lag_3', 'sales_lag_7',
        'orders_lag_1', 'orders_lag_2', 'orders_lag_3',
        'sales_rolling_mean_7', 'sales_rolling_mean_14', 'sales_rolling_mean_30',
        'sales_rolling_std_7', 'sales_rolling_std_14', 'sales_rolling_std_30'
    ]
    

    X_train = train_data[features]
    y_train = np.log1p(train_data['total_sales'])
    

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        min_samples_split=5,
        min_samples_leaf=4,
        subsample=0.8,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)
    
    future_data = daily_sales[daily_sales['order_date'] >= cutoff_date].copy()
    X_future = future_data[features]
    X_future_scaled = scaler.transform(X_future)
    future_pred = np.expm1(model.predict(X_future_scaled))
    

    train_pred = np.expm1(model.predict(X_train_scaled))
    recent_errors = train_data['total_sales'].values - train_pred
    error_std = np.std(recent_errors[-30:])
    

    fig = go.Figure()
    
    # Training data
    fig.add_trace(go.Scatter(
        x=train_data['order_date'],
        y=train_data['total_sales'],
        name='Historical Sales',
        line=dict(color='blue')
    ))
    
    # Actual future data
    fig.add_trace(go.Scatter(
        x=future_data['order_date'],
        y=future_data['total_sales'],
        name='Actual Sales',
        line=dict(color='green')
    ))
    
    # Predictions
    fig.add_trace(go.Scatter(
        x=future_data['order_date'],
        y=future_pred,
        name='Predicted Sales',
        line=dict(color='red', dash='dash')
    ))
    

    fig.add_trace(go.Scatter(
        x=future_data['order_date'],
        y=future_pred + 1.0 * error_std,
        fill=None,
        mode='lines',
        line_color='rgba(255,0,0,0.1)',
        name='Upper CI'
    ))
    
    fig.add_trace(go.Scatter(
        x=future_data['order_date'],
        y=future_pred - 1.0 * error_std,
        fill='tonexty',
        mode='lines',
        line_color='rgba(255,0,0,0.1)',
        name='Lower CI'
    ))
    
    fig.update_layout(
        title='Sales Forecast vs Actual Sales',
        xaxis_title='Date',
        yaxis_title='Sales (€)',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Calculate metrics for the prediction period
    actual_future = future_data['total_sales'].values
    mse = mean_squared_error(actual_future, future_pred)
    r2 = r2_score(actual_future, future_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((actual_future - future_pred) / actual_future)) * 100
    
    # Display metrics
    #col1, col2, col3, col4 = st.columns(4)
    #with col1:
    #    st.metric("R² Score", f"{r2:.3f}")
    #with col2:
    #    st.metric("RMSE", f"€{rmse:,.2f}")
    #with col3:
    #    st.metric("MSE", f"€{mse:,.2f}")
    #with col4:
    #    st.metric("MAPE", f"{mape:.1f}%")
    
    # Feature importance
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=True)
    
    fig_importance = px.bar(
        importance_df,
        x='Importance',
        y='Feature',
        orientation='h',
        title='Feature Importance'
    )
    
    st.plotly_chart(fig_importance, use_container_width=True)
    
    # Monthly comparison
    monthly_comparison = pd.DataFrame({
        'Date': future_data['order_date'],
        'Actual': future_data['total_sales'],
        'Predicted': future_pred
    })
    monthly_comparison = monthly_comparison.set_index('Date')
    monthly_comparison = monthly_comparison.resample('M').sum()
    monthly_comparison['Difference'] = monthly_comparison['Predicted'] - monthly_comparison['Actual']
    monthly_comparison['Difference %'] = (monthly_comparison['Difference'] / monthly_comparison['Actual'] * 100)
    
    st.subheader("Monthly Comparison")
    st.dataframe(monthly_comparison.round(2))

def main():
    st.set_page_config(page_title="Sales Prediction", layout="wide")
    st.title("🤖 Sales Prediction Application")
    sales_prediction()

if __name__ == "__main__":
    main()