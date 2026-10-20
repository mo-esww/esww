import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Wärmepumpen-Bivalenzpunkt-Rechner", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    h1 { color: #111111; }
    h2, h3 { color: #4bb6c4 !important; }
    .stButton>button { background-color: #4bb6c4; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #3aa2af; color: white; }
    [data-testid="stMetricValue"] { color: #4bb6c4; }
    </style>
""", unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("https://www.es-ww.de/wp-content/uploads/2023/02/Logo_ESW_farbig-2048x546.png", width=280)

with col_title:
    st.title("Wärmepumpen-Konfigurator & Bivalenzpunkt-Rechner")
    st.markdown("*Interaktive Auslegung, Baureihen-Wahl und Begrenzung des Bivalenzpunkts auf -4°C bis -9°C*")
    st.markdown("*Ersetzt keine Heizlastberechnung nach Norm 12831*")

st.markdown("---")

ARTIKEL_DB = {
    "AHPA 412": {"artnr": "9526560", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 412"},
    "AHPA 413": {"artnr": "9526660", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 413"},
    "AHPA 618": {"artnr": "9526760", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 618"},
    "AHPA 722": {"artnr": "9526860", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 722"},
    "AHPA 1030": {"artnr": "9526960", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPA 1030"},
    "AHPC 27": {"artnr": "9426470", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPC 27"},
    "AHPC 412": {"artnr": "9426570", "bezeichnung": "Luft/Wasser-Wärmepumpe AHPC 412"},
    "Puffer_300": {"artnr": "8089", "bezeichnung": "Heizwasser-Pufferspeicher 300 Liter"},
    "Puffer_500": {"artnr": "8091", "bezeichnung": "Heizwasser-Pufferspeicher 500 Liter"},
    "Puffer_800": {"artnr": "8093", "bezeichnung": "Heizwasser-Pufferspeicher 800 Liter"},
    "Puffer_1000": {"artnr": "8095", "bezeichnung": "Heizwasser-Pufferspeicher 1000 Liter"},
    "Boiler_300": {"artnr": "8100", "bezeichnung": "Trinkwasserspeicher Hochleistung 300 Liter"},
    "Boiler_400": {"artnr": "8120", "bezeichnung": "Trinkwasserspeicher Hochleistung 400 Liter"},
    "Boiler_500": {"artnr": "8103", "bezeichnung": "Trinkwasserspeicher Hochleistung 500 Liter"},
    "FriWa_Modul": {"artnr": "738113", "bezeichnung": "Frischwassermodul inkl. Pufferspeicher 500 Liter"},
    "MAG_35": {"artnr": "80631", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 35 Liter"},
    "MAG_50": {"artnr": "80641", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 50 Liter"},
    "MAG_80": {"artnr": "8065", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 80 Liter"}
}

x_vals = list(range(-18, 23, 2))

kennlinien_db_ahpa = {
    "AHPA 412": {
        35: [6.2, 6.6, 7.0, 7.4, 7.8, 8.2, 8.6, 9.1, 9.6, 10.1, 10.6, 11.1, 11.6, 12.1, 12.7, 13.3, 13.9, 14.5, 15.1, 15.6, 16.0],
        55: [6.1, 6.4, 6.7, 7.0, 7.3, 7.6, 7.9, 8.3, 8.7, 9.1, 9.5, 9.9, 10.3, 10.8, 11.3, 11.8, 12.3, 12.8, 13.4, 14.0, 14.5]
    },
    "AHPA 413": {
        35: [7.2, 7.7, 8.2, 8.7, 9.1, 9.6, 10.1, 10.7, 11.2, 11.7, 12.2, 12.8, 13.5, 14.4, 15.2, 16.0, 16.8, 17.6, 18.2, 18.7, 18.7],
        55: [7.0, 7.4, 7.8, 8.2, 8.6, 9.1, 9.6, 10.1, 10.7, 11.2, 11.7, 12.3, 12.9, 13.5, 14.2, 15.0, 15.8, 16.4, 17.0, 17.0, 17.2]
    },
    "AHPA 618": {
        35: [10.5, 11.0, 11.6, 12.2, 12.8, 13.5, 14.3, 15.1, 15.9, 16.7, 17.5, 18.3, 19.1, 20.0, 20.9, 21.8, 22.7, 23.6, 24.5, 25.4, 26.4],
        55: [10.4, 10.8, 11.3, 11.8, 12.3, 12.9, 13.5, 14.2, 14.9, 15.6, 16.3, 17.0, 17.7, 18.5, 19.3, 20.1, 20.9, 21.7, 22.5, 23.3, 24.0]
    },
    "AHPA 722": {
        35: [11.8, 12.5, 13.2, 13.9, 14.6, 15.4, 16.2, 16.5, 16.8, 17.1, 17.5, 19.0, 21.0, 23.2, 25.5, 27.5, 29.5, 31.5, 33.5, 35.5, 37.0],
        55: [10.6, 11.3, 12.0, 12.6, 13.2, 13.8, 14.3, 14.3, 14.4, 14.5, 14.6, 16.0, 18.0, 19.8, 21.6, 23.2, 24.8, 26.4, 28.0, 29.5, 30.8]
    },
    "AHPA 1030
