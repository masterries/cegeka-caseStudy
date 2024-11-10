import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def next_steps_outlook():
    # Page Title
    st.title("🚀 Next Steps and Outlook")
    
    st.markdown("""

    """)

    # Section 1: Predictive Analytics
    st.subheader("🔮 Predictive Analytics: Forecasting Demand and Revenue")

    # Mock data for a demand forecast visualization
    dates = pd.date_range(start="2024-01-01", periods=12, freq="M")
    actual_sales = [1500, 1600, 1650, 1700, 1550, 1650, 1720, 1800, 1750, 1850, 1900, 1950]
    forecast_sales = [1520, 1620, 1665, 1725, 1580, 1680, 1750, 1820, 1780, 1880, 1930, 1980]
    forecast_df = pd.DataFrame({"Date": dates, "Actual Sales": actual_sales, "Forecasted Sales": forecast_sales})
    
    fig_forecast = px.line(forecast_df, x="Date", y=["Actual Sales", "Forecasted Sales"], title="Sales Demand Forecast",
                           labels={"value": "Sales Volume", "variable": "Series"}, template="plotly_white")
    st.plotly_chart(fig_forecast, use_container_width=True)

    st.markdown("""
    
    **Algorithms**:
    - **RNN**
    - **Prophet**
    - **Long Short-Term Memory (LSTM) Networks**
    """)

    # Section 2: Customer Segmentation
    st.subheader("👥 Customer Segmentation and Targeting")

    # Mock data for customer segmentation
    customer_data = pd.DataFrame({
        "Customer ID": range(1, 101),
        "Age": np.random.randint(18, 70, size=100),
        "Annual Spend": np.random.randint(500, 10000, size=100)
    })
    customer_data["Segment"] = pd.cut(customer_data["Annual Spend"], bins=[0, 2000, 6000, 10000],
                                      labels=["Low", "Medium", "High"])

    fig_segment = px.scatter(customer_data, x="Age", y="Annual Spend", color="Segment", 
                             title="Customer Segmentation by Age and Spend",
                             labels={"Annual Spend": "Annual Spend ($)", "Age": "Age"},
                             template="plotly_white")
    st.plotly_chart(fig_segment, use_container_width=True)

    st.markdown("""
    **Algorithms**:
    - **K-Means Clustering**
    - **Hierarchical Clustering**
    - **DBSCAN (Density-Based Spatial Clustering of Applications with Noise)**
    """)

    # Section 3: Real-Time Anomaly Detection
    st.subheader("📈 Real-Time Anomaly Detection")

    # Mock data for anomaly detection
    anomaly_data = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=100),
        "Transaction Volume": [100 + np.random.normal(0, 10) for _ in range(90)] + [300, 310, 320] + [100 + np.random.normal(0, 10) for _ in range(7)]
    })

    fig_anomaly = px.line(anomaly_data, x="Date", y="Transaction Volume", title="Anomaly Detection in Transaction Volume",
                          labels={"Transaction Volume": "Volume"}, template="plotly_white")
    fig_anomaly.add_shape(type="rect", x0="2024-04-01", x1="2024-04-03", y0=0, y1=350, fillcolor="red", opacity=0.2, line_width=0)
    st.plotly_chart(fig_anomaly, use_container_width=True)

    st.markdown("""
    **Algorithms**:
    - **Isolation Forest**
    - **Autoencoders**:
    - **One-Class SVM (Support Vector Machine)**
    """)

    # Section 4: Recommendation Systems
    st.subheader("💡 Recommendation Systems")

    # Mock data for recommendation impact
    products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
    before_rec = [100, 150, 120, 130, 110]
    after_rec = [130, 180, 150, 160, 140]
    rec_df = pd.DataFrame({"Product": products, "Before Recommendation": before_rec, "After Recommendation": after_rec})
    
    fig_rec = px.bar(rec_df, x="Product", y=["Before Recommendation", "After Recommendation"], 
                     barmode="group", title="Product Sales Impact from Recommendations",
                     labels={"value": "Sales Volume", "variable": "Series"}, template="plotly_white")
    st.plotly_chart(fig_rec, use_container_width=True)

    st.markdown("""
    **Recommended Algorithms**:
    - **Collaborative Filtering**
    - **Random Forest**
    """)

    # Section 5: Supply Chain Optimization
    st.subheader("📦 Optimizing Supply Chain and Inventory")

    # Mock data for inventory optimization
    inventory_data = pd.DataFrame({
        "Product": ["A", "B", "C", "D", "E"],
        "Optimal Level": [50, 80, 70, 60, 90],
        "Current Stock": [30, 90, 50, 55, 95]
    })
    
    fig_inventory = px.bar(inventory_data, x="Product", y=["Optimal Level", "Current Stock"], 
                           barmode="group", title="Inventory Optimization",
                           labels={"value": "Stock Level", "variable": "Series"}, template="plotly_white")
    st.plotly_chart(fig_inventory, use_container_width=True)

    st.markdown("""
    **Recommended Algorithms**:
    - **Linear Programming**
    - **Reinforcement Learning**
    - **Demand Forecasting Models**
    """)

    # Pitch for Follow-Up Project

# Call the function to display on the Streamlit app
if __name__ == "__main__":
    st.set_page_config(page_title="Next Steps and Outlook", layout="wide")
    next_steps_outlook()
