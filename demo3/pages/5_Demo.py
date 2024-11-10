# pages/6_Data_Ingestion_Process.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import logging
import numpy as np



class StreamlitHandler(logging.Handler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.logs = []
        
    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)
        log_text = "\n".join(self.logs)
        self.placeholder.code(log_text)

def load_data():
    """Lade Daten aus CSV-Dateien"""
    data = {}
    data_files = {
        'sales_orders': 'data/sales_orders.csv',
        'order_items': 'data/order_items.csv',
        'financial_transactions': 'data/financial_transactions.csv',
        'inventory_transactions': 'data/inventory_transactions.csv',
        'products': 'data/products.csv',
        'customers': 'data/customers.csv'
    }
    
    for name, file in data_files.items():
        try:
            df = pd.read_csv(file)
            # Konvertiere Datumsspalten
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            for col in date_columns:
                df[col] = pd.to_datetime(df[col])
            data[name] = df
        except Exception as e:
            st.error(f"Fehler beim Laden von {file}: {str(e)}")
            return None
            
    return data

class DataPipeline:
    def __init__(self, logger):
        self.bronze_layer = {}
        self.silver_layer = {}
        self.gold_layer = {}
        self.logger = logger
        self.processing_metrics = {
            'start_time': None,
            'end_time': None,
            'processing_steps': []
        }

    def process_to_bronze(self, data: dict):
        """Simuliert die Verarbeitung in den Bronze Layer mit echten Daten"""
        self.logger.info("Starting Bronze Layer processing...")
        
        for source, df in data.items():
            start_time = time.time()
            try:
                # Bronze Layer speichert Rohdaten mit Metadaten
                self.bronze_layer[source] = {
                    'data': df.copy(),
                    'metadata': {
                        'ingestion_time': datetime.now().isoformat(),
                        'record_count': len(df),
                        'columns': list(df.columns),
                        'source_system': source
                    }
                }
                
                processing_time = time.time() - start_time
                self.logger.info(f"Loaded {len(df):,} records from {source} into Bronze Layer ({processing_time:.2f}s)")
                
                # Sammle Metriken
                self.processing_metrics['processing_steps'].append({
                    'layer': 'Bronze',
                    'source': source,
                    'records': len(df),
                    'processing_time': processing_time
                })
                
            except Exception as e:
                self.logger.error(f"Error processing {source} to Bronze: {str(e)}")
                raise

    

    def process_to_silver(self):
        """Simuliert die Verarbeitung in den Silver Layer mit Datenvalidierung"""
        self.logger.info("Starting Silver Layer processing...")
        
        for source, bronze_data in self.bronze_layer.items():
            start_time = time.time()
            try:
                df = bronze_data['data'].copy()
                invalid_records = []
                
                # Validierungsregeln je nach Quelle
                if source == 'sales_orders':
                    # Validiere Bestelldaten
                    invalid_mask = (
                        df['order_date'].isna() |
                        df['customer_id'].isna() |
                        (df['order_date'] > pd.Timestamp.now())
                    )
                    invalid_records = df[invalid_mask]
                    df = df[~invalid_mask]
                
                elif source == 'financial_transactions':
                    # Validiere Finanztransaktionen
                    invalid_mask = (
                        (df['payment_date'] < df['invoice_date']) |
                        df['amount'].isna() |
                        (df['amount'] <= 0)
                    )
                    invalid_records = df[invalid_mask]
                    df = df[~invalid_mask]
                
                # Speichere bereinigte Daten im Silver Layer
                self.silver_layer[source] = {
                    'data': df,
                    'invalid_records': invalid_records,
                    'metadata': {
                        'processing_time': datetime.now().isoformat(),
                        'valid_records': len(df),
                        'invalid_records': len(invalid_records),
                        'validation_rate': (len(df) / len(bronze_data['data']) * 100)
                    }
                }
                
                processing_time = time.time() - start_time
                self.logger.info(
                    f"Processed {source} to Silver Layer: "
                    f"{len(df):,} valid records, "
                    f"{len(invalid_records):,} invalid records "
                    f"({processing_time:.2f}s)"
                )
                
                # Sammle Metriken
                self.processing_metrics['processing_steps'].append({
                    'layer': 'Silver',
                    'source': source,
                    'valid_records': len(df),
                    'invalid_records': len(invalid_records),
                    'processing_time': processing_time
                })
                
            except Exception as e:
                self.logger.error(f"Error processing {source} to Silver: {str(e)}")
                raise

    def process_to_gold(self):
        """Simuliert die Verarbeitung in den Gold Layer mit Business Views"""
        self.logger.info("Starting Gold Layer processing...")
        start_time = time.time()
        
        try:
            # 1. Sales Analysis View
            if all(x in self.silver_layer for x in ['sales_orders', 'order_items', 'financial_transactions']):
                sales_orders = self.silver_layer['sales_orders']['data']
                order_items = self.silver_layer['order_items']['data']
                financial = self.silver_layer['financial_transactions']['data']
                
                # Erstelle Sales Analysis
                sales_analysis = sales_orders.merge(
                    order_items,
                    on='order_id',
                    how='left'
                )
                
                # Aggregiere nach Department
                sales_metrics = sales_analysis.groupby('department').agg({
                    'order_id': 'count',
                    'line_total': 'sum'
                }).reset_index()
                
                sales_metrics.columns = ['department', 'order_count', 'total_sales']
                self.gold_layer['sales_metrics'] = sales_metrics
            
            # 2. Inventory Analysis
            if all(x in self.silver_layer for x in ['inventory_transactions', 'products']):
                inventory = self.silver_layer['inventory_transactions']['data']
                products = self.silver_layer['products']['data']
                
                inventory_status = inventory.groupby('product_id').agg({
                    'quantity': 'sum',
                    'transaction_date': 'max'
                }).reset_index()
                
                inventory_status = inventory_status.merge(
                    products[['product_id', 'name', 'category']],
                    on='product_id',
                    how='left'
                )
                
                self.gold_layer['inventory_status'] = inventory_status
            
            processing_time = time.time() - start_time
            self.logger.info(
                f"Created Gold Layer views: "
                f"{', '.join(self.gold_layer.keys())} "
                f"({processing_time:.2f}s)"
            )
            
            # Sammle Metriken
            self.processing_metrics['processing_steps'].append({
                'layer': 'Gold',
                'views': list(self.gold_layer.keys()),
                'processing_time': processing_time
            })
            
        except Exception as e:
            self.logger.error(f"Error processing Gold Layer: {str(e)}")
            raise

