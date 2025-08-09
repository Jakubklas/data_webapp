import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import time
import asyncio
from config import *
from src.utils.utils import *
from aws_utils.s3_utils import get_s3_object, save_to_s3, get_json_config
from src.services.eoa_lambda import invoke_offer_prioritization
from src.utils.aws_utils.s3_utils import S3Handler
from src.utils.aws_utils.sf_utils import stepfunction_invoke

async def distribute_offers():
    """Separate async function to handle the offer distribution process"""
    response = await invoke_offer_prioritization(
        chunk_size=st.session_state.CHUNKS,
        offers_per_dp=st.session_state.OFFERS_PER_DP,
        weekly_dp_targets=st.session_state.WEEKLY_DP_TARGETS
    )
    return response


def EOA_Upload_Page():

    # Initialize User Session
    eoa_config =  get_json_config(BUCKET, EOA_CONFIG)
    session_vars = {
        "upload_time": None, 
        "CHUNKS": eoa_config["chunk_size"], 
        "OFFERS_PER_DP": eoa_config["offers_per_dp"], 
        "WEEKLY_DP_TARGETS": eoa_config["weekly_dp_targets"]
        }
    for var, val in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = val

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
                        response = asyncio.run(distribute_offers())
                        print("Lambda Response:", response)

                        if response["statusCode"] != 200:
                            st.error("There was a problem whilte dtistributing offers.")
                            st.stop()
                        else:
                            print("Successful reponse.")

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