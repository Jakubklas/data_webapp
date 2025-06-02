import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import time
from src.config import *
from src.utils.utils import *
from src.s3_utils import get_s3_object, save_to_s3
from src.services.eoa_lambda import invoke_offer_prioritization

def EOA_Upload_Page():

    # Initialize User Session
    if 'upload_time' not in st.session_state:
        st.session_state.upload_time = None
    st.session_state["CHUNKS"] = 150
    st.session_state["OFFERS_PER_DP"] = 3
    st.session_state["WEEKLY_DP_TARGETS"] = 2

    # Create headline
    st.title("Exclusive Offer Allocation")
    
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
            st.stop()

        # Buttons Section
        st.divider()
        col1, col2, _= st.columns(3)

        with col1:
            # SA Upload Button
            try:
                if st.button("Upload & Distribute Offers"):
                    with st.spinner("Uploading...", show_time=True):
                        success = save_to_s3(df, BUCKET, SA_OUTPUTS_KEY, format="xlsx")
                        if success:
                            st.session_state.upload_time = datetime.now(timezone.utc)
                        else:
                            st.error("❌ Upload Failed.")
                            st.stop()

                    # Lambda invocation
                    with st.spinner(text="Distributing these offers...", show_time=True):
                        response = invoke_offer_prioritization(
                                    st.session_state.CHUNKS,
                                    st.session_state.OFFERS_PER_DP,
                                    st.session_state.WEEKLY_DP_TARGETS
                                )
                        if response["statusCode"] != 200:
                            st.error("There was a problem whilte dtistributing offers.")
                            st.stop()

                    # Waiting for offers to be saved
                    with st.spinner(text="Saving offers...", show_time=True):
                        while True:
                            status, latest = check_for_new_offers(st.session_state.upload_time)
                            if status:
                                latest_df = get_s3_object(BUCKET, OUTPUT_KEY)
                                
                                csv_bytes = latest_df.to_csv(index=False).encode("utf-8")
                                ts = datetime.now(timezone.utc).strftime("%d-%m-%Y_%H-%M-%S")
                                filename = f"optimized_offers_{ts}.csv"
                                break
                            else:
                                time.sleep(5)

                    st.info(f"🔄 Latest Offers available from: {latest}")
                    if st.download_button(
                            label="Download Optimized Offers",
                            data=csv_bytes,
                            file_name=filename,
                            mime="text/csv"
                        ):
                        st.success("✅ Download Successful..")

            except Exception as e:
                st.error(f"Section Error: {e}")

if __name__ == "__main__":
    EOA_Upload_Page()