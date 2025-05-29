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

local_files = [
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\LPnS_Model\LPnS_Wave_Optimizer_V4.xlsm",                               # LPNS Wave Plan 
    r"\\ant.amazon.com\dept-eu\Amazon-Flex-Europe\Data\OE\AMZL\UTR Model\UTRChangeLog.xlsx",                             # UTR Buffers
    r"\\ant\dept-eu\TBA\UK\Business Analyses\CentralOPS\Scheduling\UK\FlexData\SPR Planner3.xlsx",                       # SPRs
    r"\\ant\dept-eu\TBA\UK\Business Analyses\CentralOPS\Scheduling\UK\FlexData\UK_Flex_Schedule_Ahead_Percentage.xlsm",  # SA Table
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Flex_SCMS_Attributes_21d.txt",                             # SCMS
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_CVP_Plan_14d.txt",                                              # CVP Data + 2W SnOP Forecast
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_CVP_Plan_All.txt",                                              # CVP Data + SnOP Forecast
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Flex_SCMS_Attributes_120d.txt",    
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Route_Summary_SPR.txt",                                    # SPR Historicals
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Route_Planning_Agg_Pivot.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_RoBL_Data_For_UTR_Mod.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Provider_Demand.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_Siphon_Data_Pivot.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Routing_DSP_to_Flex.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Routing_DSP_to_Flex_21d.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Date_Station_Cycle.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Flex_Fill_At_Sequence.txt",
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_DEA_PM_Data_Grp_Pivot.txt",                                # DEA Data
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_RoBL_Data_For_RLD_Mod.txt",                                # RoBL Data for UTR + Reporting
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_Flex_Block_Actuals_by_Cycle.txt",                               # Historical Blocks
    r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_CO_Volume_Forecast.txt",                                   # CO 48H Forecast ND
    r"\\ant\dept-eu\EUCentralOPS\Volume-Management\Control Tower\Forecast\EU_SameDay\logs\SD_forecaster_daily_logs.csv"  # CO 48H Forecast SD
] 
locked_inputs = [
        "week", "day", "ofd_date", "station", "cycle", "sa%_eoa", "sa%_week", "sa%_d3", "sa%_d3", "sa%_d2", "sa%_d1", "sa%_d0"
    ]
pinned_inputs = [
        "week", "day", "ofd_date", "station", "cycle"
    ]

"""
AWS VARIABLES
"""
BUCKET = "uk-eoa-pipeline"
scheduling_bucket = "uk-flex-scheduling"
EXCLUSION_KEY = "exclusion_dps/exclusion_dps.csv"
SA_OUTPUTS_KEY = "SA_outputs/UK_AmFlex_SA_Output.xlsx"
OUTPUT_KEY = "optimized_offers/optimized_offers_upload.csv"