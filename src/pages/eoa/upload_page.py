import streamlit as st
import pandas as pd
from datetime import datetime, timezone

import config as cfg
from src.utils.general_utils.utils import verify_eoa_upload
from src.utils.aws_utils.auth import LocalAuth
from src.utils.aws_utils.s3_utils import S3Handler
from src.utils.aws_utils.sf_utils import stepfunction_invoke

@st.cache_resource
def get_auth():
    return LocalAuth(cfg.KEY_PATH, manual_auth=True)

@st.cache_resource
def get_clients():
    auth = get_auth()
    return {
        "sf_client": auth.get_client("stepfunctions"),
        "s3_client": auth.get_client("s3"),
        "s3_resource": auth.get_resource("s3"),
    }


def EOA_Upload_Page():
    try:
        clients = get_clients()
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}. Please ensure your VPN is on.")
        st.stop()
    
    s3 = S3Handler(cfg.BUCKET, clients["s3_client"])
    s3_res = S3Handler(cfg.BUCKET, clients["s3_resource"])

    st.title("Exclusive Offer Allocation")
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

        try:
            report = verify_eoa_upload(df)
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

        st.divider()
        col1, _, _= st.columns(3)

        with col1:
            try:
                if "uploaded" not in st.session_state:
                    st.session_state.uploaded = False
                        
                if st.button("Upload & Distribute Offers"):
                    with st.spinner("Uploading...", show_time=True):
                        success = s3.save_to_s3(df, cfg.SA_OUTPUTS_KEY)
                        if success:
                            st.session_state.upload_time = datetime.now()
                            
                        else:
                            st.error("Upload Failed.")
                            st.stop()

                    # Step-Functions ECS Workflow invocation
                    with st.spinner(text="Matching offers to providers...", show_time=True):
                        response = stepfunction_invoke("match_offers", clients["sf_client"], cfg.SF_ARN)
                        if response["status"] != "SUCCEEDED":
                            st.error(f"Failed due to: {response["cause"]}\n{response["error"]}.")
                            st.stop()
                        else:
                            st.session_state.uploaded = True


                if st.session_state.uploaded:
                    st.info("Latest Offers available to download.")
                    if st.button("Download Optimized Offers"):
                        s3_res.bulk_download(cfg.OUTPUT_PREFIX, cfg.DOWNLOAD_PATH, clients["s3_resource"])
                        st.success("Download Successful!")

            except Exception as e:
                st.error(f"Section Error: {e}")

if __name__ == "__main__":
    EOA_Upload_Page()