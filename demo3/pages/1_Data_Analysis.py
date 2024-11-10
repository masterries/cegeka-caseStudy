import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os

def load_data():
    """Lade Daten aus CSV-Dateien im data Verzeichnis"""
    data = {}
    data_dir = 'data'  # Definiere das Datenverzeichnis
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
        file_path = os.path.join(data_dir, file)  # Erstelle den vollständigen Dateipfad
        try:
            data[name] = pd.read_csv(file_path)  # Lade CSV mit vollständigem Pfad
            
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
    
    # Berechne Gesamtbetrag für Verkaufsaufträge falls nicht vorhanden
    if 'sales_orders' in data and 'order_items' in data:
        if 'total_amount' not in data['sales_orders'].columns:
            order_totals = data['order_items'].groupby('order_id')['line_total'].sum().reset_index()
            data['sales_orders'] = data['sales_orders'].merge(
                order_totals,
                on='order_id',
                how='left'
            ).rename(columns={'line_total': 'total_amount'})
    
    return data

def display_data_inconsistency_challenge(data):
    """Zeigt Beispiele für Dateninkonsistenzen mit detaillierten Erklärungen"""
    st.subheader("🚨 Challenge 1: Dateninkonsistenz zwischen Systemen")
    
    # Tabs für verschiedene Ansichten
    tab1, tab2 = st.tabs(["📊 Systemvergleich", "📋 Beispiele & Erklärungen"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Berechne die Summen
            order_items_total = data['order_items']['line_total'].sum()
            financial_total = data['financial_transactions']['amount'].sum()
            
            diff_percentage = abs(order_items_total - financial_total) / order_items_total * 100
            
            st.markdown(f"""
            <div class="challenge-card">
                <h4>System Diskrepanzen</h4>
                <p>Verkaufsaufträge Total: €{order_items_total:,.2f}</p>
                <p>Finanztransaktionen Total: €{financial_total:,.2f}</p>
                <p>Abweichung: {diff_percentage:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Visualisierung der monatlichen Diskrepanzen
            monthly_sales = data['order_items'].copy()
            monthly_sales = monthly_sales.merge(
                data['sales_orders'][['order_id', 'order_date']],
                on='order_id'
            )
            monthly_sales['month'] = pd.to_datetime(monthly_sales['order_date']).dt.strftime('%Y-%m')
            monthly_sales = monthly_sales.groupby('month')['line_total'].sum().reset_index()
            
            monthly_finance = data['financial_transactions'].copy()
            monthly_finance['month'] = monthly_finance['invoice_date'].dt.strftime('%Y-%m')
            monthly_finance = monthly_finance.groupby('month')['amount'].sum().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly_sales['month'],
                y=monthly_sales['line_total'],
                name='Verkaufssystem',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=monthly_finance['month'],
                y=monthly_finance['amount'],
                name='Finanzsystem',
                line=dict(color='red')
            ))
            fig.update_layout(
                title='Monatliche Umsätze: Systemvergleich',
                xaxis_title='Monat',
                yaxis_title='Betrag (€)'
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Beispiele für Diskrepanzen
        st.markdown("""
        <style>
        .discrepancy-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            background-color: white;
        }
        .discrepancy-header {
            color: #2c3e50;
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        .example-box {
            background-color: #f8f9fa;
            border-left: 3px solid #0066cc;
            padding: 10px;
            margin-top: 5px;
        }
        .system-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            margin-right: 5px;
            font-size: 0.8em;
        }
        .crm-tag {
            background-color: #e3f2fd;
            color: #1565c0;
        }
        .finance-tag {
            background-color: #fbe9e7;
            color: #d84315;
        }
        .inventory-tag {
            background-color: #f1f8e9;
            color: #558b2f;
        }
        </style>
        """, unsafe_allow_html=True)

        # Zeitliche Unterschiede
        with st.expander("⏰ Zeitliche Unterschiede", expanded=True):
            st.markdown("""
            <div class="discrepancy-card">
                <div class="discrepancy-header">Buchungszeitpunkt-Unterschiede</div>
                <p>Ein einzelner Geschäftsvorfall wird in verschiedenen Systemen zu unterschiedlichen Zeitpunkten erfasst:</p>
                <div class="example-box">
                    <span class="system-tag crm-tag">CRM</span> Auftrag am 31.03: €1,000<br>
                    <span class="system-tag inventory-tag">Lager</span> Warenausgang am 02.04<br>
                    <span class="system-tag finance-tag">Finanzen</span> Rechnung am 05.04<br>
                    <small>→ Führt zu unterschiedlichen Monatssummen</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Stornierungen
        with st.expander("🔄 Stornierungen und Korrekturen"):
            st.markdown("""
            <div class="discrepancy-card">
                <div class="discrepancy-header">Unterschiedliche Stornologik</div>
                <p>Systeme behandeln Stornierungen und Korrekturen unterschiedlich:</p>
                <div class="example-box">
                    <span class="system-tag crm-tag">CRM</span> Auftrag wird gelöscht<br>
                    <span class="system-tag finance-tag">Finanzen</span> Stornobuchung -€1,000<br>
                    <span class="system-tag inventory-tag">Lager</span> Neue Retouren-Bewegung<br>
                    <small>→ Temporäre oder dauerhafte Inkonsistenz in Auswertungen</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Rabatte und Konditionen
        with st.expander("💰 Rabatte und Sonderkonditionen"):
            st.markdown("""
            <div class="discrepancy-card">
                <div class="discrepancy-header">Komplexe Preisberechnungen</div>
                <p>Verschiedene Rabattarten und deren Berechnung:</p>
                <div class="example-box">
                    Ausgangsbetrag: €1,000<br>
                    <span class="system-tag crm-tag">CRM</span> 10% Kundenrabatt = €900<br>
                    <span class="system-tag finance-tag">Finanzen</span> €900 + 19% MwSt - 2% Skonto = €1,052.82<br>
                    <small>→ Unterschiedliche Endbeträge je nach Berechnungslogik</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Rundungen
        with st.expander("🔢 Rundungen und Berechnungen"):
            st.markdown("""
            <div class="discrepancy-card">
                <div class="discrepancy-header">Rundungsdifferenzen</div>
                <p>Unterschiedliche Rundungsmethoden führen zu Abweichungen:</p>
                <div class="example-box">
                    Position 1: €10.666<br>
                    Position 2: €20.666<br>
                    <span class="system-tag crm-tag">CRM</span> (10.67 + 20.67) = €31.34<br>
                    <span class="system-tag finance-tag">Finanzen</span> (10.666 + 20.666) = €31.33<br>
                    <small>→ Rundungsdifferenzen akkumulieren sich</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Währungsumrechnungen
        with st.expander("💱 Währungsumrechnungen"):
            st.markdown("""
            <div class="discrepancy-card">
                <div class="discrepancy-header">Kursunterschiede</div>
                <p>Unterschiedliche Wechselkurse zu verschiedenen Zeitpunkten:</p>
                <div class="example-box">
                    Auftrag: 1,000 USD = €920 (Kurs 0.92)<br>
                    <span class="system-tag crm-tag">CRM</span> €920 (Auftragsdatum)<br>
                    <span class="system-tag finance-tag">Finanzen</span> €930 (Rechnungsdatum)<br>
                    <span class="system-tag finance-tag">Zahlung</span> €910 (Zahlungseingang)<br>
                    <small>→ Verschiedene EUR-Beträge in den Systemen</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_manual_effort_challenge(data):
    """Zeigt die Herausforderungen durch manuelle Bearbeitung"""
    st.subheader("⏰ Challenge 2: Zeitaufwand durch manuelle Prozesse")
    
    col1, col2 = st.columns(2)
    
    with col1:
        processing_times = pd.DataFrame({
            'Prozess': ['Datenexport', 'Datenbereinigung', 'Datenzusammenführung', 
                       'Berichterstellung', 'Qualitätskontrolle'],
            'Zeit (Stunden)': [2, 3, 4, 3, 2]
        })
        
        fig = px.bar(
            processing_times,
            x='Prozess',
            y='Zeit (Stunden)',
            title='Zeitaufwand pro Berichtserstellung'
        )
        fig.update_traces(marker_color='#ff4b4b')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="challenge-card">
            <h4>Auswirkungen manueller Prozesse</h4>
            <ul>
                <li>14 Stunden Gesamtaufwand pro Bericht</li>
                <li>Hohe Fehleranfälligkeit</li>
                <li>Verzögerte Entscheidungsfindung</li>
                <li>Gebundene Ressourcen für Routineaufgaben</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_accessibility_challenge(data):
    """Visualisiert Probleme mit der Datenzugänglichkeit"""
    st.subheader("🔒 Challenge 3: Eingeschränkte Datenzugänglichkeit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Analyse der Datenzugriffe nach Abteilung
        departments = data['customers']['department'].unique()
        access_data = pd.DataFrame({
            'Abteilung': departments,
            'Zugriff auf Verkaufsdaten': [100 if d == 'Vertrieb' else np.random.randint(20, 60) for d in departments],
            'Zugriff auf Finanzdaten': [100 if d == 'Finanzen' else np.random.randint(10, 40) for d in departments],
            'Zugriff auf Lagerdaten': [100 if d == 'Produktion' else np.random.randint(30, 70) for d in departments]
        })
        
        fig = px.imshow(
            access_data.iloc[:, 1:].values,
            labels=dict(x='Datenkategorie', y='Abteilung'),
            x=['Verkauf', 'Finanzen', 'Lager'],
            y=access_data['Abteilung'],
            color_continuous_scale='Reds',
            title='Datenzugriff nach Abteilung (%)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="challenge-card">
            <h4>Probleme der Datenzugänglichkeit</h4>
            <ul>
                <li>Datensilos zwischen Abteilungen</li>
                <li>Inkonsistente Zugriffsrechte</li>
                <li>Verzögerte Informationsweitergabe</li>
                <li>Fehlende zentrale Datenverwaltung</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_data_quality_challenge(data):
    """Zeigt Probleme mit der Datenqualität"""
    st.subheader("📊 Challenge 4: Datenqualitätsprobleme")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Berechne echte Datenqualitätsmetriken
        total_orders = len(data['sales_orders'])
        orders_with_items = len(data['order_items']['order_id'].unique())
        completeness = (orders_with_items / total_orders * 100) if total_orders > 0 else 0
        
        # Berechne Konsistenz zwischen Systemen
        sales_total = data['order_items']['line_total'].sum()
        finance_total = data['financial_transactions']['amount'].sum()
        consistency = (min(sales_total, finance_total) / max(sales_total, finance_total) * 100)
        
        quality_metrics = pd.DataFrame({
            'Metrik': ['Vollständigkeit', 'Konsistenz', 'Aktualität', 'Genauigkeit'],
            'Score': [completeness, consistency, 75, 80]  # Letzte zwei sind Beispielwerte
        })
        
        fig = px.bar(
            quality_metrics,
            x='Metrik',
            y='Score',
            title='Datenqualitäts-Scores (%)'
        )
        fig.update_traces(marker_color='#ff4b4b')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        <div class="challenge-card">
            <h4>Identifizierte Datenqualitätsprobleme</h4>
            <ul>
                <li>Nur {completeness:.1f}% der Aufträge haben vollständige Daten</li>
                <li>{abs(100-consistency):.1f}% Abweichung zwischen Systemen (Verkauf und Finanz)</li>
                <li>Unterschiedliche Datumsformate in Systemen</li>
                <li>Fehlende Standardisierung von Bezeichnungen</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def main():
    # Seitenkonfiguration
    st.set_page_config(page_title="Analytics Landscape Challenges", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
            .main {padding: 0rem 0rem;}
            .stAlert {padding: 0.5rem; margin: 0.5rem 0;}
            .challenge-card {
                border-left: 4px solid #ff4b4b;
                padding: 1rem;
                margin: 1rem 0;
                background-color: #f8f9fa;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📈 Analytics Landscape Assessment")
    st.markdown("""
    Diese Analyse zeigt die wichtigsten Herausforderungen im aktuellen Analytics-Setup,
    basierend auf Daten aus D365 F&O, CRM und dem Inventory Management System.
    """)
    
    # Lade Daten
    data = load_data()
    
    if data is None:
        st.error("Fehler beim Laden der Daten. Bitte stelle sicher, dass alle CSV-Dateien vorhanden sind.")
        return
    
    # Debug-Information
    if st.checkbox("Debug-Informationen anzeigen"):
        for key, df in data.items():
            st.write(f"Datensatz: {key}")
            st.write("Spalten:", df.columns.tolist())
            st.write("Erste Zeilen:")
            st.write(df.head())
            st.write("---")
    
    # Zeige die verschiedenen Herausforderungen
    display_data_inconsistency_challenge(data)
    display_manual_effort_challenge(data)
    display_accessibility_challenge(data)
    display_data_quality_challenge(data)

if __name__ == "__main__":
    main()