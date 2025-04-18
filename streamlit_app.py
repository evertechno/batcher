import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile
from datetime import datetime

BATCH_SIZE = 5000

st.set_page_config(page_title="Email Batcher", layout="centered")

st.title("📧 Email ID Batcher")
st.write("Upload a CSV file with a column of email IDs. This app will split them into batches of 5,000 and provide a ZIP file with `.txt` files.")

uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

def process_emails(file):
    try:
        df = pd.read_csv(file)
        email_col = None

        # Try to auto-detect email column
        for col in df.columns:
            if 'email' in col.lower():
                email_col = col
                break

        if email_col is None:
            st.error("Could not detect an email column. Please ensure the CSV has a column with email addresses.")
            return

        emails = df[email_col].dropna().unique()

        if len(emails) == 0:
            st.warning("No valid email IDs found.")
            return

        total_batches = (len(emails) + BATCH_SIZE - 1) // BATCH_SIZE

        with tempfile.TemporaryDirectory() as tmpdir:
            txt_files = []

            for i in range(total_batches):
                batch = emails[i * BATCH_SIZE: (i + 1) * BATCH_SIZE]
                batch_file_path = os.path.join(tmpdir, f"emails_batch_{i+1}.txt")
                with open(batch_file_path, "w") as f:
                    f.write("\n".join(batch))
                txt_files.append(batch_file_path)

            zip_filename = os.path.join(tmpdir, f"email_batches_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip")
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file_path in txt_files:
                    zipf.write(file_path, os.path.basename(file_path))

            with open(zip_filename, "rb") as f:
                st.success(f"Processed {len(emails)} emails into {total_batches} batches.")
                st.download_button(
                    label="📦 Download ZIP of Batches",
                    data=f,
                    file_name="email_batches.zip",
                    mime="application/zip"
                )
    except Exception as e:
        st.error(f"Error processing file: {e}")

if uploaded_file:
    process_emails(uploaded_file)
