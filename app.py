import streamlit as st
import json
import requests
import base64
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# =========================================================
# 1. KONFIGURACJA I ZASOBY - NOWE REPOZYTORIUM
# =========================================================
try:
    # Pobieranie tokena z nowej struktury sekretów
    GITHUB_TOKEN = st.secrets["G_TOKEN"]
except:
    GITHUB_TOKEN = None 

REPO_OWNER = "natpio"
REPO_NAME = "vortezabasepep"
# Twój nowy SHEET_ID z linku google sheets
SHEET_ID = "1JV-vXpwAbvvboQd7eijashVmS3kkOqTf_LJrbrsWSxo"

def get_github_file(file_path):
    if not GITHUB_TOKEN: return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
    except: pass
    return None

def get_remote_data():
    content = get_github_file("lista_kontrolna.json")
    if content:
        data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
        return data, content['sha']
    return None, None

def get_bg_base64():
    content = get_github_file("bg_vorteza.png")
    if content and 'content' in content:
        return content['content'].replace("\n", "").replace("\r", "")
    return ""

def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Pamiętaj o dodaniu GCP_SERVICE_ACCOUNT w secrets
    creds_info = st.secrets["GCP_SERVICE_ACCOUNT"]
    credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(credentials)

def load_from_google_sheets():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except: return pd.DataFrame()

def save_to_google_sheets(row_data):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row(row_data)
        return True
    except: return False

# =========================================================
# 2. DESIGN VORTEZA 15.6 - STYLE
# =========================================================
def apply_vorteza_design():
    bg_data = get_bg_base64()
    bg_style = f"""
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.92)), 
                        url("data:image/png;base64,{bg_data}") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}
    """ if bg_data else ".stApp { background-color: #050505 !important; }"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Montserrat:wght@400;700&display=swap');
        
        {bg_style}
        
        [data-testid="stWidgetLabel"], .stMarkdown, p, label {{
            color: #B58863 !important;
            font-family: 'Montserrat', sans-serif !important;
        }}

        .vorteza-header {{
            font-family: 'Michroma', sans-serif !important;
            color: #B58863 !important;
            text-align: center; letter-spacing: 4px; padding: 20px; text-transform: uppercase;
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.98) !important;
            border-right: 1px solid #B58863;
        }}
        
        [data-testid="stExpander"] svg {{ display: none !important; }}
        
        .stExpander {{
            background-color: rgba(20, 20, 20, 0.8) !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
            border-radius: 4px !important;
            margin-bottom: 8px !important;
        }}

        [data-testid="stExpanderSummary"] > div {{
            color: #B58863 !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.9rem !important;
            text-transform: uppercase;
        }}

        .log-entry {{
            background-color: rgba(12, 12, 12, 0.95) !important;
            border-left: 8px solid #B58863 !important;
            padding: 20px; margin-bottom: 15px; color: #B58863 !important;
        }}

        .log-entry-alert {{ border-left: 8px solid #FF4B4B !important; }}

        .card-plate {{
            font-family: 'Michroma', sans-serif !important;
            font-size: 1.4rem !important;
            color: #B58863 !important;
        }}

        input, textarea, [data-baseweb="select"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #B58863 !important;
            border: 1px solid rgba(181, 136, 99, 0.3) !important;
        }}

        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display:none;}}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. LOGIKA SYSTEMU
# =========================================================
st.set_page_config(page_title="VORTEZA LOGISTICS", layout="wide")
apply_vorteza_design()

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        try: st.image('logo_vorteza.png', use_container_width=True)
        except: pass
        st.markdown("<h1 class='vorteza-header'>SYSTEM ACCESS</h1>", unsafe_allow_html=True)
        u = st.text_input("OPERATOR ID")
        p = st.text_input("SECURITY KEY", type="password")
        if st.button("AUTHORIZE"):
            # Pobieranie użytkowników z sekcji [credentials][usernames] lub [USERS]
            users = st.secrets.get("USERS", {})
            if u in users and str(users[u]) == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")

