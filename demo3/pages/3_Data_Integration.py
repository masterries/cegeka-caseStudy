# pages/5_Technical_Requirements_Ingestion.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import os

def mermaid_star_schema():
    components.html(
        """
        <pre class="mermaid">
erDiagram
    SALES_FACTS {
        int order_id PK
        int customer_id FK
        int product_id FK
        int quantity
        float total_amount
        date order_date FK
        string status "e.g., 'Pending' or 'Completed'"
    }

    INVENTORY_FACTS {
        int transaction_id PK
        int product_id FK
        int location_id FK
        int quantity
        date transaction_date
    }

    CUSTOMER_DIMENSION {
        int customer_id PK
        string customer_name
        string region
        date customer_since
    }

    PRODUCT_DIMENSION {
        int product_id PK
        string product_name
        string category
        float price
    }

    DATE_DIMENSION {
        date date_key PK
        int year
        int month
        int day
    }

    LOCATION_DIMENSION {
        int location_id PK
        string location_name
        string region
    }

    SALES_FACTS }o--|| CUSTOMER_DIMENSION : "customer_id"
    SALES_FACTS }o--|| PRODUCT_DIMENSION : "product_id"
    SALES_FACTS }o--|| DATE_DIMENSION : "order_date"
    
    INVENTORY_FACTS }o--|| PRODUCT_DIMENSION : "product_id"
    INVENTORY_FACTS }o--|| LOCATION_DIMENSION : "location_id"
    INVENTORY_FACTS }o--|| DATE_DIMENSION : "transaction_date"

        </pre>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
        </script>
        """,
        height=600,
    )










def load_data():
    """Lade Daten aus CSV-Dateien im data Verzeichnis"""
    data = {}
    data_dir = 'data'
    csv_files = [
        'products.csv',
        'customers.csv',
        'sales_orders.csv',
        'order_items.csv',
        'inventory_transactions.csv',
        'financial_transactions.csv'
    ]
    
    for file in csv_files:
        name = file.replace('.csv', '')
        file_path = os.path.join(data_dir, file)
        try:
            data[name] = pd.read_csv(file_path)
            
            # Konvertiere Datumsspalten
            date_columns = [col for col in data[name].columns if 'date' in col.lower()]
            for date_col in date_columns:
                data[name][date_col] = pd.to_datetime(data[name][date_col])
                
        except FileNotFoundError:
            st.error(f"❌ Datei {file_path} nicht gefunden!")
            return None
        except Exception as e:
            st.error(f"❌ Fehler beim Laden von {file_path}: {str(e)}")
            return None
    
    return data

def analyze_data_volumes(data):
    """Analysiere Datenvolumen pro System"""
    volumes = pd.DataFrame([
        {
            'System': 'D365 F&O',
            'Transaktionen': len(data['financial_transactions']),
            'Datensätze/Tag': len(data['financial_transactions']) / len(data['financial_transactions']['invoice_date'].dt.date.unique())
        },
        {
            'System': 'CRM',
            'Transaktionen': len(data['sales_orders']),
            'Datensätze/Tag': len(data['sales_orders']) / len(data['sales_orders']['order_date'].dt.date.unique())
        },
        {
            'System': 'Inventory',
            'Transaktionen': len(data['inventory_transactions']),
            'Datensätze/Tag': len(data['inventory_transactions']) / len(data['inventory_transactions']['transaction_date'].dt.date.unique())
        }
    ])
    return volumes

def analyze_data_quality(data):
    """Analysiere Datenqualität der Systeme"""
    quality_metrics = pd.DataFrame({
        'Metrik': ['Vollständigkeit', 'Konsistenz', 'Aktualität', 'Genauigkeit'],
        'D365': [
            100 * (1 - data['financial_transactions'].isnull().mean().mean()),
            95,  # Beispielwert für Konsistenz
            100 * (data['financial_transactions']['payment_date'] <= data['financial_transactions']['due_date']).mean(),
            98  # Beispielwert für Genauigkeit
        ],
        'CRM': [
            100 * (1 - data['sales_orders'].isnull().mean().mean()),
            92,  # Beispielwert für Konsistenz
            90,  # Beispielwert für Aktualität
            94  # Beispielwert für Genauigkeit
        ],
        'Inventory': [
            100 * (1 - data['inventory_transactions'].isnull().mean().mean()),
            97,  # Beispielwert für Konsistenz
            99,  # Beispielwert für Aktualität
            98  # Beispielwert für Genauigkeit
        ]
    })
    return quality_metrics

def display_lineage_mermaid():
    components.html(
        """
        <pre class="mermaid">
            flowchart LR
                sales_orders.csv -->|Load| BronzeLayer[Bronze Layer - sales_orders_bronze]
                inventory_transactions.csv -->|Load| BronzeLayer2[Bronze Layer - inventory_bronze]
                
                BronzeLayer -->|Clean and validate| SilverLayer[Silver Layer - sales_orders_silver]
                BronzeLayer2 -->|Validate and join| SilverLayer2[Silver Layer - inventory_silver]
                
                SilverLayer -->|Aggregate| GoldLayer[Gold Layer - sales_facts]
                SilverLayer2 -->|Aggregate| GoldLayer2[Gold Layer - inventory_facts]
        </pre>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({ startOnLoad: true, theme: 'light' });
        </script>
        """,
        height=400,
    )


def mermaid(code: str) -> None:
    components.html(
        f"""
        <pre class="mermaid">
            {code}
        </pre>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'light' }});
        </script>
        """,
        height=800,
    )

def display_ingestion_requirements(data):
    st.title("🔄 Data Ingestion Konzept")
    
    st.markdown("""
    ### Übersicht der Datenquellen und Anforderungen
    
    Basierend auf der Analyse der vorhandenen Daten wird im Folgenden das Konzept für die 
    Integration der verschiedenen Quellsysteme in eine zentrale Datenhaltung vorgestellt.
    """)
    
    # System Architecture Diagram
    st.subheader("📐 System Architektur")
    mermaid("""
graph TD
    subgraph Sources[Quellsysteme]
        D365[D365 F&O] --> IL1[Ingestion Layer]
        CRM[CRM System] --> IL2[Ingestion Layer]
        INV[Inventory System] --> IL3[Ingestion Layer]
    end
    
    subgraph BronzeLayer[Bronze Layer - Rohdaten]
        IL1 --> B1[Bronze D365]
        IL2 --> B2[Bronze CRM]
        IL3 --> B3[Bronze Inventory]
    end
    
    subgraph Processing[Validierung & Verarbeitung]
        B1 --> V1[Validierung]
        B2 --> V2[Validierung]
        B3 --> V3[Validierung]
        V1 --> DL[Delta Load]
        V2 --> DL
        V3 --> DL
    end
    
    subgraph RefinedLayers[Veredelte Daten]
        DL --> S[Silver Layer]
        S --> G[Gold Layer]
    end

        
        classDef source fill:#ff9999,stroke:#ff0000
        classDef process fill:#99ff99,stroke:#00ff00
        classDef storage fill:#9999ff,stroke:#0000ff
        
        class D365,CRM,INV source
        class IL1,IL2,IL3,V1,V2,V3,DL process
        class B,S,G storage
    """)

if __name__ == "__main__":
    st.set_page_config(page_title="Technical Requirements - Data Ingestion", layout="wide")
    
    # Lade Daten
    data = load_data()

    
    if data is not None:
        display_ingestion_requirements(data)
        mermaid_star_schema()
        display_lineage_mermaid()
    else:
        st.error("X")