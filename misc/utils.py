import pandas as pd
from datetime import timezone
from config import *
from s3_utils import save_to_s3, list_s3_objects

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