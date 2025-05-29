import streamlit as st
import pandas as pd
from datetime import timezone
from src.config import *
from src.s3_utils import save_to_s3, list_s3_objects

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

def erase_excluded_dps():
    empty_df = pd.DataFrame(columns=excl_columns)
    save_to_s3(empty_df, BUCKET, EXCLUSION_KEY)
    return {
        "message": "Exclusion DPs have been erased for this week." 
    }

def check_for_new_offers(upload_time):

    try:
        latest = list_s3_objects(BUCKET, OUTPUT_KEY)
        latest_local = latest.astimezone(local_timezone)

        if latest is None or upload_time is None:
            return False, latest_local

        # Ensure both datetimes are timezone-aware in UTC
        if latest.tzinfo is None:
            latest = latest.replace(tzinfo=timezone.utc)
        if upload_time.tzinfo is None:
            upload_time = upload_time.replace(tzinfo=timezone.utc)

        print(f"Latest available file from {latest_local}")
        return (latest >= upload_time), latest_local

    except Exception as e:
        print(f"Error getting the newest S3 file: {e}")
        return False, None
    

def separate_text_input(text, item_length=None):
    try:
        if len(text) == item_length:
            separator = None
        elif "," in text:
            separator = ","
        elif ", " in text:
            separator = ", "
        elif " " in text:
            separator = " "
        elif "\n" in text:
            separator = "\n"
        elif "\t" in text:
            separator = "\t"

        result = text.split(sep=separator)
        outliers = [item for item in result if len(item) != item_length]

        if len(outliers) != 0:
            st.error(f"Items not found: {outliers}")

        return result
    except Exception as e:
        st.error(f"Unexpected text format. Separate values by commas, spaces, new-lines, or tabs. \n {e}")

@st.dialog("⚠️ Please confirm", width="small")
def confirm_dialog(session_variable, message, yes, no):
    st.write(message)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(yes):
            session_variable = True
            return session_variable
            st.rerun()
    with c2:
        if st.button(no):
            session_variable = False
            st.stop()
            return session_variable
            