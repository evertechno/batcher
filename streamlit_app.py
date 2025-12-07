import streamlit as st
import requests
import pandas as pd
import json

# Page configuration
st.set_page_config(
    page_title="Lens Data Viewer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Supabase Lens Data Viewer")
st.markdown("View data from your Supabase lens-data function")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Table name input
    table_name = st.text_input(
        "Table Name",
        value="aspirex_conversations",
        help="Name of the table to query"
    )
    
    # Limit input
    limit = st.number_input(
        "Limit",
        min_value=1,
        max_value=1000,
        value=10,
        help="Number of records to fetch"
    )
    
    # Fetch button
    fetch_data = st.button("🔄 Fetch Data", type="primary", use_container_width=True)

# Main content area
try:
    # Get API key from secrets
    api_key = st.secrets["api_key"]
    
    if fetch_data:
        with st.spinner("Fetching data..."):
            # Construct the URL
            url = f"https://lbtoopahmulfgffzjumy.supabase.co/functions/v1/lens-data"
            
            # Set up parameters
            params = {
                "table": table_name,
                "limit": limit
            }
            
            # Set up headers
            headers = {
                "x-api-key": api_key
            }
            
            # Make the GET request
            response = requests.get(url, params=params, headers=headers)
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                
                # Display success message
                st.success(f"✅ Successfully fetched data from {table_name}")
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["📊 Table View", "📄 JSON View", "📈 Stats"])
                
                with tab1:
                    if isinstance(data, list) and len(data) > 0:
                        # Convert to DataFrame for better display
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True, height=500)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"{table_name}_data.csv",
                            mime="text/csv"
                        )
                    elif isinstance(data, list):
                        st.info("No data returned from the query.")
                    else:
                        st.write(data)
                
                with tab2:
                    st.json(data)
                    
                    # Copy button for JSON
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json.dumps(data, indent=2),
                        file_name=f"{table_name}_data.json",
                        mime="application/json"
                    )
                
                with tab3:
                    if isinstance(data, list) and len(data) > 0:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Records", len(data))
                        
                        with col2:
                            st.metric("Fields", len(data[0].keys()) if data else 0)
                        
                        with col3:
                            st.metric("Table", table_name)
                        
                        # Show field names
                        st.subheader("Available Fields")
                        if data:
                            st.write(", ".join(data[0].keys()))
                    else:
                        st.info("No statistics available for empty dataset.")
            
            else:
                st.error(f"❌ Error: {response.status_code}")
                st.code(response.text)
                
except KeyError:
    st.error("🔑 API key not found in secrets!")
    st.info("""
    Please add your API key to Streamlit secrets:
    
    **Local development:**
    Create a file `.streamlit/secrets.toml` with:
    ```toml
    api_key = "your_api_key_here"
    ```
    
    **Streamlit Cloud:**
    Go to your app settings → Secrets and add:
    ```toml
    api_key = "your_api_key_here"
    ```
    """)
    
except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.exception(e)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit 🎈")
