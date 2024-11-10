import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Analytics Landscape Assessment",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .main {padding: 0rem 0rem;}
        .css-18e3th9 {padding: 2rem 1rem;}
        .data-card {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 1.5rem;
            margin: 1rem 0;
            background-color: white;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #0066cc;
        }
        .file-header {
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .system-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin: 2px;
        }
        .d365-badge {
            background-color: #e3f2fd;
            color: #1565c0;
        }
        .crm-badge {
            background-color: #f3e5f5;
            color: #7b1fa2;
        }
        .inventory-badge {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
    </style>
""", unsafe_allow_html=True)

# Dictionary mit Informationen über die Datenquellen
DATA_SOURCES = {
    'products.csv': {
        'source': 'Inventory',
        'description': 'Produktstammdaten aus dem Lagerverwaltungssystem',
        'key_fields': ['product_id', 'name', 'category', 'unit_price'],
        'update_frequency': 'Täglich'
    },
    'customers.csv': {
        'source': 'CRM',
        'description': 'Kundenstammdaten aus dem CRM-System',
        'key_fields': ['customer_id', 'company_name', 'contact_name', 'email'],
        'update_frequency': 'Stündlich'
    },
    'sales_orders.csv': {
        'source': 'CRM',
        'description': 'Verkaufsaufträge aus dem CRM-System',
        'key_fields': ['order_id', 'customer_id', 'order_date', 'status'],
        'update_frequency': 'Echtzeit'
    },
    'order_items.csv': {
        'source': 'CRM',
        'description': 'Detaillierte Auftragspositionen aus dem CRM-System',
        'key_fields': ['order_id', 'product_id', 'quantity', 'unit_price'],
        'update_frequency': 'Echtzeit'
    },
    'inventory_transactions.csv': {
        'source': 'Inventory',
        'description': 'Lagerbewegungen aus dem Lagerverwaltungssystem',
        'key_fields': ['transaction_id', 'product_id', 'quantity', 'transaction_date'],
        'update_frequency': 'Echtzeit'
    },
    'financial_transactions.csv': {
        'source': 'D365',
        'description': 'Finanztransaktionen aus D365 Finance',
        'key_fields': ['transaction_id', 'order_id', 'amount', 'payment_date'],
        'update_frequency': 'Täglich'
    }
}

def get_source_badge(source):
    """Erstellt ein HTML-Badge für die Datenquelle"""
    badge_class = {
        'D365': 'd365-badge',
        'CRM': 'crm-badge',
        'Inventory': 'inventory-badge'
    }.get(source, '')
    
    return f'<span class="system-badge {badge_class}">{source}</span>'

def load_data_overview():
    """Lädt Übersicht aller CSV Dateien"""
    data_files = {}
    data_path = "data"
    
    try:
        for file in os.listdir(data_path):
            if file.endswith('.csv'):
                file_path = os.path.join(data_path, file)
                df = pd.read_csv(file_path)
                data_files[file] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'size': round(os.path.getsize(file_path) / (1024 * 1024), 2),  # Size in MB
                    'preview': df.head(3),
                    'column_list': list(df.columns),
                    'source_info': DATA_SOURCES.get(file, {})
                }
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {str(e)}")
        return None
    
    return data_files

def main():
    # Header
    st.title("📊 Analytics Landscape Assessment")
    
    # System-Überblick
    st.markdown("""
    Diese Anwendung analysiert die Datenlandschaft eines Unternehmens mit mehreren Systemen:
    
    <div style="margin: 20px 0;">
        <span class="system-badge d365-badge">D365 Finance and Operations</span>
        <span class="system-badge crm-badge">CRM System</span>
        <span class="system-badge inventory-badge">Inventory Management System</span>
    </div>
    """, unsafe_allow_html=True)
    
    # System-Architektur
    st.subheader("🏗️ System-Architektur")
    st.markdown("""
    <div class="data-card">
        <h4>Datenfluss zwischen Systemen</h4>
        <ul>
            <li><strong>D365 Finance:</strong> Zentrales ERP-System für Finanzbuchhaltung und Controlling</li>
            <li><strong>CRM-System:</strong> Verwaltung von Kundenbeziehungen und Verkaufsprozessen</li>
            <li><strong>Inventory Management:</strong> Lagerverwaltung und Bestandsführung</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Datenübersicht
    st.header("🗃️ Verfügbare Datensätze")
    data_files = load_data_overview()
    
    if data_files:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Zusammenfassung
            st.markdown("""
            <div class="data-card">
                <h3>📑 Datensatz-Übersicht</h3>
            """, unsafe_allow_html=True)
            
            total_rows = sum(file_info['rows'] for file_info in data_files.values())
            total_size = sum(file_info['size'] for file_info in data_files.values())
            
            st.markdown(f"""
                <p>Anzahl Dateien: <span class="metric-value">{len(data_files)}</span></p>
                <p>Gesamtzeilen: <span class="metric-value">{total_rows:,}</span></p>
                <p>Gesamtgröße: <span class="metric-value">{total_size:.2f} MB</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            # System-Verteilung
            st.markdown("""
            <div class="data-card">
                <h3>🔄 Datenverteilung nach System</h3>
            """, unsafe_allow_html=True)
            
            system_counts = {
                'D365': len([f for f in data_files if data_files[f]['source_info'].get('source') == 'D365']),
                'CRM': len([f for f in data_files if data_files[f]['source_info'].get('source') == 'CRM']),
                'Inventory': len([f for f in data_files if data_files[f]['source_info'].get('source') == 'Inventory'])
            }
            
            for system, count in system_counts.items():
                st.markdown(f"""
                    {get_source_badge(system)} <span class="metric-value">{count}</span> Dateien
                    <br>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Detaillierte Dateiinformationen
            for file_name, file_info in data_files.items():
                with st.expander(f"📄 {file_name}"):
                    source_info = file_info['source_info']
                    st.markdown(f"""
                    <div class="file-header">
                        {get_source_badge(source_info.get('source', 'Unbekannt'))}
                        <p><strong>Beschreibung:</strong> {source_info.get('description', 'Keine Beschreibung verfügbar')}</p>
                        <p><strong>Aktualisierung:</strong> {source_info.get('update_frequency', 'Unbekannt')}</p>
                        <p>Zeilen: {file_info['rows']:,}</p>
                        <p>Spalten: {file_info['columns']}</p>
                        <p>Größe: {file_info['size']} MB</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    tabs = st.tabs(["Vorschau", "Spalten", "Schlüsselfelder"])
                    
                    with tabs[0]:
                        st.dataframe(file_info['preview'])
                    
                    with tabs[1]:
                        st.write("Verfügbare Spalten:")
                        for col in file_info['column_list']:
                            st.markdown(f"- `{col}`")
                            
                    with tabs[2]:
                        st.write("Schlüsselfelder:")
                        for field in source_info.get('key_fields', []):
                            st.markdown(f"- `{field}`")

if __name__ == "__main__":
    main()