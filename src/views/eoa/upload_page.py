import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import time

import config as cfg
from src.utils.general_utils.utils import preprocess_eoa_upload
from src.utils.aws_utils.auth import LocalAuth
from src.utils.aws_utils.s3_utils import S3Handler
from src.utils.aws_utils.sf_utils import stepfunction_invoke
from src.utils.aws_utils.lambda_utils import lambda_invoke

try:
    auth = LocalAuth(cfg.KEY_PATH, manual_auth=True)
except:
    st.error(f"VPN Connection is necessary for this program to run as intended.")

def EOA_Upload_Page():

    if "sf_client" not in st.session_state:
        st.session_state.sf_client = auth.get_client("stepfunctions")
    if "s3_client" not in st.session_state:
        st.session_state.s3_client = auth.get_client("s3")
    if "s3_resource" not in st.session_state:
        st.session_state.s3_resource = auth.get_resource("s3")

    s3 = S3Handler(cfg.BUCKET, st.session_state.s3_client)

    # Create headline
    st.title("Exclusive Offer Allocation")
    
    # File Upload Section
    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=False
    )
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")

        # File Processing and Metadata
        try:
            report = preprocess_eoa_upload(df)
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
        col1, _, _= st.columns(3)

        with col1:
            # SA Upload Button
            try:
                if st.button("Upload & Distribute Offers"):
                    with st.spinner("Uploading...", show_time=True):
                        success = s3.save_to_s3(df, cfg.SA_OUTPUTS_KEY)
                        if success:
                            st.session_state.upload_time = datetime.now(timezone.utc)
                        else:
                            st.error("❌ Upload Failed.")
                            st.stop()

                    # Step-Functions ECS Workflow invocation
                    with st.spinner(text="Distributing these offers...", show_time=True):
                        resposne = stepfunction_invoke("match_offers", cfg.SF_ARN)
                        if resposne != "SUCCEEDED":
                            st.error("There was a problem whilte dtistributing offers.")
                            st.stop()
                        else:
                            st.success("Matched DPs to available offers.")

                    # Bulk download the S3 offers files
                    st.info(f"🔄 Latest Offers available to download.")
                    if st.button("Download Optimized Offers"):
                        s3_res = S3Handler(cfg.BUCKET, st.session_state.s3_resource)
                        s3_res.bulk_download(cfg.OUTPUT_PREFIX, cfg.DOWNLOAD_PATH)
                        st.success("✅ Download Successful..")

            except Exception as e:
                st.error(f"Section Error: {e}")

if __name__ == "__main__":
    EOA_Upload_Page()