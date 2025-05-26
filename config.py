import pytz
from datetime import timezone, timedelta

title = "Flex Scheduling Central"
page_icon = r"C:\Users\jklas\Downloads\icon.ico"

latest_upload = None
local_timezone = timezone(timedelta(hours=1))

sa_columns = [
    "OFD Date",
    "Station",
    "Wave",
    "Duration",
    "Cycle",
    "Service Type"
]

excl_columns = [
    "provider_id",
    "num_targeted",
    "last_saved_year",
    "last_saved_week"
]

schedule = {
    "Wednesday_1": ["12:00", 1, "09:30"],
    "Thursday_1": ["12:00", 0, "16:00"],
    "Thursday_2": ["17:00", 1, "09:30"],
    "Friday_1": ["11:00", 0, "15:30"]
}

phase2_stations_filter = [
    'DXM5',
    'DXS1',
    'DST1',
    'DBI5',
    'DXM3',
    'DLS4',
    'DWN2',
    'DME4',
    'DCR3',
    'DPR1',
    'DBI7',
    'DRR1',
    'DXN1',
    'DLU2',
    'DDD1'
]


"""
AWS VARIABLES
"""
BUCKET = "uk-eoa-pipeline"
EXCLUSION_KEY = "exclusion_dps/exclusion_dps.csv"
SA_OUTPUTS_KEY = "SA_outputs/UK_AmFlex_SA_Output.xlsx"
OUTPUT_KEY = "optimized_offers/optimized_offers_upload.csv"