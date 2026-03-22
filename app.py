import streamlit as st
import pandas as pd

# 1. PAGE CONFIG MUST BE THE ABSOLUTE FIRST COMMAND
st.set_page_config(page_title="AI Ledger Agent", page_icon="🧾", layout="wide")

# --- Header ---
st.title("🤖 AI Automated Ledger Agent")
st.markdown("Automated ingestion and structuring of complex multi-page PDF invoices via **Llama 3.1**.")
st.info("ℹ️ **Portfolio Demo:** This is a read-only dashboard. The AI extraction backend runs locally to protect Gmail OAuth credentials. Check the GitHub README for the video demonstration of the live pipeline!")
st.divider()

# --- Data Fetching Function (Reads local CSV instead of Google API) ---
@st.cache_data
def load_ledger_data():
    try:
        # Reads the static CSV you downloaded
        df = pd.read_csv('demo_data.csv')
        return df
    except Exception as e:
        st.error(f"Could not load demo data: {e}")
        return pd.DataFrame()

# Load the data safely
df = load_ledger_data()

# --- Main Dashboard Rendering ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    
    # Safely handle column calculations
    current_balance = float(df.iloc[-1]['Balance']) if 'Balance' in df.columns and len(df) > 0 else 0.0
    total_invoices = len(df)
    total_debits = df['Debit'].sum() if 'Debit' in df.columns else 0.0
    
    col1.metric(label="💰 Current Account Balance", value=f"${current_balance:,.2f}")
    col2.metric(label="📄 Total Invoices Processed", value=f"{total_invoices}")
    col3.metric(label="📉 Total Money Out (Debits)", value=f"${total_debits:,.2f}")

    st.write("") # Spacer

    tab1, tab2 = st.tabs(["📋 Extracted Ledger Data", "📈 Balance History"])
    
    with tab1:
        st.dataframe(df, hide_index=True)
        
    with tab2:
        if 'Date' in df.columns and 'Balance' in df.columns:
            chart_data = df[['Date', 'Balance']].set_index('Date')
            st.line_chart(chart_data, color="#2e86c1")
        else:
            st.warning("Missing columns for chart generation.")
else:
    st.warning("⚠️ demo_data.csv not found. Please add it to the repository.")