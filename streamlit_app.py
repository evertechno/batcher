import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Lens Data Viewer", layout="wide")

# -----------------------
# Load API Key from st.secrets
# -----------------------
API_KEY = st.secrets.get("API_KEY", None)

if not API_KEY:
    st.error("API_KEY not found in st.secrets. Please add it before running the app.")
    st.stop()

# -----------------------
# Streamlit UI
# -----------------------
st.title("🔍 Lens Data Viewer")
st.caption("Fetch data from Supabase Edge Function using API key from st.secrets")

table_name = st.text_input("Table name", value="aspirex_conversations")
limit = st.number_input("Limit", min_value=1, max_value=1000, value=10, step=1)

endpoint = f"https://lbtoopahmulfgffzjumy.supabase.co/functions/v1/lens-data"

if st.button("Fetch Data"):
    with st.spinner("Fetching data..."):
        try:
            # Prepare request
            url = f"{endpoint}?table={table_name}&limit={limit}"
            headers = {"x-api-key": API_KEY}

            # Call Edge Function
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                st.error(f"Error: {response.status_code} - {response.text}")
            else:
                data = response.json()

                # Render data
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.success("Data fetched successfully!")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.write("Response:")
                    st.json(data)

        except Exception as e:
            st.error(f"Unexpected error: {e}")
