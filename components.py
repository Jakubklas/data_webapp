import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from config import *
from utils import *
from s3_utils import get_s3_object, save_to_s3

def create_sidebar(text="This is a sample app"):
    with st.sidebar:
        st.header(text)
        st.link_button(label = "Upload EOA", url = "https://midway-auth.amazon.com/login")
        st.link_button(label = "Settings", url = "https://midway-auth.amazon.com/login")
        st.link_button(label = "Other", url = "https://midway-auth.amazon.com/login")

def process_sa(df):
    report = {}

    # Verify Columns
    for col in df.columns:
        if col not in sa_columns:
            report["column_check"] = False
        else:
            report["column_check"] = True

    # Count offers, stations, durations
    report["offers"] = df.shape[0]
    report["stations"] = df["Station"].nunique()
    report["avg_duration"] = df["Duration"].mean()

    return report

def create_layout():

    # Initialize User Session
    if 'upload_time' not in st.session_state:
        st.session_state.upload_time = None


    # Create headline
    st.title(title)
    
    # File Upload Section
    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=False
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")

        # File Processing and Metadata
        try:
            report = process_sa(df)
            latest_upload = datetime.now().strftime("%A") + ", " + datetime.now().strftime("%H:%M")
            st.success(f"Last file uploaded: {latest_upload}")

            st.divider()
            st.write("File preview")
            st.dataframe(df.head(3))

            st.write("File stats")
            report_df = pd.DataFrame([report]).reset_index(drop=True)
            st.dataframe(report_df)
        except Exception as e:
            st.error(f"Error processing file: {e}")

        # Buttons Section
        st.divider()
        col1, col2 = st.columns([1, 1])

        with col1:
            # SA Upload Button
            try:
                if st.button("Upload & Get Offers"):
                    success = save_to_s3(df, BUCKET, SA_OUTPUTS_KEY, format="xlsx")
                    if success:
                        st.success("✅ Upload Sucsessful.")
                        st.session_state.upload_time = datetime.now(timezone.utc)
                    else:
                        st.error("❌ Upload Failed.")
            except Exception as e:
                st.error(f"Section Error: {e}")
            """
            # DP Erase Button
            try:
                if st.button("Erase Excluded DPs"):
                    success = erase_excluded_dps()
                    if success:
                        st.success("✅ DP Exclusions Erased.")
                    else:
                        st.error("❌ Failed Erasing DP Exclusions")
            except Exception as e:
                st.error(f"Section Error: {e}")
            """
        with col2:
            try:
                if "upload_time" not in st.session_state:
                    st.session_state.upload_time = None
                if st.button("Download Optimized Offers"):
                    # 3) On click, check readiness
                    if not check_for_new_offers(st.session_state.upload_time):
                        st.info("🔄 Offers are still being computed.")
                    else:
                        latest_df = get_s3_object(BUCKET, OUTPUT_KEY)
                        if latest_df is None or latest_df.empty:
                            st.error("❌ No optimized offers available.")
                        else:
                            csv_bytes = latest_df.to_csv(index=False).encode("utf-8")
                            ts = datetime.now(timezone.utc).strftime("%d-%m-%Y_%H-%M-%S")
                            filename = f"optimized_offers_{ts}.csv"

                            st.download_button(
                                label="Click here to save the file",
                                data=csv_bytes,
                                file_name=filename,
                                mime="text/csv"
                            )

            except Exception as e:
                st.error(f"❌ Error fetching or preparing download: {e}")


    

             # TODO: When a new SA file is uploaded, mark the time and only serve the new file once the optimized offers file's last_update_time is grearted than the marked upload file
             # TODO: Provide updates about offer processing in real-time
             # TODO: Add last_update_time to the optimized offers csv name.  