def display_gold_layer_views(pipeline):
        """Zeigt detaillierte Ansichten der Gold Layer Views"""
        st.header("🌟 Gold Layer Views")
        
        tab1, tab2 = st.tabs(["📊 Sales Metrics", "📦 Inventory Status"])
        
        with tab1:
            if 'sales_metrics' in pipeline.gold_layer:
                st.subheader("Sales Metrics by Department")
                
                # Get sales metrics data
                sales_metrics = pipeline.gold_layer['sales_metrics']
                
                # Display metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sales metrics table
                    st.dataframe(
                        sales_metrics.style.format({
                            'total_sales': '€{:,.2f}',
                            'order_count': '{:,}'
                        }),
                        use_container_width=True
                    )
                
                with col2:
                    # Sales distribution chart
                    fig = px.pie(
                        sales_metrics,
                        values='total_sales',
                        names='department',
                        title='Sales Distribution by Department'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Orders by department
                fig = px.bar(
                    sales_metrics,
                    x='department',
                    y=['order_count', 'total_sales'],
                    title='Orders and Sales by Department',
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary metrics
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    st.metric(
                        "Total Sales",
                        f"€{sales_metrics['total_sales'].sum():,.2f}"
                    )
                with metrics_col2:
                    st.metric(
                        "Total Orders",
                        f"{sales_metrics['order_count'].sum():,}"
                    )
                with metrics_col3:
                    st.metric(
                        "Average Order Value",
                        f"€{sales_metrics['total_sales'].sum() / sales_metrics['order_count'].sum():,.2f}"
                    )
        
        with tab2:
            if 'inventory_status' in pipeline.gold_layer:
                st.subheader("Inventory Status Overview")
                
                inventory_status = pipeline.gold_layer['inventory_status']
                
                # Filters
                col1, col2 = st.columns(2)
                with col1:
                    selected_categories = st.multiselect(
                        "Filter by Category",
                        options=inventory_status['category'].unique(),
                        default=inventory_status['category'].unique()
                    )
                
                filtered_inventory = inventory_status[
                    inventory_status['category'].isin(selected_categories)
                ]
                
                # Inventory metrics
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    st.metric(
                        "Total Stock",
                        f"{filtered_inventory['quantity'].sum():,}"
                    )
                with metrics_col2:
                    st.metric(
                        "Products",
                        f"{len(filtered_inventory):,}"
                    )
                with metrics_col3:
                    st.metric(
                        "Categories",
                        f"{len(filtered_inventory['category'].unique())}"
                    )
                
                # Stock by category
                fig = px.bar(
                    filtered_inventory.groupby('category')['quantity'].sum().reset_index(),
                    x='category',
                    y='quantity',
                    title='Stock by Category'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top products
                st.subheader("Top 10 Products by Stock Level")
                top_products = filtered_inventory.nlargest(10, 'quantity')
                fig = px.bar(
                    top_products,
                    x='name',
                    y='quantity',
                    color='category',
                    title='Top 10 Products by Stock Level'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed inventory table
                st.subheader("Detailed Inventory Status")
                st.dataframe(
                    filtered_inventory.style.format({
                        'quantity': '{:,}',
                        'transaction_date': lambda x: x.strftime('%Y-%m-%d %H:%M')
                    }),
                    use_container_width=True
                )

def run_pipeline(data, progress_bar, status_text):
    """Führt die komplette Pipeline aus"""
    # Logging Setup
    logger = logging.getLogger('pipeline_logger')
    logger.handlers = []  # Clear existing handlers
    log_placeholder = st.empty()
    handler = StreamlitHandler(log_placeholder)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    pipeline = DataPipeline(logger)
    
    # Bronze Layer
    status_text.text("Verarbeite Bronze Layer...")
    progress_bar.progress(0)
    
    # Künstliche Verzögerung für Bronze Layer
    for source, df in data.items():
        time.sleep(1)  # 1 Sekunde Verzögerung pro Quelle
        pipeline.process_to_bronze({source: df})
        progress_value = min(33, (list(data.keys()).index(source) + 1) / len(data) * 33)
        progress_bar.progress(int(progress_value))
    
    # Silver Layer
    status_text.text("Verarbeite Silver Layer...")
    time.sleep(2)  # 2 Sekunden Verzögerung für Silver Layer
    pipeline.process_to_silver()
    progress_bar.progress(66)
    
    # Gold Layer
    status_text.text("Verarbeite Gold Layer...")
    time.sleep(2)  # 2 Sekunden Verzögerung für Gold Layer
    pipeline.process_to_gold()
    progress_bar.progress(100)
    
    status_text.text("Pipeline abgeschlossen!")
    
    return pipeline

def display_pipeline_metrics(pipeline):
    """Zeigt detaillierte Metriken der Pipeline"""
    st.header("📊 Pipeline Metriken")
    
    # Layer Statistiken
    col1, col2, col3 = st.columns(3)
    
    # Bronze Metriken
    with col1:
        st.subheader("Bronze Layer")
        total_bronze = sum(len(data['data']) for data in pipeline.bronze_layer.values())
        st.metric("Gesamt Records", f"{total_bronze:,}")
        
    # Silver Metriken
    with col2:
        st.subheader("Silver Layer")
        total_silver = sum(len(data['data']) for data in pipeline.silver_layer.values())
        total_invalid = sum(len(data.get('invalid_records', [])) for data in pipeline.silver_layer.values())
        st.metric("Valide Records", f"{total_silver:,}")
        st.metric("Invalide Records", f"{total_invalid:,}")
    
    # Gold Metriken
    with col3:
        st.subheader("Gold Layer")
        for view_name, view_data in pipeline.gold_layer.items():
            st.metric(f"{view_name}", f"{len(view_data):,} Einträge")
    
    # Verarbeitungszeiten
    st.subheader("⏱️ Verarbeitungszeiten")
    processing_df = pd.DataFrame(pipeline.processing_metrics['processing_steps'])
    
    fig = px.bar(
        processing_df,
        x='layer',
        y='processing_time',
        color='source' if 'source' in processing_df.columns else None,
        title='Verarbeitungszeit pro Layer'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Datenqualität im Silver Layer
    st.subheader("🔍 Datenqualität (Silver Layer)")
    quality_data = []
    for source, data in pipeline.silver_layer.items():
        quality_data.append({
            'Quelle': source,
            'Validierungsrate': data['metadata']['validation_rate'],
            'Valide Records': data['metadata']['valid_records'],
            'Invalide Records': data['metadata']['invalid_records']
        })
    
    quality_df = pd.DataFrame(quality_data)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Valide Records',
        x=quality_df['Quelle'],
        y=quality_df['Valide Records'],
        marker_color='green'
    ))
    fig.add_trace(go.Bar(
        name='Invalide Records',
        x=quality_df['Quelle'],
        y=quality_df['Invalide Records'],
        marker_color='red'
    ))
    
    fig.update_layout(
        barmode='stack',
        title='Datenqualität nach Quelle'
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("🔄 Data Pipeline Monitor")
    
    # Lade Daten
    data = load_data()
    if data is None:
        st.error("❌ Fehler beim Laden der Daten!")
        return
    
    # Pipeline Status
    st.header("Pipeline Status")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        progress_bar = st.progress(0)
        status_text = st.empty()
        if 'pipeline_running' not in st.session_state:
            st.session_state.pipeline_running = False
        
        # Start Pipeline Button
        if st.button("Start Pipeline", disabled=st.session_state.pipeline_running):
            st.session_state.pipeline_running = True
            pipeline = run_pipeline(data, progress_bar, status_text)
            display_pipeline_metrics(pipeline)
            display_gold_layer_views(pipeline)  # Neue Funktion für Gold Layer Views
            st.session_state.pipeline_running = False




if __name__ == "__main__":
    st.set_page_config(page_title="Data Pipeline Monitor", layout="wide")
    main()