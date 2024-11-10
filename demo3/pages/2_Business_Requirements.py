# pages/4_Business_Requirements.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

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
        height=600,
    )

def display_comprehensive_analysis():
    st.title("🎯 Business Requirements & Strategische Lösungen")
    
    # Übersichtsdiagramm
    st.markdown("### 📊 Gesamtübersicht")
    st.markdown("Das folgende Diagramm zeigt den Zusammenhang zwischen Herausforderungen, Anforderungen und Zielen:")

    # Mermaid Übersichtsdiagramm
    mermaid("""
    graph TD
        subgraph Challenges[Aktuelle Herausforderungen]
            C1[Dateninkonsistenz] --> R1[Datenintegration]
            C2[Manuelle Prozesse] --> R2[Prozessautomatisierung]
            C3[Fehlende Governance] --> R3[Governance Framework]
        end
        
        subgraph Requirements[Anforderungen]
            R1 --> G1[Datenqualität]
            R2 --> G2[Effizienzsteigerung]
            R3 --> G3[Compliance & Kontrolle]
        end
        
        subgraph Goals[Projektziele]
            G1 --> S1[Phase 1: Analyse]
            G2 --> S2[Phase 2: Implementation]
            G3 --> S3[Phase 3: Optimierung]
        end
        
        classDef challenge fill:#ff9999,stroke:#ff0000
        classDef requirement fill:#99ff99,stroke:#00ff00
        classDef goal fill:#9999ff,stroke:#0000ff
        
        class C1,C2,C3 challenge
        class R1,R2,R3 requirement
        class G1,G2,G3 goal
    """)

    # Prozessfluss
    st.markdown("### 🔄 Prozessfluss der Lösungsimplementierung")
    mermaid("""
    sequenceDiagram
        participant DS as Datenquellen
        participant ETL as ETL Prozesse
        participant DWH as Data Warehouse
        participant BI as BI Layer
        participant User as Endnutzer
        
        DS->>ETL: Rohdaten
        Note over ETL: Validierung & Transformation
        ETL->>DWH: Integrierte Daten
        Note over DWH: Data Modeling
        DWH->>BI: Analytische Daten
        Note over BI: Self-Service Analytics
        BI->>User: Reports & Dashboards
        User->>BI: Feedback
    """)

    # Impact & Solutions Tab
    tab1, tab2 = st.tabs(["💡 Impact & Lösungen", "📈 KPIs & Metriken"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Challenge Impact Matrix
            impact_data = {
                'Challenge': ['Dateninkonsistenz', 'Manuelle Prozesse', 'Fehlende Governance'],
                'Business Impact': [85, 78, 72],
                'Lösungskomplexität': [75, 60, 65]
            }
            df = pd.DataFrame(impact_data)
            
            fig = px.scatter(df, 
                x='Business Impact', 
                y='Lösungskomplexität',
                text='Challenge',
                size=[50, 40, 45],
                title='Impact vs. Komplexität Matrix')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            ### 🎯 Lösungsansätze
            
            #### 1. Datenintegration
            - Zentrales Data Warehouse
            - Automatisierte ETL Prozesse
            - Real-time Synchronisation
            
            #### 2. Prozessautomatisierung
            - Workflow Automation
            - Self-Service Analytics
            - Automatische Validierung
            
            #### 3. Governance
            - Daten-Ownership
            - Qualitätssicherung
            - Compliance-Monitoring
            """)

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # KPI Ziele Diagramm
            mermaid("""
            graph TD
                subgraph Effizienz[Effizienzsteigerung]
                    E1[Zeitersparnis] --> E2[60% Reduktion]
                    E3[Automatisierung] --> E4[80% Prozesse]
                end
                subgraph Qualität[Datenqualität]
                    Q1[Genauigkeit] --> Q2[99% Korrektheit]
                    Q3[Konsistenz] --> Q4[95% Übereinstimmung]
                end
                subgraph Governance[Governance & Compliance]
                    G1[Dokumentation] --> G2[100% Abdeckung]
                    G3[Prozesse] --> G4[90% Standardisierung]
                end
            """)
        
        with col2:
            # Timeline
            timeline_data = pd.DataFrame([
                {'Milestone': 'Datenintegration', 'Start': 0, 'Ende': 3},
                {'Milestone': 'Prozessautomatisierung', 'Start': 2, 'Ende': 6},
                {'Milestone': 'Governance Implementation', 'Start': 4, 'Ende': 9},
                {'Milestone': 'Optimierung', 'Start': 8, 'Ende': 12}
            ])
            
            fig = px.timeline(timeline_data, 
                            x_start='Start', 
                            x_end='Ende', 
                            y='Milestone',
                            title='Projekt Timeline (Monate)')
            st.plotly_chart(fig, use_container_width=True)

    # Governance Structure
    st.markdown("### 🏛️ Governance Struktur")
    mermaid("""
    graph TB
        subgraph Roles[Rollen & Verantwortlichkeiten]
            DO[Data Owner] --> DQ[Data Quality]
            DO --> DP[Data Privacy]
            DS[Data Steward] --> DQ
            DS --> DG[Data Governance]
        end
        
        subgraph Processes[Prozesse]
            DQ --> QM[Quality Monitoring]
            DG --> AM[Access Management]
            DP --> PC[Privacy Controls]
        end
        
        subgraph Tools[Werkzeuge]
            QM --> QT[Quality Tools]
            AM --> AT[Access Tools]
            PC --> PT[Privacy Tools]
        end
        
        classDef roles fill:#ffcccc,stroke:#ff0000
        classDef processes fill:#ccffcc,stroke:#00ff00
        classDef tools fill:#cce5ff,stroke:#0066cc
        
        class DO,DS roles
        class DQ,DG,DP processes
        class QT,AT,PT tools
    """)
if __name__ == "__main__":
    display_comprehensive_analysis()