import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime
from src.config import *
from src.utils.utils import *
from src.s3_utils import get_s3_object, save_to_s3, object_exists, get_json_config, save_json_config


def Settings_Page():
    st.title("Settings")

    st.header("Targeting Configuration", divider="gray")
    st.write("Configure the way Exclusive offers are sent to DPs")

    col1, col2 = st.columns([1,1])

    with col1:
        if object_exists(BUCKET, EOA_CONFIG):
            eoa_config = get_json_config(BUCKET, EOA_CONFIG)
        else:
            st.error(f"Configuration file '{EOA_CONFIG}' does not exist")
        
        OFFERS_PER_DP = st.number_input("Maximum offers per target", min_value=1, max_value=6, value=eoa_config["offers_per_dp"])
        WEEKLY_DP_TARGETS = st.number_input("Maximum DP targets per week", min_value=1, max_value=4, value=eoa_config["weekly_dp_targets"])
        RISK_THRESHOLD = st.number_input("Minimum risk threshold", min_value=0.1, max_value=1.0, value=eoa_config["risk_threshold"])
        CHUNKS = st.number_input("Offer Processing Chunks", min_value=50, max_value=300, value=eoa_config["chunk_size"])

        if st.button("Save Configuration"):
            eoa_config = {
                "offers_per_dp": OFFERS_PER_DP,
                "weekly_dp_targets": WEEKLY_DP_TARGETS,
                "risk_threshold": RISK_THRESHOLD,
                "chunk_size": CHUNKS,
            }
            
            if save_json_config(BUCKET, EOA_CONFIG, eoa_config):
                st.success("Targeting configuration was saved.")
            else:
                st.error("There was a problem saving the new settings.")

    with col2:
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(
        f"""
        Exclusive Offers will target each DP <b>maximum {WEEKLY_DP_TARGETS}</b> times per week
        with  <b>maximum {OFFERS_PER_DP} offers</b> sent to each DP. DPs with <b>more than {int(RISK_THRESHOLD*100)}%</b>
        probability of disengaging will be considered "at risk" and will be targetd with priority.
        Offers will be <b>processed in chunks of {CHUNKS}</b> for more efficient processing.
        """,
        unsafe_allow_html=True
        )

    st.write(" ")
    st.header("Exclusions", divider="gray")

    uploaded_file = st.file_uploader(
        label = "Exclude specific DPs or Stations from EOA targeting.",
        type=["csv"],
        accept_multiple_files=False
        )

    buffer = StringIO()
    empty_df = pd.DataFrame(columns=["provider_id", "station"])
    empty_df.to_csv(buffer, index=False)
    buffer.seek(0)

    col1, col2 = st.columns([1,1])
    with col1:
        st.download_button(
            label="Download CSV template",
            file_name=f"EOA_Exclusions_{datetime.now().strftime('%d_%m_%Y')}.csv",
            data=buffer.getvalue(),
            mime="text/csv"
        )
    with col2:
        st.download_button(
            label="Download Current Exclusions",
            file_name=f"EOA_Exclusions_{datetime.now().strftime('%d_%m_%Y')}.csv",
            data= get_s3_object(BUCKET, EXCLUSION_KEY).to_csv(index=False).encode("utf-8"),
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
                    # Perform the action
                    save_to_s3(pd.DataFrame(columns=excl_columns),
                            BUCKET, EXCLUSION_KEY, format="csv")
                    st.success("✅ DP Exclusions Erased.")
                    # Turn off confirm mode
                    st.session_state.confirm_wipe = False

            with no:
                if st.button("No, cancel"):
                    # Just exit confirm mode
                    st.session_state.confirm_wipe = False


if __name__ == "__main__":
    Settings_Page()