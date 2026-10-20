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
    "MAG_50": {"artnr": "80641", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 50 Liter"},
    "MAG_80": {"artnr": "8065", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 80 Liter"}
}

# --- Kennlinien-Datenbank für alle Modelle getrennt nach Baureihen ---
x_vals = list(range(-18, 23, 2))

kennlinien_db_ahpa = {
    "AHPA 412": {
        35: [6.2, 6.6, 7.0, 7.4, 7.8, 8.2, 8.6, 9.1, 9.6, 10.1, 10.6, 11.1, 11.6, 12.1, 12.7, 13.3, 13.9, 14.5, 15.1, 15.6, 16.0],
        55: [6.1, 6.4, 6.7, 7.0, 7.3, 7.6, 7.9, 8.3, 8.7, 9.1, 9.5, 9.9, 10.3, 10.8, 11.3, 11.8, 12.3, 12.8, 13.4, 14.0, 14.5]
    },
    "AHPA 413": {
