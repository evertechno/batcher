import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Lens Data Viewer", layout="wide")

# -----------------------
# Load secrets
# -----------------------
API_KEY = st.secrets.get("API_KEY")  # your x-api-key
SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY")  # needed for Authorization

if not API_KEY or not SUPABASE_SERVICE_KEY:
    st.error("Missing API_KEY or SUPABASE_SERVICE_KEY in st.secrets.")
    st.stop()

# -----------------------
# Endpoint
# -----------------------
ENDPOINT = "https://lbtoopahmulfgffzjumy.supabase.co/functions/v1/lens-data"

# -----------------------
# UI
# -----------------------
st.title("🔍 Lens Data Viewer (Supabase Edge Function)")
st.caption("Reads API keys from st.secrets")

table_name = st.text_input("Table name", value="aspirex_conversations")
limit = st.number_input("Limit", min_value=1, max_value=1000, value=10, step=1)

if st.button("Fetch Data"):
    with st.spinner("Fetching data..."):

        url = f"{ENDPOINT}?table={table_name}&limit={limit}"

        headers = {
            "x-api-key": API_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                st.error(f"Error {response.status_code}: {response.text}")
            else:
                data = response.json()

                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.success(f"Fetched {len(df)} rows.")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.json(data)

        except Exception as e:
            st.error(f"Error: {e}")
