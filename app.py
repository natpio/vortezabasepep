import streamlit as st
import pandas as pd
import json
import requests
import base64
from PIL import Image

# =========================================================
# KONFIGURACJA GITHUB I SEKRETÓW
# =========================================================
try:
    GITHUB_TOKEN = st.secrets["G_TOKEN"]
    USER_DB = st.secrets["credentials"]["usernames"]
except Exception as e:
    GITHUB_TOKEN = "BRAK"
    USER_DB = {}

REPO_OWNER = "natpio"
REPO_NAME = "rentownosc-transportu"
FILE_PATH = "config.json"

# =========================================================
# FUNKCJE POMOCNICZE DANYCH
# =========================================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def get_github_data():
    """Pobiera plik konfiguracyjny z GitHub API."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded), content['sha']
        else:
            if st.session_state.get("authenticated"):
                st.error(f"Błąd GitHub API: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        if st.session_state.get("authenticated"):
            st.error(f"Błąd połączenia z bazą Cloud: {e}")
        return None, None

def update_github_data(new_data, sha):
    """Aktualizuje plik konfiguracyjny na GitHubie."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    updated_content = json.dumps(new_data, indent=4, ensure_ascii=False)
    encoded = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": "Update from VORTEZA FLOW Interface",
        "content": encoded,
        "sha": sha
    }
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200, 201]

