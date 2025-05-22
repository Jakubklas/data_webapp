import pandas as pd
from datetime import timezone
from config import *
from s3_utils import save_to_s3, list_s3_objects

def erase_excluded_dps():
    empty_df = pd.DataFrame(columns=excl_columns)
    save_to_s3(empty_df, BUCKET, EXCLUSION_KEY)
    return {
        "message": "Exclusion DPs have been erased for this week." 
    }

def check_for_new_offers(upload_time):

    try:
        latest = list_s3_objects(BUCKET, SA_OUTPUTS_KEY)
        if latest is None or upload_time is None:
            return False
        
        if latest.tzinfo is None:
            latest = latest.replace(tzinfo=timezone.utc)
        if upload_time.tzinfo is None:
            upload_time = upload_time.replace(tzinfo=timezone.utc)

        print(f"Latest available file from {latest}")
        return latest >= upload_time

    except Exception as e:
        print(f"Error getting the newest S3 file: {e}")
        return False