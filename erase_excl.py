import pandas as pd
from config import *
from s3_utils import save_to_s3

def erase_excluded_dps():
    empty_df = pd.DataFrame(columns=excl_columns)
    save_to_s3(empty_df, BUCKET, EXCLUSION_KEY)
    return {
        "message": "Exclusion DPs have been erased for this week." 
    }
