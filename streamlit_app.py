import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Lens Data Viewer", layout="wide")

# -----------------------
# Load secrets
# -----------------------
API_KEY = st.secrets.get("LENS_API_KEY")  # from user_lens_api_keys table
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY")  # needed for Authorization

if not API_KEY or not SUPABASE_ANON_KEY:
    st.error("Missing LENS_API_KEY or SUPABASE_ANON_KEY in st.secrets")
    st.stop()

ENDPOINT = "https://lbtoopahmulfgffzjumy.supabase.co/functions/v1/lens-data"

# -----------------------
# UI
# -----------------------
st.title("🔍 Lens Data Viewer (Lens API)")
st.caption("Authenticated using x-api-key + Supabase anon key")

table = st.text_input("Table name", "aspirex_conversations")
limit = st.number_input("Limit", 1, 100, 10)

if st.button("Fetch Data"):
    with st.spinner("Loading..."):

        params = {"table": table, "limit": limit}

        headers = {
            "x-api-key": API_KEY,                         # Your own API key
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",  # Required by Supabase gateway
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(ENDPOINT, headers=headers, params=params)

            if response.status_code != 200:
                st.error(f"Error {response.status_code}: {response.text}")
                st.stop()

            data = response.json()

            # Show table results
            if "data" in data:
                df = pd.DataFrame(data["data"])
                st.dataframe(df, use_container_width=True)
            else:
                st.json(data)

        except Exception as e:
            st.error(f"Error: {e}")
