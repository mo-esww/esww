import streamlit as st
import pandas as pd

# --- Seiten-Konfiguration & Corporate Design ---
st.set_page_config(
    page_title="Wärmepumpen-Konfigurator", 
    page_icon="🔥", 
    layout="centered"
)

# Eigene CSS-Anpassungen mit deinem Farbcode #4bb6c4
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
col_logo, col_title = st.columns([1, 2])
with col_logo:
    st.image("https://www.es-ww.de/wp-content/uploads/2023/02/Logo_ESW_farbig-2048x546.png", width=320)

with col_title:
    st.title("Wärmepumpen-Konfigurator")
    st.markdown("*Überschlägige Heizlast- und Komponenten-Auslegung, ersetzt keine Berechnung nach DIN 12831*")

st.markdown("---")

# --- 1. Eingabemöglichkeit: Modus-Auswahl ---
st.subheader("1. Gebäudedaten & Parameter")

auswahl_modus = st.radio(
    "Wie möchten Sie die Heizlast ermitteln?",
    [
        "1. Über Gebäudestandard & Wohnfläche (Standard)",
        "2. Anhand fossilem Brennstoffverbrauch (Öl / Gas)",
        "3. Direkte Heizlast-Vorgabe (z.B. nach DIN 12831)"
    ]
)

st.markdown("")

# Variablen initialisieren
heizlast_watt = 0.0

# --- Modus 1: Wohnfläche & Baujahr ---
if auswahl_modus.startswith("1."):
    wohnflaeche = st.number_input("Beheizte Wohnfläche (m²)", min_value=20, max_value=1000, value=160, step=10)
    baujahr = st.selectbox("Baujahr / Dämmstandard", [1950, 1970, 1980, 1990, 2000, 2010, 2016])
    
    heizlast_tabelle = {
        1950: 160.0, 1970: 130.0, 1980: 110.0, 1990: 90.0, 2000: 70.0, 2010: 50.0, 2016: 40.0
    }
    spez_heizlast = heizlast_tabelle.get(baujahr, 50.0)
    heizlast_watt = wohnflaeche * spez_heizlast
    personen = st.selectbox("Anzahl Personen im Haushalt", [1, 2, 3, 4, 5, 6, 7])

# --- Modus 2: Fossiler Brennstoffverbrauch ---
elif auswahl_modus.startswith("2."):
    brennstoff_art = st.selectbox("Brennstoffart", ["Heizöl (Liter/Jahr)", "Erdgas (kWh/Jahr)", "Flüssiggas (Liter/Jahr)"])
    verbrauch = st.number_input("Jahresverbrauch", min_value=500, max_value=100000, value=2500, step=100)
    
    # Überschlägige Umrechnung auf Heizlast (inkl. Wirkungsgrad-Annahme alter Kessel ca. 0.8 / 0.85)
    if "Heizöl" in brennstoff_art:
        # 1 Liter Heizöl ~ 10 kWh. Bei altem Kessel ca. 80% Nutzungsgrad -> Jahresarbeit / ~2000 Volllaststunden als Daumenwert
        jaehrliche_waermearbeit = verbrauch * 10 * 0.85
    elif "Erdgas" in brennstoff_art:
        jaehrliche_waermearbeit = verbrauch * 0.85
    else:  # Flüssiggas
        jaehrliche_waermearbeit = verbrauch * 6.5 * 0.85
        
    # Daumenwert-Heizlastabschätzung über Jahresarbeit / 2000 Vollbenutzungsstunden (oder Schweizer Formel)
    heizlast_watt = (jaehrliche_waermearbeit / 2000) * 1000
    personen = st.selectbox("Anzahl Personen im Haushalt", [1, 2, 3, 4, 5, 6, 7])

