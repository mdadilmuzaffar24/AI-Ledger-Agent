import streamlit as st
import pandas as pd
import gspread
from google.oauth2.credentials import Credentials
import os

# 1. PAGE CONFIG MUST BE THE ABSOLUTE FIRST COMMAND
st.set_page_config(page_title="AI Ledger Agent", page_icon="🧾", layout="wide")

# --- ☁️ THE STREAMLIT CLOUD HACK ☁️ ---
# If the app is running on the cloud, this writes your secrets into local JSON files 
# so your backend code can authenticate with Google seamlessly.
if "token_json_string" in st.secrets and not os.path.exists("token.json"):
    with open("token.json", "w") as f:
        f.write(st.secrets["token_json_string"])
        
if "credentials_json_string" in st.secrets and not os.path.exists("credentials.json"):
    with open("credentials.json", "w") as f:
        f.write(st.secrets["credentials_json_string"])
# -------------------------------------

from main import run_agent

# ⚠️ YOUR SPREADSHEET ID
SPREADSHEET_ID = '1fNOrk4kBvVjd11pu8eJJnihQLydiIuaW-hjkpGoAK6E'

# --- Header ---
st.title("🤖 AI Automated Ledger Agent")
st.markdown("Automated ingestion and structuring of unstructured PDF invoices via **Llama 3.1**.")
st.divider()

# --- Data Fetching Function ---
@st.cache_data(ttl=5)
def load_ledger_data():
    if not os.path.exists('token.json'):
        return pd.DataFrame()
    
    try:
        creds = Credentials.from_authorized_user_file('token.json')
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        return pd.DataFrame()

# Load the data safely
df = load_ledger_data()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Agent Control Panel")
    st.write("Trigger the Llama 3.1 ingestion pipeline to scan the inbox.")
    
    if st.button("🚀 Process Inbox Now", type="primary"):
        with st.status("Initializing AI Agent...", expanded=True) as status:
            st.write("🔍 Searching inbox for unread PDFs...")
            try:
                run_agent() # Run the backend
                status.update(label="✅ Processing Complete!", state="complete", expanded=False)
                st.cache_data.clear() # Clear cache so new data shows up instantly
                st.rerun() # Refresh the dashboard
            except Exception as e:
                status.update(label="❌ Error occurred", state="error")
                st.error(f"Details: {e}")

# --- Main Dashboard Rendering ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    
    # Safely handle column calculations even if the sheet is missing data
    current_balance = float(df.iloc[-1]['Balance']) if 'Balance' in df.columns and len(df) > 0 else 0.0
    total_invoices = len(df)
    total_debits = df['Debit'].sum() if 'Debit' in df.columns else 0.0
    
    col1.metric(label="💰 Current Account Balance", value=f"${current_balance:,.2f}")
    col2.metric(label="📄 Total Invoices Processed", value=f"{total_invoices}")
    col3.metric(label="📉 Total Money Out (Debits)", value=f"${total_debits:,.2f}")

    st.write("") # Spacer

    tab1, tab2 = st.tabs(["📋 Live Ledger", "📈 Balance History"])
    
    with tab1:
        st.dataframe(df, hide_index=True)
        
    with tab2:
        if 'Date' in df.columns and 'Balance' in df.columns:
            chart_data = df[['Date', 'Balance']].set_index('Date')
            st.line_chart(chart_data, color="#2e86c1")
        else:
            st.warning("Missing 'Date' or 'Balance' columns in Google Sheet to generate chart.")
else:
    # Error Handling UI
    if not os.path.exists('token.json'):
        st.error("⚠️ token.json not found! Please check your Streamlit Secrets.")
    else:
        st.info("📭 The ledger is currently empty. Send a test invoice to your email and click 'Process Inbox Now'.")