import streamlit as st
import pandas as pd
import numpy as np
import io

# --- Seiten-Konfiguration & Corporate Design ---
st.set_page_config(
    page_title="Wärmepumpen-Bivalenzpunkt-Rechner", 
    page_icon="🔥", 
    layout="wide"
)

# Eigene CSS-Anpassungen mit dem Farbcode #4bb6c4
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    h1 {
        color: #111111;
    }
    h2, h3 {
        color: #4bb6c4 !important;
    }
    .stButton>button {
        background-color: #4bb6c4;
        color: white;
        border-radius: 5px;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #3aa2af;
        color: white;
    }
    [data-testid="stMetricValue"] {
        color: #4bb6c4;
    }
    </style>
""", unsafe_allow_html=True)

# --- Kopfbereich mit Logo und Titel ---
col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("https://www.es-ww.de/wp-content/uploads/2023/02/Logo_ESW_farbig-2048x546.png", width=280)

with col_title:
    st.title("Wärmepumpen-Konfigurator & Bivalenzpunkt-Rechner")
    st.markdown("*Interaktive Auslegung, Baureihen-Wahl und Begrenzung des Bivalenzpunkts auf -4°C bis -9°C*")
    st.markdown("*Ersetzt keine Heizlastberechnung nach Norm 12831*")

st.markdown("---")

# --- Artikelstamm / Artikelnummern-Datenbank ---
ARTIKEL_DB = {
    # Wärmepumpen AHPA
    "AHPA 412": {"artnr": "9526560", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 412"},
    "AHPA 413": {"artnr": "9526660", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 413"},
    "AHPA 618": {"artnr": "9526760", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 618"},
    "AHPA 722": {"artnr": "9526860", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 722"},
    "AHPA 1030": {"artnr": "9526960", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 1030"},
    
    # Wärmepumpen AHPC
    "AHPC 27": {"artnr": "9426470", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPC 27"},
    "AHPC 412": {"artnr": "9426570", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPC 412"},
    
    # Pufferspeicher
    "Puffer_300": {"artnr": "8089", "bezeichnung": "Heizwasser-Pufferspeicher 300 Liter"},
    "Puffer_500": {"artnr": "8091", "bezeichnung": "Heizwasser-Pufferspeicher 500 Liter"},
    "Puffer_800": {"artnr": "8093", "bezeichnung": "Heizwasser-Pufferspeicher 800 Liter"},
    "Puffer_1000": {"artnr": "8095", "bezeichnung": "Heizwasser-Pufferspeicher 1000 Liter"},
    
    # Trinkwasserspeicher / FriWa
    "Boiler_300": {"artnr": "8100", "bezeichnung": "Trinkwasserspeicher Hochleistung 300 Liter"},
    "Boiler_400": {"artnr": "8120", "bezeichnung": "Trinkwasserspeicher Hochleistung 400 Liter"},
    "Boiler_500": {"artnr": "8103", "bezeichnung": "Trinkwasserspeicher Hochleistung 500 Liter"},
    "FriWa_Modul": {"artnr": "738113", "bezeichnung": "Frischwassermodul inkl. Pufferspeicher 500 Liter"},
    
    # Ausdehnungsgefäße (MAG)
    "MAG_35": {"artnr": "80631", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 35 Liter"},
    "MAG_50": {"artnr": "80641", "bezeichnung": "Membran-Aus