else:
    is_dispatcher = "dyspozytor" in st.session_state.user.lower() or st.session_state.user == "admin"
    
    with st.sidebar:
        try: st.image('logo_vorteza.png', width=150)
        except: pass
        st.write(f"USER: **{st.session_state.user.upper()}**")
        st.markdown("---")
        
        if is_dispatcher:
            df_full = load_from_google_sheets()
            if not df_full.empty:
                # Kolumny muszą istnieć w Twoim Sheets
                raw_plates = df_full['Numer Rejestracyjny'].astype(str).unique()
                plates = ["WSZYSTKIE"] + sorted([p for p in raw_plates if p.strip()])
                f_plate = st.selectbox("POJAZD", plates)
                f_alerts = st.checkbox("TYLKO ALERTY")
            if st.button("ODŚWIEŻ"): st.rerun()
            st.markdown("---")
        
        if st.button("WYLOGUJ"):
            st.session_state.auth = False
            st.rerun()

    if is_dispatcher:
        st.markdown("<h2 class='vorteza-header'>COMMAND CENTER</h2>", unsafe_allow_html=True)
        
        if not df_full.empty:
            df = df_full.copy()
            df['Data i Godzina'] = pd.to_datetime(df['Data i Godzina'], errors='coerce')
            df = df.dropna(subset=['Data i Godzina'])
            
            if f_plate != "WSZYSTKIE":
                df = df[df['Numer Rejestracyjny'].astype(str) == f_plate]
            if f_alerts:
                df = df[df['Wynik Kontroli'].str.contains("ALERT|USTERK|BRAK", na=False, case=False)]
            
            df = df.sort_values(by='Data i Godzina', ascending=False)

            for _, row in df.iterrows():
                status_raw = str(row.get('Wynik Kontroli', ''))
                is_alert = any(word in status_raw.upper() for word in ["ALERT", "USTERK", "BRAK"])
                entry_class = "log-entry log-entry-alert" if is_alert else "log-entry"
                
                if is_alert:
                    msg = status_raw.split(":")[-1] if ":" in status_raw else status_raw
                    fault_html = f'<div style="color:#FF4B4B; margin-top:10px; font-weight:700;">⚠️ {msg.strip()}</div>'
                else:
                    fault_html = '<div style="color:#B58863; margin-top:10px;">✅ STATUS: NOMINAL</div>'

                st.markdown(f"""
                <div class="{entry_class}">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="card-plate">{row.get('Numer Rejestracyjny', 'N/A')}</span>
                        <span style="opacity:0.7;">{row.get('Data i Godzina').strftime('%Y-%m-%d | %H:%M')}</span>
                    </div>
                    <div style="font-size:0.9rem; margin-top:5px;">
                        OP: {row.get('Operator ID', 'N/A')} | KM: {row.get('Przebieg (km)', 0)}
                    </div>
                    {fault_html}
                    {f'<div style="margin-top:8px; font-size:0.8rem; opacity:0.6;">Uwagi: {row.get("Uwagi i Obserwacje", "")}</div>' if row.get("Uwagi i Obserwacje") else ""}
                </div>
                """, unsafe_allow_html=True)

    else:
        # WIDOK KIEROWCY
        st.markdown("<h2 class='vorteza-header'>VORTEZA PROTOCOL</h2>", unsafe_allow_html=True)
        data_gh, _ = get_remote_data()
        
        with st.form("driver_form", clear_on_submit=True):
            r = st.text_input("NUMER REJESTRACYJNY").upper()
            k = st.number_input("PRZEBIEG (KM)", step=1)
            
            check_results = {}
            if data_gh and "lista_kontrolna" in data_gh:
                for kat, punkty in data_gh["lista_kontrolna"].items():
                    with st.expander(kat.upper()):
                        for pt in punkty:
                            res = st.checkbox(pt, key=f"f_{pt}")
                            check_results[pt] = "OK" if res else "BRAK"
            
            u = st.text_area("UWAGI")
            
            if st.form_submit_button("PRZEŚLIJ PROTOKÓŁ"):
                if not r: st.error("Podaj rejestrację!")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    errs = [pt for pt, v in check_results.items() if v == "BRAK"]
                    status = "NOMINAL" if not errs else f"ALERT: {', '.join(errs)}"
                    # Zapisywanie do Google Sheets
                    if save_to_google_sheets([ts, st.session_state.user, r, k, status, u]):
                        st.success("Protokół wysłany do bazy.")
                        st.rerun()
