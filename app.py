import streamlit as st
import pandas as pd
import numpy as np
import io

# --- Seiten-Konfiguration ---
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

# --- Kopfbereich ---
col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("https://www.es-ww.de/wp-content/uploads/2023/02/Logo_ESW_farbig-2048x546.png", width=280)

with col_title:
    st.title("Wärmepumpen-Konfigurator & Bivalenzpunkt-Rechner")
    st.markdown("*Interaktive Auslegung, Baureihe-Wahl & Bivalenzpunkt-Begrenzung (inkl. PLZ-Klimadaten)*")
    st.markdown("*Ersetzt keine Heizlastberechnung nach Norm 12831*")

st.markdown("---")

# --- Artikelstamm ---
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
    "SC490_1": {"artnr": "738182", "bezeichnung": "Kompaktspeicher-Lösung SC490-1"},
    "SC490_2": {"artnr": "738183", "bezeichnung": "Kompaktspeicher-Lösung SC490-2"},
    "MAG_35": {"artnr": "80631", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 35 Liter"},
    "MAG_50": {"artnr": "80641", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 50 Liter"},
    "MAG_80": {"artnr": "8065", "bezeichnung": "Membran-Ausdehnungsgefäß Heizung 80 Liter"},
    "Anschlusskombi": {"artnr": "80481", "bezeichnung": "Gefäßanschlusskombination für MAGs bis 50L inkl. Isolierung"},
    "Pumpengruppe_ungemischt": {"artnr": "PG-UNG", "bezeichnung": "Pumpengruppe ungemischt"},
    "Pumpengruppe_gemischt": {"artnr": "PG-GEM", "bezeichnung": "Pumpengruppe gemischt"}
}

# --- Kennlinien-Datenbank ---
x_vals = [-18, -16, -14, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

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
    "AHPA 1030": {
        35: [16.5, 17.5, 18.5, 19.5, 21.0, 22.5, 24.0, 24.8, 25.5, 26.2, 27.0, 30.0, 34.0, 38.0, 42.0, 45.8, 49.5, 53.0, 56.5, 60.0, 63.0],
        55: [16.2, 17.0, 17.8, 18.6, 19.8, 21.0, 22.2, 22.8, 23.3, 23.8, 24.2, 27.0, 31.0, 34.8, 38.5, 41.8, 45.2, 48.5, 51.8, 55.0, 58.0]
    }
}

kennlinien_db_ahpc = {
    "AHPC 27": {
        35: [4.7, 5.0, 5.3, 5.7, 6.1, 6.5, 7.0, 7.5, 8.0, 7.9, 7.9, 8.3, 8.7, 9.1, 9.5, 10.0, 10.1, 10.3, 10.4, 10.6, 10.7],
        55: [4.5, 4.8, 5.1, 5.5, 5.9, 6.3, 6.8, 7.0, 7.1, 7.1, 7.1, 7.5, 8.0, 8.4, 8.8, 9.0, 9.2, 9.3, 9.5, 9.6, 9.7]
    },
    "AHPC 412": {
        35: [7.6, 8.0, 8.5, 9.0, 9.5, 10.0, 10.6, 11.2, 11.8, 12.5, 13.0, 13.5, 14.2, 14.9, 15.6, 16.5, 16.8, 17.1, 17.4, 17.7, 18.0],
        55: [7.2, 7.6, 8.0, 8.5, 9.0, 9.5, 10.1, 10.8, 11.5, 12.2, 12.5, 13.1, 13.8, 14.5, 15.2, 16.0, 16.3, 16.6, 16.9, 17.2, 17.4]
    }
}

# --- Hilfsfunktion zur PLZ-Ermittlung der Norm-Außentemperatur ---
def ermittle_t_norm_aus_plz(plz_str):
    if not plz_str or len(plz_str) < 2:
        return -12.0
    ziffer = plz_str[:1]
    ersten_zwei = plz_str[:2]
    
    plz_mapping_spezial = {
        "82": -16.0, "83": -14.0, "84": -13.0, 
        "93": -14.0, "94": -14.0, "98": -14.0, "99": -13.8,
        "01": -14.0, "02": -14.0, "09": -14.0, 
        "10": -13.3, "12": -13.3, "13": -13.3, "14": -12.7, 
        "20": -10.5, "22": -10.5, "23": -11.0, 
        "50": -8.7, "51": -8.7, "56": -12.0, "54": -12.0,
        "40": -8.4, "41": -8.5, "44": -9.1, "47": -8.4, 
        "60": -10.1, "63": -10.5, "65": -10.5, 
        "70": -11.8, "76": -10.7, "79": -11.0
    }
    
    if ersten_zwei in plz_mapping_spezial:
        return plz_mapping_spezial[ersten_zwei]
        
    zonen_fallback = {
        "0": -13.0, "1": -12.0, "2": -10.0, "3": -11.0, "4": -9.0,
        "5": -10.0, "6": -10.5, "7": -11.0, "8": -12.0, "9": -13.0
    }
    return zonen_fallback.get(ziffer, -12.0)

# --- Eingabebereich (Übersichtlich untereinander / geordnet) ---
st.subheader("1. Gebäudedaten & Parameter")

auswahl_modus = st.radio(
    "Wie möchten Sie die Heizlast ermitteln?", 
    ["1. Über Gebäudestandard & Wohnfläche (Standard)", "2. Anhand fossilem Brennstoffverbrauch (Öl / Gas)", "3. Direkte Heizlast-Vorgabe (z.B. nach DIN 12831)"],
    key="auswahl_modus_radio"
)
heizlast_watt = 0.0
gewaehlte_sanierungen = []
personen = 3

if auswahl_modus.startswith("1."):
    gebaeude_typ = st.radio(
        "Gebäudetyp", 
        ["Einfamilienhaus (EFH)", "Mehrfamilienhaus (MFH)"], 
        horizontal=True,
        key="gebaeude_typ_radio"
    )
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        wohnflaeche = st.number_input("Beheizte Wohnfläche (m²)", min_value=20, max_value=2000, value=160, step=10, key="wohnflaeche_input")
        baujahr = st.slider("Baujahr / Dämmstandard", min_value=1930, max_value=2026, value=1980, step=1, key="baujahr_slider")
    with col_g2:
        personen = st.selectbox("Anzahl Personen im Haushalt", [1, 2, 3, 4, 5, 6, 7], key="personen_select_mode1")
    
    stuetz_jahre = [1930, 1958, 1968, 1977, 1983, 1994, 2001, 2008, 2015, 2026]
    if gebaeude_typ.startswith("Einfamilienhaus"):
        stuetz_lasten = [160.0, 160.0, 140.0, 110.0, 95.0, 75.0, 60.0, 40.0, 30.0, 20.0]
    else:
        stuetz_lasten = [120.0, 120.0, 110.0, 90.0, 75.0, 60.0, 45.0, 35.0, 25.0, 15.0]
        
    spez_heizlast = np.interp(baujahr, stuetz_jahre, stuetz_lasten)
    st.caption(f"Angesetzte spezifische Heizlast ({gebaeude_typ.split()[0]}): **{spez_heizlast:.1f} W/m²** (Baujahr {baujahr})")
    
    heizlast_watt = wohnflaeche * spez_heizlast
    
    st.markdown("#### Geplante Sanierungsmaßnahmen")
    sanierungs_optionen = {
        "Fenster erneuert (2-fach Wärmeschutzverglasung)": 0.075,
        "Fenster erneuert (3-fach Wärmeschutzverglasung)": 0.115,
        "Kellerdeckendämmung (Ca. 6–12 cm)": 0.055,
        "Oberste Geschossdecke gedämmt (Ca. 14–24 cm)": 0.085,
        "Dachdämmung (Zwischen-/Aufsparrendämmung)": 0.14,
        "Außenwanddämmung (Ca. 12–16 cm WDVS)": 0.20,
        "Rohrleitungen gedämmt (im unheiz. Bereich)": 0.02,
        "Lüftungsanlage mit Wärmerückgewinnung": 0.10
    }
    gewaehlte_sanierungen = st.multiselect(
        "Wählen Sie durchgeführte oder geplante Sanierungsmaßnahmen:",
        options=list(sanierungs_optionen.keys()),
        default=[],
        key="sanierung_multiselect"
    )
    reduktions_faktor = sum([sanierungs_optionen[m] for m in gewaehlte_sanierungen])
    reduktions_faktor = min(reduktions_faktor, 0.60)
    heizlast_watt = heizlast_watt * (1.0 - reduktions_faktor)
    
    if gewaehlte_sanierungen:
        st.info(f"💡 Reduktion durch Sanierung: **-{reduktions_faktor*100:.1f}%**")

elif auswahl_modus.startswith("2."):
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        brennstoff_art = st.selectbox("Brennstoffart", ["Heizöl (Liter/Jahr)", "Erdgas (kWh/Jahr)", "Flüssiggas (Liter/Jahr)"], key="brennstoff_select")
        verbrauch = st.number_input("Jahresverbrauch", min_value=500, max_value=100000, value=2500, step=100, key="verbrauch_input")
    with col_b2:
        personen = st.selectbox("Anzahl Personen im Haushalt", [1, 2, 3, 4, 5, 6, 7], key="personen_select_mode2")
    
    if "Heizöl" in brennstoff_art:
        jaehrliche_waermearbeit = verbrauch * 10 * 0.85
    elif "Erdgas" in brennstoff_art:
        jaehrliche_waermearbeit = verbrauch * 0.85
    else:
        jaehrliche_waermearbeit = verbrauch * 6.5 * 0.85
    heizlast_watt = (jaehrliche_waermearbeit / 2000) * 1000
else:
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        heizlast_kw = st.number_input("Vorhandene Heizlast / Vorgabe (kW)", min_value=2.0, max_value=100.0, value=10.0, step=0.5, key="heizlast_kw_input")
    with col_v2:
        personen = st.selectbox("Anzahl Personen im Haushalt", [1, 2, 3, 4, 5, 6, 7], key="personen_select_mode3")
    heizlast_watt = heizlast_kw * 1000.0

st.markdown("---")

# --- Klimadaten ---
st.subheader("2. Klimadaten")
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
    plz_eingabe = st.text_input("Standort Postleitzahl (PLZ)", value="56410", max_chars=5, key="plz_input")
    t_norm_automatisch = ermittle_t_norm_aus_plz(plz_eingabe)
with col_k2:
    t_grenz = st.number_input("Heizgrenztemperatur (T_grenz) [°C]", min_value=10.0, max_value=20.0, value=15.0, step=1.0, key="tgrenz_input")
with col_k3:
    systemtemperatur = st.selectbox("Systemtemperatur / Vorlauf [°C]", [35, 55], key="systemtemp_select")

manuell_ueberschreiben = st.checkbox("Norm-Außentemperatur manuell anpassen", value=False, key="manuell_chk")
if manuell_ueberschreiben:
    t_norm = st.number_input("Norm-Außentemperatur (T_norm) [°C]", min_value=-25.0, max_value=0.0, value=float(t_norm_automatisch), step=1.0, key="tnorm_manuell")
else:
    t_norm = t_norm_automatisch
    st.info(f"📍 Ermittelte Norm-Außentemperatur für PLZ {plz_eingabe if plz_eingabe else '...'} : **{t_norm} °C**")

st.markdown("---")

# --- Baureihe + Zubehör ---
st.subheader("3. Baureihe + Zubehör")
col_z1, col_z2 = st.columns(2)
with col_z1:
    baureihe_wahl = st.selectbox("Wärmepumpe", ["AHPA", "AHPC"], key="baureihe_select")
with col_z2:
    speicherloesung = st.selectbox("Speicherlösung", ["Zweispeicherlösung", "SC490-1", "SC490-2"], key="speicherloesung_select")

# Bedingte Abfrage: Nur bei Zweispeicherlösung Warmwasser & Frischwasser abfragen
pumpengruppen_liste = []
if speicherloesung == "Zweispeicherlösung":
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        ww_bereitung = st.selectbox("Warmwasserbereitung", ["ja", "nein"], key="ww_bereit_select")
    with col_w2:
        frischwasser = st.selectbox("Frischwassermodul", ["nein", "ja"], key="frischwasser_select")
    
    st.markdown("#### Pumpengruppen-Konfiguration")
    anzahl_pumpengruppen = st.selectbox("Anzahl der Pumpengruppen", [1, 2, 3], key="anzahl_pg_select")
    
    pg_cols = st.columns(anzahl_pumpengruppen)
    for i in range(1, anzahl_pumpengruppen + 1):
        with pg_cols[i-1]:
            typ = st.selectbox(f"Pumpengruppe {i}", ["gemischt", "ungemischt"], key=f"pg_typ_{i}")
            pumpengruppen_liste.append(typ)
else:
    ww_bereitung = "nein"
    frischwasser = "nein"

# --- Ab hier Haupt-Flow ---
ww_aufschlag = (personen * 500) if ww_bereitung == "ja" else 0
gesamt_last_kw = (heizlast_watt + ww_aufschlag) / 1000.0

aktive_db = kennlinien_db_ahpa if baureihe_wahl == "AHPA" else kennlinien_db_ahpc
ergebnisse_liste = []

for wp_name, daten in aktive_db.items():
    wp_leistungen = daten[systemtemperatur]
    biv_punkt = 99.0
    leistung_biv = 0.0
    last_werte = [gesamt_last_kw * (t_grenz - x) / (t_grenz - t_norm) for x in x_vals]
    differenzen = [wp_l - l_w for wp_l, l_w in zip(wp_leistungen, last_werte)]
    
    for i in range(len(x_vals) - 1):
        if differenzen[i] * differenzen[i+1] <= 0:
            x1, x2 = x_vals[i], x_vals[i+1]
            d1, d2 = differenzen[i], differenzen[i+1]
            if d1 != d2:
                biv_punkt = x1 - d1 * (x2 - x1) / (d2 - d1)
                leistung_biv = wp_leistungen[i] + (biv_punkt - x1) / (x2 - x1) * (wp_leistungen[i+1] - wp_leistungen[i])
            else:
                biv_punkt = x1
                leistung_biv = wp_leistungen[i]
            break
            
    if biv_punkt == 99.0 and differenzen[0] >= 0:
        biv_punkt = -18.0
        leistung_biv = wp_leistungen[0]
    elif biv_punkt == 99.0:
        biv_punkt = 22.0
        leistung_biv = wp_leistungen[-1]

    wp_power_tnorm = np.interp(t_norm, x_vals, wp_leistungen)
    deckungsgrad_norm = (wp_power_tnorm / gesamt_last_kw) * 100
    
    ergebnisse_liste.append({
        "Modell": wp_name,
        "Bivalenzpunkt [°C]": round(biv_punkt, 1),
        "Leistung bei Biv. [kW]": round(leistung_biv, 2),
        "Deckung bei T_norm [%]": round(deckungsgrad_norm, 1),
        "Leistungen": wp_leistungen,
        "MaxLeistungBei22C": wp_leistungen[-1]
    })

df_ergebnisse = pd.DataFrame(ergebnisse_liste)
df_geprueft = df_ergebnisse.sort_values(by="MaxLeistungBei22C", ascending=True)
passende_wps = df_geprueft[(df_geprueft["Bivalenzpunkt [°C]"] >= -9.0) & (df_geprueft["Bivalenzpunkt [°C]"] <= -4.0)]

warnung_aktiv = False
if not passende_wps.empty:
    empfohlene_wp = passende_wps.iloc[0]["Modell"]
else:
    empfohlene_wp = df_geprueft.iloc[0]["Modell"]
    warnung_aktiv = True

row_empf = df_ergebnisse[df_ergebnisse["Modell"] == empfohlene_wp].iloc[0]
biv_empfehlung = row_empf["Bivalenzpunkt [°C]"]
aktive_leistungen = row_empf["Leistungen"]

alternativ_wp = ""
alternativ_biv = 0.0
alternativ_leistungen = []

if warnung_aktiv:
    staerkere_modelle = df_geprueft[df_geprueft["MaxLeistungBei22C"] >= row_empf["MaxLeistungBei22C"]]
    if len(staerkere_modelle) > 1:
        alternativ_row = staerkere_modelle.iloc[1]
    else:
        alternativ_row = df_geprueft.iloc[-1]
    
    alternativ_wp = alternativ_row["Modell"]
    alternativ_biv = alternativ_row["Bivalenzpunkt [°C]"]
    alternativ_leistungen = alternativ_row["Leistungen"]

def berechne_komponenten(modell_name):
    if speicherloesung.startswith("SC490"):
        puffer_gr = 0
        boiler_gr = 0
        mag_gr = 50  # Fix 50 Liter bei SC490-1 und SC490-2
    else:
        puffer_tabelle = {"AHPA 412": 300, "AHPA 413": 500, "AHPA 618": 500, "AHPA 722": 800, "AHPA 1030": 1000, "AHPC 27": 300, "AHPC 412": 300}
        puffer_gr = puffer_tabelle.get(modell_name, 300)

        if frischwasser == "ja":
            boiler_gr = 500
        else:
            boiler_tabelle = {1: 300, 2: 300, 3: 300, 4: 400, 5: 400, 6: 500, 7: 500}
            boiler_gr = boiler_tabelle.get(personen, 400)

        mag_tabelle = {300: 35, 500: 50, 800: 80, 1000: 80}
        mag_gr = mag_tabelle.get(puffer_gr, 35)
    return puffer_gr, boiler_gr, mag_gr

st.markdown("---")
st.subheader("4. Auswertung, Bivalenzpunkt & Komponentenauswahl")

if warnung_aktiv:
    st.warning(f"**Hinweis:** Keines der Modelle aus der Baureihe **{baureihe_wahl}** erreicht bei dieser Heizlast einen Bivalenzpunkt im Zielbereich von **-4°C bis -9°C**. Das kleinste verfügbare Modell (**{empfohlene_wp}**) wurde als Empfehlung gewählt.")
    st.markdown("### Modell-Auswahl für das Angebot:")
    
    auswahl_optionen = [
        f"Empfohlenes Klein-Modell: {empfohlene_wp} (Biv.: {biv_empfehlung} °C)",
        f"Nächstgrößere Alternative: {alternativ_wp} (Biv.: {alternativ_biv} °C)"
    ]
    
    gewaehlte_option = st.radio(
        "Welches Modell möchten Sie für die Detailansicht und das Diagramm verwenden?",
        auswahl_optionen,
        key="modell_auswahl_radio"
    )
    
    if "Alternative" in gewaehlte_option:
        aktives_modell = alternativ_wp
        aktiver_biv = alternativ_biv
        aktive_leistungen = alternativ_leistungen
    else:
        aktives_modell = empfohlene_wp
        aktiver_biv = biv_empfehlung
        aktive_leistungen = row_empf["Leistungen"]
else:
    aktives_modell = empfohlene_wp
    aktiver_biv = biv_empfehlung
    aktive_leistungen = row_empf["Leistungen"]

puffer_groesse, boiler_groesse, mag_groesse = berechne_komponenten(aktives_modell)

res_col1, res_col2, res_col3 = st.columns(3)
with res_col1:
    st.metric(label="Gesamt-Heizlast", value=f"{gesamt_last_kw:.1f} kW")
    st.metric(label=f"Ausgewählte WP ({baureihe_wahl})", value=aktives_modell)

with res_col2:
    st.metric(label="Ermittelter Bivalenzpunkt", value=f"{aktiver_biv} °C")
    st.metric(label="Ausdehnungsgefäß (MAG)", value=f"{mag_groesse} Liter")

with res_col3:
    if speicherloesung.startswith("SC490"):
        st.metric(label="Speicherlösung", value=speicherloesung)
        st.metric(label="System", value="Kompaktspeicher")
    else:
        st.metric(label="Pufferspeicher", value=f"{puffer_groesse} Liter")
        st.metric(label="Trinkwasser-Boiler / FriWa", value=f"{boiler_groesse} Liter")

st.markdown("---")
st.subheader(f"Kennlinien-Vergleich für {aktives_modell}")

chart_data = pd.DataFrame({
    "Quellentemperatur (°C)": x_vals,
    "Gebäude-Heizlast (kW)": [gesamt_last_kw * (t_grenz - x) / (t_grenz - t_norm) for x in x_vals],
    f"WP Maximalleistung {aktives_modell} ({systemtemperatur}°C)": aktive_leistungen
}).set_index("Quellentemperatur (°C)")

st.line_chart(chart_data)

st.markdown("---")
st.subheader("Artikel-Stückliste für CRM-Export")

stueckliste = []
wp_info = ARTIKEL_DB.get(aktives_modell, {"artnr": "UNKNOWN", "bezeichnung": aktives_modell})
stueckliste.append({"Pos": 1, "Kategorie": "Wärmepumpe", "Artikelnummer": wp_info["artnr"], "Bezeichnung": wp_info["bezeichnung"], "Menge": 1, "Einheit": "Stk"})

if speicherloesung.startswith("SC490"):
    sc_key = "SC490_1" if speicherloesung == "SC490-1" else "SC490_2"
    sc_info = ARTIKEL_DB[sc_key]
    stueckliste.append({"Pos": 2, "Kategorie": "Speicher", "Artikelnummer": sc_info["artnr"], "Bezeichnung": sc_info["bezeichnung"], "Menge": 1, "Einheit": "Stk"})
else:
    puffer_key = f"Puffer_{puffer_groesse}"
    puffer_info = ARTIKEL_DB.get(puffer_key, {"artnr": f"PS-{puffer_groesse}L", "bezeichnung": f"Pufferspeicher {puffer_groesse} L"})
    stueckliste.append({"Pos": 2, "Kategorie": "Speicher", "Artikelnummer": puffer_info["artnr"], "Bezeichnung": puffer_info["bezeichnung"], "Menge": 1, "Einheit": "Stk"})

    if frischwasser == "ja":
        friwa_info = ARTIKEL_DB["FriWa_Modul"]
        stueckliste.append({"Pos": 3, "Kategorie": "Warmwasser", "Artikelnummer": friwa_info["artnr"], "Bezeichnung": friwa_info["bezeichnung"], "Menge": 1, "Einheit": "Stk"})
    elif ww_bereitung == "ja":
        boiler_key = f"Boiler_{boiler_groesse}"
        boiler_info = ARTIKEL_DB.get(boiler_key, {"artnr": f"TWS-{boiler_groesse}L", "bezeichnung": f"Trinkwasserspeicher {boiler_groesse} L"})
        stueckliste.append({"Pos": 3, "Kategorie": "Warmwasser", "Artikelnummer": boiler_info["artnr"], "Bezeichnung": boiler_info["bezeichnung"], "Menge": 1, "Einheit": "Stk"})

# MAG hinzufügen
mag_key = f"MAG_{mag_groesse}"
mag_info = ARTIKEL_DB.get(mag_key, {"artnr": f"MAG_{mag_groesse}", "bezeichnung": f"Membran-Ausdehnungsgefäß {mag_groesse} L"})
stueckliste.append({"Pos": len(stueckliste) + 1, "Kategorie": "Zubehör", "Artikelnummer": mag_info["artnr"], "Bezeichnung": mag_info["bezeichnung"], "Menge": 1, "Einheit": "Stk"})

# Wenn MAG <= 50 Liter, Gefäßanschlusskombination automatisch hinzufügen
if mag_groesse <= 50:
    kombi_info = ARTIKEL_DB["Anschlusskombi"]
    stueckliste.append({"Pos": len(stueckliste) + 1, "Kategorie": "Zubehör", "Artikelnummer": kombi_info["artnr"], "Bezeichnung": kombi_info["bezeichnung"], "Menge": 1, "Einheit": "Stk"})

# Pumpengruppen zur Stückliste hinzufügen (nur bei Zweispeicherlösung)
if speicherloesung == "Zweispeicherlösung":
    for idx, pg_typ in enumerate(pumpengruppen_liste, 1):
        pg_key = f"Pumpengruppe_{pg_typ}"
        pg_info = ARTIKEL_DB[pg_key]
        stueckliste.append({
            "Pos": len(stueckliste) + 1,
            "Kategorie": "Pumpengruppe",
            "Artikelnummer": pg_info["artnr"],
            "Bezeichnung": f"Pumpengruppe {idx} ({pg_typ})",
            "Menge": 1,
            "Einheit": "Stk"
        })

df_stueckliste = pd.DataFrame(stueckliste)
st.dataframe(df_stueckliste, use_container_width=True, hide_index=True)

def create_excel_download(df_items):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_items.to_excel(writer, index=False, sheet_name='Artikelstueckliste_CRM')
        df_params = pd.DataFrame([
            {"Parameter": "Gebäudetyp", "Wert": gebaeude_typ if 'gebaeude_typ' in locals() else "N/A"},
            {"Parameter": "Gewähltes WP-Modell", "Wert": aktives_modell},
            {"Parameter": "Baureihe", "Wert": baureihe_wahl},
            {"Parameter": "Speicherlösung", "Wert": speicherloesung},
            {"Parameter": "Standort PLZ", "Wert": plz_eingabe if 'plz_eingabe' in locals() else "N/A"},
            {"Parameter": "Norm-Außentemperatur (°C)", "Wert": t_norm},
            {"Parameter": "Sanierungsmaßnahmen", "Wert": ", ".join(gewaehlte_sanierungen) if gewaehlte_sanierungen else "Keine"},
            {"Parameter": "Gesamtheizlast (kW)", "Wert": round(gesamt_last_kw, 2)},
            {"Parameter": "Ermittelter Bivalenzpunkt (°C)", "Wert": round(aktiver_biv, 1)},
            {"Parameter": "Vorlauftemperatur (°C)", "Wert": systemtemperatur},
            {"Parameter": "Warmwasserbereitung", "Wert": ww_bereitung},
            {"Parameter": "Frischwassermodul", "Wert": frischwasser},
            {"Parameter": "Pumpengruppen Konfiguration", "Wert": ", ".join([f'PG {i+1}: {t}' for i, t in enumerate(pumpengruppen_liste)]) if speicherloesung == "Zweispeicherlösung" else "N/A"}
        ])
        df_params.to_excel(writer, index=False, sheet_name='Auslegungsdaten')
    return output.getvalue()

excel_data = create_excel_download(df_stueckliste)

st.download_button(
    label="Artikelliste als Excel für CRM herunterladen",
    data=excel_data,
    file_name=f"CRM_Angebotspositionen_{aktives_modell.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("App mit neuem Layout und bedingten Pumpengruppen fehlerfrei geladen!")
