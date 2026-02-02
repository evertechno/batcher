import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Lens API Explorer", layout="wide", page_icon="🔍")

# --- Load Secrets ---
API_KEY = st.secrets.get("LENS_API_KEY")
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY")

if not API_KEY or not SUPABASE_ANON_KEY:
    st.error("Missing LENS_API_KEY or SUPABASE_ANON_KEY in st.secrets")
    st.stop()

# --- Configuration Mapping (Matching Deno Script) ---
BASE_URL = "https://lbtoopahmulfgffzjumy.supabase.co/functions/v1/lens-api"

CIRCULAR_SOURCES = [
    'sebi', 'rbi', 'sec', 'fca', 'mas', 'sfc', 'bafin', 
    'cbn', 'hkma', 'ibbi', 'iosco', 'irda', 'nse'
]
RSS_SOURCES = ['boj', 'eiopa', 'bis']

# --- UI Sidebar ---
st.sidebar.header("🛠️ API Configuration")
endpoint = st.sidebar.selectbox(
    "Select Endpoint",
    ["circulars", "invector_json", "ai_analyzed_datasets", "regulatory_benchmarks", "sources"]
)

st.sidebar.divider()
st.sidebar.header("🔍 Filters")

# Global Filters
limit = st.sidebar.slider("Limit", 1, 100, 25)
search = st.sidebar.text_input("Search (Title)", "")

# Conditional Filters based on Endpoint
params = {"limit": limit}
if search:
    params["search"] = search

if endpoint in ["circulars", "invector_json", "regulatory_benchmarks"]:
    all_src = CIRCULAR_SOURCES + RSS_SOURCES if endpoint == "circulars" else CIRCULAR_SOURCES
    selected_source = st.sidebar.selectbox("Source Regulator", ["all"] + all_src)
    if selected_source != "all":
        params["source"] = selected_source

if endpoint == "circulars":
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start Date", value=None)
    end_date = col2.date_input("End Date", value=None)
    if start_date: params["start_date"] = start_date.strftime("%Y-%m-%d")
    if end_date: params["end_date"] = end_date.strftime("%Y-%m-%d")

if endpoint == "ai_analyzed_datasets":
    params["dataset"] = st.sidebar.text_input("Dataset Name")
    params["tags"] = st.sidebar.text_input("Tags (comma separated)")

# --- Header ---
st.title(f"🔍 Lens Explorer: `{endpoint}`")
st.caption(f"Connected to: {BASE_URL}")

# --- API Execution ---
if st.button("Run Query", type="primary"):
    headers = {
        "x-api-key": API_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }

    with st.spinner("Fetching data from Lens API..."):
        try:
            # Construct final URL
            target_url = f"{BASE_URL}/{endpoint}" if endpoint != "circulars" else f"{BASE_URL}/circulars"
            
            response = requests.get(target_url, headers=headers, params=params)
            
            if response.status_code == 200:
                res_data = response.json()
                
                # Metrics Row
                if "total" in res_data:
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Found", res_data.get("total", 0))
                    m2.metric("Returned", res_data.get("count", 0))
                    m3.metric("Response Time", response.headers.get("X-Response-Time", "N/A"))

                # Data Rendering
                if endpoint == "sources":
                    st.json(res_data)
                elif "data" in res_data:
                    df = pd.DataFrame(res_data["data"])
                    if not df.empty:
                        st.dataframe(df, use_container_width=True)
                        st.download_button(
                            "Download CSV",
                            df.to_csv(index=False),
                            file_name=f"lens_{endpoint}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No records found for this query.")
                else:
                    st.write("Response Received:")
                    st.json(res_data)
                    
            else:
                st.error(f"Error {response.status_code}")
                st.json(response.json())
                
        except Exception as e:
            st.error(f"Application Error: {str(e)}")

# --- Metadata View (Default) ---
if not st.session_state.get('run_query'):
    with st.expander("ℹ️ Endpoint Documentation"):
        st.markdown(f"""
        **Current Endpoint:** `{endpoint}`  
        **Supported Sources:** {', '.join([s.upper() for s in CIRCULAR_SOURCES])}  
        **RSS Sources:** {', '.join([s.upper() for s in RSS_SOURCES])}
        """)

st.divider()
st.info("💡 Tip: Use the 'Search' filter in the sidebar to look for specific keywords in circular titles.")
