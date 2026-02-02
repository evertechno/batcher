import streamlit as st
import requests
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Lens Data Viewer", layout="wide", page_icon="🔍")

# --- Load Secrets ---
API_KEY = st.secrets.get("LENS_API_KEY")  # x-api-key
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY")  # Bearer Token

if not API_KEY or not SUPABASE_ANON_KEY:
    st.error("Missing LENS_API_KEY or SUPABASE_ANON_KEY in st.secrets")
    st.stop()

# --- Configuration ---
BASE_URL = "https://lbtoopahmulfgffzjumy.supabase.co/functions/v1/lens-api"
headers = {
    "x-api-key": API_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
}

# --- UI Layout ---
st.title("🔍 Lens Data Viewer")
st.caption("Accessing Lens API for Regulatory and Table Data")

# Sidebar for Navigation
st.sidebar.header("Data Source")
option = st.sidebar.selectbox(
    "Select Endpoint",
    ("Generic Table", "SEBI Circulars", "Regulatory Benchmarks")
)

limit = st.sidebar.number_input("Result Limit", 1, 100, 10)

# --- Logic ---

if option == "Generic Table":
    table_name = st.text_input("Table Name", "aspirex_conversations")
    if st.button("Fetch Table Data"):
        with st.spinner(f"Fetching from {table_name}..."):
            params = {"table": table_name, "limit": limit}
            try:
                response = requests.get(BASE_URL, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data.get("data", data))
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

elif option == "SEBI Circulars":
    source = st.selectbox("Source", ["sebi", "rbi", "irda"])
    if st.button("Fetch Circulars"):
        with st.spinner("Fetching Circulars..."):
            params = {"source": source, "limit": limit}
            try:
                # Appending /circulars to the base URL
                response = requests.get(f"{BASE_URL}/circulars", headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    # Snippet 1 returns data directly or in a 'data' key
                    df = pd.DataFrame(data.get("data", data) if isinstance(data, dict) else data)
                    st.success(f"Showing last {limit} {source.upper()} circulars")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

elif option == "Regulatory Benchmarks":
    if st.button("Fetch Benchmarks"):
        with st.spinner("Fetching Benchmarks..."):
            params = {"limit": limit}
            try:
                # Appending /regulatory_benchmarks to the base URL
                response = requests.get(f"{BASE_URL}/regulatory_benchmarks", headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data.get("data", data) if isinstance(data, dict) else data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

# --- Footer ---
st.divider()
st.info("Ensure your Supabase Edge Function is deployed and the routing for /circulars and /regulatory_benchmarks is correctly handled.")