# --- Modus 3: Direkte Heizlast ---
else:
    heizlast_kw = st.number_input("Vorhandene Heizlast / Vorgabe (kW)", min_value=2.0, max_value=50.0, value=10.0, step=0.5)
    heizlast_watt = heizlast_kw * 1000.0
    personen = st.selectbox("Anzahl Personen im Haushalt", [1, 2, 3, 4, 5, 6, 7])

# Allgemeine Zusatzparameter für alle Modi
systemtemperatur = st.selectbox("Systemtemperatur (°C)", [35, 40, 45, 50, 55])
wp_typ_wahl = st.selectbox("Wärmepumpen-Baureihe", ["AHPA", "AHPC"])
ww_bereitung = st.selectbox("Warmwasserbereitung", ["ja", "nein"])
frischwasser = st.selectbox("Frischwassermodul", ["nein", "ja"])

# --- Berechnungs-Logik (Komponentenauswahl) ---
ww_aufschlag = 2000 if ww_bereitung == "ja" else 0
gesamt_last = heizlast_watt + ww_aufschlag

wp_daten_ahpa = {
    "AHPA 412": {35: 11500, 40: 11125, 45: 10750, 50: 10350, 55: 10000},
    "AHPA 413": {35: 12500, 40: 12375, 45: 12250, 50: 12125, 55: 12000},
    "AHPA 618": {35: 17000, 40: 16750, 45: 16500, 50: 16250, 55: 16000},
    "AHPA 722": {35: 19000, 40: 18500, 45: 18000, 50: 17500, 55: 17000},
    "AHPA 1030": {35: 29500, 40: 28625, 45: 27750, 50: 26875, 55: 26000},
}
wp_daten_ahpc = {
    "AHPC 27": {35: 7500, 40: 7125, 45: 6750, 50: 6375, 55: 6000},
    "AHPC 412": {35: 12500, 40: 12125, 45: 11750, 50: 11375, 55: 11000},
}

aktive_wp_liste = wp_daten_ahpa if wp_typ_wahl == "AHPA" else wp_daten_ahpc
empfohlene_wp = "Keine passende WP gefunden"
for wp_name, leistungen in aktive_wp_liste.items():
    if leistungen.get(systemtemperatur, 0) >= gesamt_last:
        empfohlene_wp = wp_name
        break
if empfohlene_wp == "Keine passende WP gefunden" and len(aktive_wp_liste) > 0:
    empfohlene_wp = list(aktive_wp_liste.keys())[-1]

puffer_tabelle = {
    "AHPA 412": 300, "AHPA 413": 500, "AHPA 618": 500, "AHPA 722": 800, "AHPA 1030": 1000,
    "AHPC 27": 300, "AHPC 412": 300
}
puffer_groesse = puffer_tabelle.get(empfohlene_wp, 300)

if frischwasser == "ja":
    boiler_groesse = 500
else:
    boiler_tabelle = {1: 300, 2: 300, 3: 300, 4: 400, 5: 400, 6: 500, 7: 500}
    boiler_groesse = boiler_tabelle.get(personen, 400)

mag_tabelle = {300: 35, 500: 50, 800: 80, 1000: 80}
mag_groesse = mag_tabelle.get(puffer_groesse, 35)

# --- Ergebnis-Anzeige ---
st.markdown("---")
st.subheader("📊 Auswertung & Komponentenauswahl")

res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="Berechnete Heizlast", value=f"{heizlast_watt:,.0f} W".replace(",", "."))
    st.metric(label="Warmwasseraufschlag", value=f"{ww_aufschlag} W")
    st.metric(label="Empfohlene Wärmepumpe", value=empfohlene_wp)

with res_col2:
    st.metric(label="Pufferspeicher", value=f"{puffer_groesse} Liter")
    st.metric(label="Trinkwasser-Boiler", value=f"{boiler_groesse} Liter")
    st.metric(label="Ausdehnungsgefäß (MAG)", value=f"{mag_groesse} Liter")

st.success("Konfiguration erfolgreich abgeschlossen!")