# =========================================================
# SYSTEM LOGOWANIA
# =========================================================
def check_password():
    """Zarządza dostępem do aplikacji."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("Login"):
                st.markdown("### VORTEZA | SECURE ACCESS")
                user = st.text_input("Użytkownik")
                password = st.text_input("Hasło", type="password")
                submit = st.form_submit_button("ZALOGUJ")
                
                if submit:
                    if user in USER_DB and USER_DB[user] == password:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user
                        st.rerun()
                    else:
                        st.error("Nieprawidłowe dane logowania.")
        return False
    return True

# =========================================================
# STYLIZACJA VORTEZA SYSTEMS (SQM STYLE)
# =========================================================
def apply_vorteza_theme():
    bin_str = get_base64_of_bin_file('bg_vorteza.png')
    if bin_str:
        bg_style = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(bg_style, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #0E0E0E; }</style>", unsafe_allow_html=True)

    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');

            :root {
                --v-copper: #B58863;
                --v-dark: #0E0E0E;
                --v-panel: rgba(20, 20, 20, 0.9);
                --v-text: #E0E0E0;
            }

            .stApp {
                color: var(--v-text);
                font-family: 'Montserrat', sans-serif;
            }

            h1, h2, h3, .stSubheader {
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }

            label[data-testid="stWidgetLabel"] {
                color: var(--v-copper) !important;
                font-weight: 700 !important;
                text-transform: uppercase;
                font-size: 0.85rem !important;
                letter-spacing: 1px;
            }

            div[data-baseweb="select"] > div, input {
                background-color: rgba(15, 15, 15, 0.9) !important;
                color: white !important;
                border: 1px solid #444 !important;
            }
            
            .vorteza-card {
                background-color: var(--v-panel);
                padding: 30px;
                border-radius: 5px;
                border-left: 5px solid var(--v-copper);
                box-shadow: 0 10px 40px rgba(0,0,0,0.8);
                backdrop-filter: blur(15px);
                margin-bottom: 20px;
            }

            .route-preview {
                background-color: rgba(181, 136, 99, 0.1);
                border: 1px solid var(--v-copper);
                padding: 15px;
                margin-top: 15px;
                border-radius: 4px;
            }

            [data-testid="stMetricValue"] {
                color: var(--v-copper) !important;
                font-size: 2.2rem !important;
                font-weight: 700 !important;
            }

            .stButton > button {
                background-color: rgba(0, 0, 0, 0.7);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 15px;
                width: 100%;
                font-weight: 700;
                text-transform: uppercase;
                transition: 0.3s;
            }
            .stButton > button:hover {
                background-color: var(--v-copper);
                color: black;
            }

            .cost-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            .cost-table th {
                text-align: left;
                color: var(--v-copper);
                border-bottom: 1px solid #444;
                padding: 8px;
            }
            .cost-table td {
                padding: 10px 8px;
                border-bottom: 1px solid #222;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# GŁÓWNA LOGIKA APLIKACJI
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW | SQM", layout="wide")
apply_vorteza_theme()

if check_password():
    # Nagłówek aplikacji
    col_logo, col_title, col_logout = st.columns([1, 4, 1])
    with col_logo:
        try:
            logo = Image.open('logo_vorteza.png')
            st.image(logo, use_container_width=True)
        except:
            st.title("VORTEZA")

    with col_title:
        st.markdown("<br>", unsafe_allow_html=True)
        st.title("VORTEZA FLOW")
    
    with col_logout:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("WYLOGUJ"):
            del st.session_state["authenticated"]
            st.rerun()

    if GITHUB_TOKEN == "BRAK":
        st.error("SYSTEM HALT: GITHUB_TOKEN MISSING.")
    else:
        config, file_sha = get_github_data()

        # Renderujemy zakładki TYLKO jeśli dane zostały pobrane pomyślnie
        if config:
            tab1, tab2 = st.tabs(["📊 MARGIN ANALYZER", "⚙️ SYSTEM CORE"])

            # --- TAB 1: KALKULATOR ---
            with tab1:
                col_cfg, col_res = st.columns([1, 1], gap="large")
                
                with col_cfg:
                    st.subheader("Transport Configuration")
                    v_type = st.selectbox("Vehicle Unit Type", list(config["VEHICLE_DATA"].keys()))
                    start_p = st.selectbox("Starting Point", list(config["DISTANCES_AND_MYTO"].keys()))
                    
                    available_dests = list(config["DISTANCES_AND_MYTO"][start_p].keys())
                    route = st.selectbox("Target Destination", available_dests) if available_dests else None
                    extra_km = st.number_input("Additional Distance (KM)", value=0, step=10)
                    
                    if route:
                        r_info = config["DISTANCES_AND_MYTO"][start_p][route]
                        st.markdown(f"""
                            <div class="route-preview">
                                <b style="color:#B58863;">BASE DISTANCE DATA:</b><br>
                                🇵🇱 Poland: <b>{r_info['distPL']} km</b><br>
                                🇪🇺 EU / Other: <b>{r_info['distEU']} km</b><br>
                                ➕ Additional: <b>{extra_km} km</b><br>
                                <hr style="border:0; border-top:1px solid #444; margin:5px 0;">
                                📏 Total Calculation: <b>{r_info['distPL'] + r_info['distEU'] + extra_km} km</b>
                            </div>
                        """, unsafe_allow_html=True)

                with col_res:
                    if route:
                        st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
                        st.subheader("Technical Margin Analysis")
                        
                        v_info = config["VEHICLE_DATA"][v_type]
                        prices = config["PRICE"]
                        euro_rate = config["EURO_RATE"]
                        total_km = r_info["distPL"] + r_info["distEU"] + extra_km

                        total_fuel_l = total_km * v_info["fuelUsage"]
                        pl_l = min(total_fuel_l, v_info["tankCapacity"])
                        eu_l = max(0, total_fuel_l - pl_l)
                        
                        c_fuel_pln = (pl_l * prices["fuelPLN"]) + (eu_l * prices["fuelEUR"] * euro_rate)
                        c_adblue_pln = (total_km * v_info["adBlueUsage"]) * prices["adBluePLN"]
                        c_service_pln = (r_info["distPL"] * v_info["serviceCostPLN"]) + ((r_info["distEU"] + extra_km) * v_info["serviceCostEUR"] * euro_rate)
                        
                        myto_key = f"myto{v_type}"
                        c_myto_eur = r_info.get(myto_key, 0)
                        c_myto_pln = c_myto_eur * euro_rate
                        
                        total_pln = c_fuel_pln + c_adblue_pln + c_service_pln + c_myto_pln
                        total_eur = total_pln / euro_rate

                        m1, m2 = st.columns(2)
                        m1.metric("TOTAL COST (PLN)", f"{round(total_pln, 2)} zł")
                        m2.metric("TOTAL COST (EUR)", f"€ {round(total_eur, 2)}")

                        st.markdown(f"""
                            <table class="cost-table">
                                <tr><th>Category</th><th>PLN Value</th><th>EUR Value</th></tr>
                                <tr><td>Fuel & Energy</td><td>{round(c_fuel_pln, 2)} zł</td><td>€ {round(c_fuel_pln/euro_rate, 2)}</td></tr>
                                <tr><td>AdBlue Fluids</td><td>{round(c_adblue_pln, 2)} zł</td><td>€ {round(c_adblue_pln/euro_rate, 2)}</td></tr>
                                <tr><td>Technical Service</td><td>{round(c_service_pln, 2)} zł</td><td>€ {round(c_service_pln/euro_rate, 2)}</td></tr>
                                <tr><td>Road Tolls (Myto)</td><td>{round(c_myto_pln, 2)} zł</td><td>€ {round(c_myto_eur, 2)}</td></tr>
                            </table>
                            <div style="margin-top:15px; font-size:0.75rem; color:#666; text-transform: uppercase;">
                                EX RATE: 1 EUR = {euro_rate} PLN | UNIT: {v_type} | {start_p} - {route}
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

            # --- TAB 2: SYSTEM CORE ---
            with tab2:
                st.subheader("Vorteza Master Access")
                if st.session_state.get("username") == "admin":
                    st.success(f"Authorized as {st.session_state.username}")
                    
                    st.markdown("### 1. Global Economic Factors")
                    e1, e2, e3 = st.columns(3)
                    with e1: new_euro = st.number_input("EURO Rate (PLN)", value=config["EURO_RATE"], format="%.4f")
                    with e2: new_f_pl = st.number_input("Fuel PLN/L", value=config["PRICE"]["fuelPLN"])
                    with e3: new_f_eu = st.number_input("Fuel EUR/L", value=config["PRICE"]["fuelEUR"])
                    
                    st.write("---")
                    st.markdown("### 2. Route Management")
                    adm_mode = st.radio("Database Mode:", ["Add New Route", "Edit / Delete Existing"], horizontal=True)

                    if adm_mode == "Add New Route":
                        as1, as2 = st.columns(2)
                        with as1:
                            starts = list(config["DISTANCES_AND_MYTO"].keys())
                            s_city = st.selectbox("Start City", ["+ NEW"] + starts)
                            if s_city == "+ NEW": s_city = st.text_input("Type Start City Name")
                        with as2: d_city = st.text_input("Type Destination Name")
                        v_pl, v_eu, v_mftl, v_msolo, v_mbus = 0, 0, 0, 0, 0
                    else:
                        as1, as2 = st.columns(2)
                        with as1: s_city = st.selectbox("Select Start Point", list(config["DISTANCES_AND_MYTO"].keys()))
                        with as2: 
                            d_list = list(config["DISTANCES_AND_MYTO"][s_city].keys())
                            d_city = st.selectbox("Select Target City", d_list) if d_list else None
                        
                        if d_city:
                            curr = config["DISTANCES_AND_MYTO"][s_city][d_city]
                            v_pl, v_eu = curr["distPL"], curr["distEU"]
                            v_mftl = curr.get("mytoFTL", 0)
                            v_msolo = curr.get("mytoSolo", 0)
                            v_mbus = curr.get("mytoBus", 0)
                        else:
                            v_pl, v_eu, v_mftl, v_msolo, v_mbus = 0, 0, 0, 0, 0

                    if s_city and d_city and s_city != "+ NEW":
                        st.markdown(f"#### Edit Entry: {s_city} ➔ {d_city}")
                        ed1, ed2 = st.columns(2)
                        with ed1:
                            n_pl = st.number_input("Distance PL (km)", value=v_pl)
                            n_eu = st.number_input("Distance EU (km)", value=v_eu)
                        with ed2:
                            n_mftl = st.number_input("Road Tolls FTL (EURO)", value=float(v_mftl), step=0.1)
                            n_msolo = st.number_input("Road Tolls Solo (EURO)", value=float(v_msolo), step=0.1)
                            n_mbus = st.number_input("Road Tolls Bus (EURO)", value=float(v_mbus), step=0.1)

                        if st.button("SAVE"):
                            if s_city not in config["DISTANCES_AND_MYTO"]: 
                                config["DISTANCES_AND_MYTO"][s_city] = {}
                            config["DISTANCES_AND_MYTO"][s_city][d_city] = {
                                "distPL": n_pl, "distEU": n_eu, 
                                "mytoFTL": n_mftl, "mytoSolo": n_msolo, "mytoBus": n_mbus
                            }
                            # Aktualizacja stałych ekonomicznych
                            config["EURO_RATE"] = new_euro
                            config["PRICE"]["fuelPLN"] = new_f_pl
                            config["PRICE"]["fuelEUR"] = new_f_eu
                            
                            if update_github_data(config, file_sha):
                                st.success("Cloud Synchronized Successfully.")
                                st.rerun()

                        if adm_mode == "Edit / Delete Existing" and st.button("DELETE THIS ENTRY PERMANENTLY"):
                            del config["DISTANCES_AND_MYTO"][s_city][d_city]
                            if not config["DISTANCES_AND_MYTO"][s_city]: 
                                del config["DISTANCES_AND_MYTO"][s_city]
                            if update_github_data(config, file_sha):
                                st.success("Entry Deleted.")
                                st.rerun()
                else:
                    st.warning("Ta sekcja jest dostępna tylko dla użytkownika o uprawnieniach 'admin'.")
        else:
            st.error("Brak dostępu do danych konfiguracyjnych. Sprawdź poświadczenia GitHub API.")
