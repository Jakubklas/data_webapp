import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime
import pytz

import config as cfg
from src.utils.aws_utils.s3_utils import S3Handler
from src.utils.aws_utils.dynamo_utils import Config, Exclusions
from src.utils.aws_utils.lambda_utils import lambda_invoke
from src.utils.aws_utils.auth import LocalAuth

try:
    auth = LocalAuth(cfg.KEY_PATH, manual_auth=True)
except:
    st.error(f"VPN Connection is necessary for this program to run as intended.")
lmbd_client = auth.get_client("lambda")
dynamo_resource = auth.get_resource("dynamodb")
s3_client = auth.get_client("s3")

s3 = S3Handler(bucket=cfg.BUCKET, client=s3_client)
ddb_cfg = Config(resource=dynamo_resource)


def Settings_Page():

    # Config State:
    up_to_date = True
    for var in ["offers_per_dp", "weekly_dp_targets", "risk_threshold", "timezone"]:    
        if var not in st.session_state:
            up_to_date = False
    if not up_to_date:
        try:
            eoa_config = {item["config"]: item["value"] for item in ddb_cfg.get_config()}
            st.session_state.offers_per_dp = int(eoa_config["offers_per_dp"])
            st.session_state.weekly_dp_targets = int(eoa_config["weekly_dp_targets"])
            st.session_state.risk_threshold = float(eoa_config["risk_threshold"])
            st.session_state.timezone = pytz.timezone(eoa_config["timezone"])
        except Exception as e:
            st.error(f"Failed to fetch the current configuration due to : \n{e}")


    st.title("Settings")

    st.header("Targeting Configuration", divider="gray")
    st.write("Configure the way Exclusive offers are sent to DPs")

    col1, col2 = st.columns([1,1])

    with col1:
        try:
            response = ddb_cfg.get_config()
            eoa_config = {item["config"]: item["value"] for item in response}
        except Exception as e:
            st.error(f"Failed to fetch the current configuration due to : \n{e}")
        
        st.session_state.offers_per_dp = st.number_input("Maximum offers per target", min_value=1, max_value=6, value=st.session_state.offers_per_dp)
        st.session_state.weekly_dp_targets = st.number_input("Maximum DP targets per week", min_value=1, max_value=4, value=st.session_state.weekly_dp_targets)
        st.session_state.risk_threshold = st.number_input("Minimum risk threshold", min_value=0.1, max_value=1.0, value=st.session_state.risk_threshold)

        if st.button("Save Configuration"):
            try:
                input_data = {
                    "offers_per_dp": st.session_state.offers_per_dp,
                    "weekly_dp_targets": st.session_state.weekly_dp_targets,
                    "risk_threshold": st.session_state.risk_threshold
                }
                
                response = ddb_cfg.index_config(input_data)
                if response["fail"]:
                    st.success(f"Success: {response["success"]}")
                    st.error(f"Errors: {response["fail"]}")
                else:
                    st.success(f"Targetting settings saved successfully")
            except Exception as e:
                st.error(f"Problem saving the new settings due to: \n{e}")

    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write(
        f"""
        Exclusive Offers will target each DP <b>maximum {st.session_state.weekly_dp_targets}</b> times per week
        with  <b>maximum {st.session_state.offers_per_dp} offers</b> sent to each DP. DPs with <b>more than {int(st.session_state.risk_threshold*100)}%</b>
        probability of disengaging will be considered "at risk" and will be targetd with priority.
        """,
        unsafe_allow_html=True
        )


    st.write(" ")
    st.header("Exclusions", divider="gray")

    uploaded_file = st.file_uploader(
        label = "Exclude specific DPs from EOA targeting for the current week.",
        type=["csv"],
        accept_multiple_files=False
        )
    
    if uploaded_file:
        if "ddb_excl" not in st.session_state:
            st.session_state.ddb_excl = Exclusions(dynamo_resource, st.session_state.timezone)

        try:
            providers = pd.read_csv(uploaded_file)["provider_id"].dropna().astype(str).to_list()
            response = st.session_state.ddb_excl.fully_exclude_providers(providers)
            st.info(f"File uploaded. {response}")
        except Exception as e:
            st.error(f"Failed to upload provider exclusions due to:\n{e}")


    buffer = StringIO()
    empty_df = pd.DataFrame(columns=["provider_id"])
    empty_df.to_csv(buffer, index=False)
    buffer.seek(0)

    col1, col2 = st.columns([1,1])
    with col1:
        st.download_button(
            label="Download CSV template",
            file_name=f"EOA_DP_Exclusions_{datetime.now().strftime('%d_%m_%Y')}.csv",
            data=buffer.getvalue(),
            mime="text/csv"
        )

    if "confirm_wipe" not in st.session_state:
        st.session_state.confirm_wipe = False

    with col1:
        if st.button("Wipe this week’s exclusions"):
            st.session_state.confirm_wipe = True

        if st.session_state.confirm_wipe:
            st.info("⚠️ Are you sure? This will erase the offers memory for this week, causing us to target some DPs more times than the current configured maximum.")
            yes, no = st.columns(2)

            with yes:
                if st.button("Yes, wipe"):
                    if "ddb_excl" not in st.session_state:
                        st.session_state.ddb_excl = Exclusions(dynamo_resource, st.session_state.timezone)

                    # Perform the action
                    command = {
                        "run": "remove_all_exclusions"
                    }
                    response = st.session_state.ddb_excl.remove_all_exclusions()
                    st.success(f"Removed {response["success"]} excluded DPs.")
                    # Turn off confirm mode
                    st.session_state.confirm_wipe = False

            with no:
                if st.button("No, cancel"):
                    # Just exit confirm mode
                    st.session_state.confirm_wipe = False


if __name__ == "__main__":
    Settings_Page()