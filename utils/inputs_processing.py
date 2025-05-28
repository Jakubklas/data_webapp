import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
import boto3
import os
from misc.logging import log_msg
from config import *
from s3_utils import get_s3_object

class InputsProcessor():
    def __init__(self, bucket, local_files):
        self.bucket = bucket
        self.local_files = local_files
    
    @log_msg
    def sync(self):
        try:
            client = boto3.client("s3")
            for file in self.local_files:

                buffer = BytesIO()
                fmt = os.path.splitext(file)[1].lower()
                name = os.path.splitext(os.path.basename(file))[0]

                if fmt == ".txt":
                    df = pd.read_csv(file, sep="\t")
                    df.to_parquet(buffer, index=False)
                    save_fmt = ".parquet"
                elif fmt == ".csv":
                    df = pd.read_csv(file)
                    df.to_parquet(buffer, index=False)
                    save_fmt = ".parquet"
                elif fmt in [".xlsx", ".xlsm", ".xls"]:
                    save_fmt = fmt
                    with open(file, "rb") as f:
                        buffer.write(f.read())
                
                buffer.seek(0)
                client.put_object(
                    Bucket= scheduling_bucket,
                    Key = f"{name}{save_fmt}",
                    Body = buffer.getvalue(),
                    ContentType="application/octet-stream"
                    )

                print(f"✅ Uploaded: {name}")

                return True
        except Exception as e:
            raise e

    @log_msg
    def process_snop(self):
        try:
            df = get_s3_object(self.bucket, "UK_CVP_Plan_14d.parquet")

            cols = ["joinkey", "week", "ofd_date", "station", "cycle", "value", "flex_share_cvp", "flex_spr_cvp", "source"]

            df["ofd_volume"] = df["ofd_volume"].astype(int)
            df["week"] = pd.to_datetime(df["ofd_date"]).dt.isocalendar().week
            df["flex_spr"] = df["flex_spr"].astype(int, errors="ignore")
            df["flex_routes_available"] = df["flex_routes_available"].astype(int, errors="ignore")
            df["source"] = "snop_fcst"
            df = df.rename(columns={
                "flex_share": "flex_share_cvp",
                "flex_spr": "flex_spr_cvp",
                "ofd_volume": "value"
            })

            df["joinkey"] = df["ofd_date"].astype(str) + df["station"] + df["cycle"]
            df = df[cols]
            self.snop_fcst = df.copy()
            return self

        except Exception as e:
            raise e
    
    @log_msg
    def process_co_nd(self):
        try:
            df = get_s3_object(self.bucket, "UK_AMZL_CO_Volume_Forecast.parquet")

            cols = ["joinkey", "ofd_date", "station", "cycle", "value", "source"]

            df["published"] = pd.to_datetime(df["published"])
            df = df.loc[df.groupby(["ofddate", "stationcode", "wavegroupname"])["published"].idxmax()]
            df["source"] = "co_fcst"
            df = df.rename(columns={
                "ofddate": "ofd_date",
                "stationcode": "station",
                "wavegroupname": "cycle",
                "volume": "value"
            })

            df["joinkey"] = df["ofd_date"] + df["station"] + df["cycle"]
            df = df[cols]
            self.co_nd_fcst = df.copy()
            return self

        except Exception as e:
            raise e
    
    @log_msg
    def process_co_sd(self):
        try:
            df = get_s3_object(self.bucket, "SD_forecaster_daily_logs.parquet")

            cols = ["joinkey", "ofd_date", "station", "cycle", "value", "source"]

            # Rename columns first
            df = df.rename(columns={
                "Node": "station",
                "OFD_DATE": "ofd_date",
                "Expected OFD ": "value"
            })

            # Filter for UK
            df = df[df["Country"] == "UK"]

            # Filter for today and tomorrow
            today = datetime.today().date()
            tomorrow = today + timedelta(days=1)
            df = df[df["ofd_date"].isin([today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")])]

            # Cycle naming
            df["cycle"] = "CYCLE_SD_" + df["Cycle"]

            # Joining Key
            df["joinkey"] = df["ofd_date"] + df["station"] + df["cycle"]
            df["source"] = "co_fcst"
            df = df[cols]
            self.co_sd_fcst = df.copy()
            return self
        
        except Exception as e:
            raise e

    @log_msg
    def join_forecasts(self):
        try:
            forecasts = pd.concat(
                [self.snop_fcst, self.co_nd_fcst, self.co_sd_fcst],
                axis=0,
                ignore_index=True,
                sort=False
            )

            # Separate Column for SNOP FCST (2W, for weely SA)
            cond_1 = forecasts["source"] == "snop_fcst"
            forecasts["snop_fcst"] = forecasts["value"][cond_1]

            # Separate Column for CO FCST (48H, for D-2 SA)
            cond_2 = forecasts["source"] == "co_fcst"
            forecasts["co_fcst"] = forecasts["value"][cond_2]

            # Ensuring each row has its Flex Share and SPR
            forecasts = forecasts.drop(["flex_share_cvp", "flex_spr_cvp"], axis=1)
            forecasts = forecasts.merge(
                self.snop_fcst[["joinkey", "flex_share_cvp", "flex_spr_cvp"]],
                how="left",
                on="joinkey"
            )
            self.forecasts = forecasts
            return self 

        except Exception as e:
            raise e
    
    @log_msg    
    def process_scms(self):
        try:
            df = get_s3_object(self.bucket, "UK_AMZL_Flex_SCMS_Attributes_21d.parquet")

            cols = ["joinkey", "week", "day", "ofd_date", "station", "cycle", "wave_capacity", "wave_start_time", "wave_frequency", "wave_end_time", "valid_from", "wave_max"]

            df = df.rename(columns={
                "start_time": "wave_start_time",
                "end_time": "wave_end_time",
                "max_wave_capacity": "wave_capacity"
            })

            df["week"] = pd.to_datetime(df["ofd_date"]).dt.isocalendar().week
            df["wave_start_time"] = pd.to_datetime(df["wave_start_time"], format="%H:%M").dt.strftime("%H:%M")
            df["wave_frequency"] = pd.to_timedelta(df["wave_frequency"]).dt.total_seconds()/60
            df["wave_end_time"] = pd.to_datetime(df["wave_end_time"], format="%H:%M").dt.strftime("%H:%M")
            df["valid_from"] = pd.to_datetime(df["valid_from"], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")

            df["wave_minutes"] = (pd.to_datetime(df["wave_end_time"], format="%H:%M") - pd.to_datetime(df["wave_start_time"], format="%H:%M")).dt.total_seconds()/60
            df["wave_minutes"] = df["wave_minutes"].astype(int)

            df["max_wave_count"] = (df["wave_minutes"] / df["wave_frequency"]).astype(int, errors="ignore")
            max_wave_cond = df["max_wave_count"] > 15
            df["wave_max"] = df["max_wave_count"]
            df.loc[max_wave_cond, "wave_max"] = 15

            df["joinkey"] = df["ofd_date"] + df["station"] + df["cycle"]
            df = df[cols]
            self.scms_data = df.copy()
            return self

        except Exception as e:
            raise e
    
    @log_msg    
    def process_utr(self):
        try:
            df = get_s3_object(self.bucket, "UTRChangeLog.xlsx", sheet_name="DailyRange")

            df = df.rename(columns={
                "JoinKey": "joinkey",
                "Buffer": "utr_buffer",
                "OFDDate": "ofd_date",
                "Station": "station",
                "Cycle": "cycle"
                })

            df["ofd_date"] = pd.to_datetime(df["ofd_date"], format="%Y-%m-%d")
            df["joinkey"] = df["ofd_date"].astype(str) + df["station"] + df["cycle"]
            df = df[df["ofd_date"].between(pd.Timestamp.today().normalize(), pd.Timestamp.today().normalize() + pd.Timedelta(days=21))]

            self.utr_data = df.copy()
            return self
        
        except Exception as e:
            raise e

    @log_msg    
    def process_spr(self):
        try:
            df = get_s3_object(self.bucket, "SPR Planner3.xlsx", header=1, sheet_name="Data")

            cols = ["cycle", "station", "Calc SPR"]
            df = df[cols]
            df = df.rename(columns={
                "Calc SPR": "calc_spr"
            })

            self.spr_data = df.copy()
            return self
            
        except Exception as e:
            raise e

    @log_msg    
    def process_sa_table(self):
        try:
            df = get_s3_object(self.bucket, "UK_Flex_Schedule_Ahead_Percentage.xlsm")

            df = df.rename(columns={
                "DOW": "day",
                "Station": "station",
                "Cycle": "cycle",
                "SA% EOA": "sa%_eoa",
                "SA% WK": "sa%_week",
                "SA% D3": "sa%_d3",
                "SA% D2": "sa%_d2",
                "SA% D1": "sa%_d1",
                "SA% D0": "sa%_d0"
            })

            df = df.fillna(0)
            self.sa_table = df.copy()
            return self

        except Exception as e:
            raise e
    
    @log_msg
    def process_waveplan(self):
        try:
            df = get_s3_object(self.bucket, "LPnS_Wave_Optimizer_V4.xlsm", header=1, sheet_name="WavePlanSD")

            columns = [
                "Date", "Station", "Cycle",
                "D-1", "D-2", "D-3", "D-4", "D-5", "D-6", "D-7", "D-8", "D-9", "D-10", "D-11", "D-12", "D-13", "D-14", "D-15",
                "C-1", "C-2", "C-3", "C-4", "C-5", "C-6", "C-7", "C-8", "C-9", "C-10", "C-11", "C-12", "C-13", "C-14", "C-15"
                ]

            df = df[columns]
            df.columns = [col.strip().replace(" ", "_").replace("-", "_") for col in df.columns]
            df = df.rename(columns={
                "Date": "ofd_date",
                "Station": "station",
                "Cycle": "cycle"
            })

            df["joinkey"] = df["ofd_date"].astype(str) + df["station"] + df["cycle"]
            df = df.fillna(0)
            self.wave_plan = df.copy()
            return self
        
        except Exception as e:
            raise e
    
    @log_msg
    def combine_data(self):
        try:
            # Get all columns in theri original order
            cols = list(
                dict.fromkeys(
                    list(self.scms_data.columns)
                    + list(self.forecasts.columns)
                    + list(self.utr_data.columns) 
                    + list(self.spr_data.columns) 
                    + list(self.sa_table.columns) 
                    + list(self.wave_plan.columns)
                    )
                )

            # Start with SCMS data and join Forecasts

            df = self.scms_data.merge( # Join SCSMS + Forecasts
                self.forecasts,
                on="joinkey",
                how="left",
                suffixes=('', '_a')
            ) \
                .merge(  # Join UTR buffers
                self.utr_data,
                on="joinkey",
                how="left",
                suffixes=('', '_b')
            ) \
                .merge( # Join SPR Plan
                self.spr_data,
                on=["cycle", "station"],
                how="left",
                suffixes=('', '_c')
            ) \
                .merge( # Join SA Table
                self.sa_table,
                on=["day", "station", "cycle"],
                how="left",
                suffixes=('', '_d')
            ) \
                .merge( # Join Wave Plan
                self.wave_plan,
                on="joinkey",
                how="left",
                suffixes=('', '_e')
            )

            # Drop unnecesary cols Sort by Date/Cycle/Station
            df = df[cols].drop("joinkey", axis=1)
            df = df.sort_values(["ofd_date", "cycle", "station"], ascending=False)

            # Only include current Week and next week
            cw = datetime.now().isocalendar().week
            nw = cw + 1
            relevant_weeks = df["week"].isin([cw, nw])

            df = df[relevant_weeks]
            self.scheduling_inputs = df.copy()
            return self.scheduling_inputs
                
        except Exception as e:
            raise e
        