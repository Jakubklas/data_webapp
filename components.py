import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
from datetime import datetime, timezone
from config import *
from utils import *
from s3_utils import get_s3_object, save_to_s3


def EOA_Upload_Page():

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
            st.stop()

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

        with col2:
            try:
                if "upload_time" not in st.session_state:
                    st.session_state.upload_time = None
                if st.button("Check for new offers"):
                    # 3) On click, check readiness
                    status, latest = check_for_new_offers(st.session_state.upload_time)
                    if not status:
                        st.info(f"🔄 Latest optimized offers from {latest.strftime('%Y-%m-%d %H:%M:%S')}.")
                    else:
                        latest_df = get_s3_object(BUCKET, OUTPUT_KEY)
                        
                        if latest_df is None or latest_df.empty:
                            st.error("❌ No optimized offers available.")
                        else:
                            csv_bytes = latest_df.to_csv(index=False).encode("utf-8")
                            ts = datetime.now(timezone.utc).strftime("%d-%m-%Y_%H-%M-%S")
                            filename = f"optimized_offers_{ts}.csv"

                            st.info(f"🔄 Latest Offers available from: {latest}")
                            if st.download_button(
                                    label="Download Optimized Offers",
                                    data=csv_bytes,
                                    file_name=filename,
                                    mime="text/csv"
                                ):
                                st.success("✅ Download Successful..")

            except Exception as e:
                st.error(f"❌ Error fetching or preparing download: {e}")


def Settings_Page():
    st.title("Settings")

    st.header("Targeting Configuration", divider="gray")
    st.write("Configure the way Exclusive offers are sent to DPs")

    col1, col2 = st.columns([1,1])

    with col1:
        OFFERS_PER_DP = st.number_input("Maximum offers per target", min_value=1, max_value=6, value=3)
        WEEKLY_DP_TARGETS = st.number_input("Maximum DP targets per week", min_value=1, max_value=4, value=2)
        RISK_THRESHOLD = st.number_input("Minimum risk threshold", min_value=1, max_value=4, value=2)
        CHUNKS = st.number_input("Offer Processing Chunks", min_value=50, max_value=300, value=100)

    with col2:
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(
        f"""
        Exclusive Offers will target each DP <b>maximum {WEEKLY_DP_TARGETS}</b> times per week
        with  <b>maximum {OFFERS_PER_DP} offers</b> sent to each DP. DPs with <b>more than {RISK_THRESHOLD}</b>
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