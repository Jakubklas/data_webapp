import boto3
from botocore.exceptions import ClientError
from io import BytesIO, StringIO
import pandas as pd
import os

s3_client = boto3.client("s3")

def get_s3_object(bucket, prefix, header=0, sheet_name=0):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get('Contents', [])
        
        if len(contents) >= 1:
            # Sort by last modified and get the most recent file
            latest_file = sorted(contents, key=lambda x: x['LastModified'], reverse=True)[0]
            key = latest_file['Key']
            
            # Skip if it's just a directory
            if key.endswith('/'):
                raise ValueError(f"No files found in directory: {key}")
                
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            data = obj['Body'].read()
            
            if key.lower().endswith('.parquet'):
                return pd.read_parquet(BytesIO(data))
            elif key.lower().endswith('.csv'):
                return pd.read_csv(BytesIO(data))
            elif key.lower().endswith(('.xlsx', '.xls', '.xlsm')):
                return pd.read_excel(BytesIO(data), header=header, sheet_name=sheet_name)  # reads first sheet by default
            elif key.lower().endswith('.txt'):
                return pd.read_csv(BytesIO(data), sep='\t', encoding='utf-8')
        else:
            raise ValueError("No objects found in the prefix")
            
    except Exception as e:
        print(f"Error reading from S3: {str(e)}")
        raise

def list_s3_objects(bucket, prefix):
    """List objects in S3 bucket with given prefix and return the latest updated time in datetime"""
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = response.get('Contents', [])
    if not contents:
        return None
    latest = max(obj['LastModified'] for obj in contents)
    return latest

def save_to_s3(df, bucket, key, format):
    try:
        if format == "csv":
            buffer = StringIO()
            df.to_csv(buffer, index=False)
            body = buffer.getvalue().encode('utf-8')
            content_type = "text/csv"

        elif format in ["xlsx", "xlsm"]:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)
            body = buffer.read()
            content_type = (
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
            
        elif format == "parquet":
            buffer = BytesIO()
            df.to_parquet(buffer, index=False)
            buffer.seek(0)
            body = buffer.read()
            content_type = "application/octet-stream"

        else:
            raise ValueError(f"Unsupported format: {format}")

        response = s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=content_type
        )
    except ClientError as e:
        print(e)
        return False

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f"Successfully saved {format.upper()} to {key}")
        return True
    else:
        print(f"Upload failed with response: {response}")
        return False

def object_exists(bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "404" or error_code == "NoSuchKey":
            return False

        raise

def refresh_inputs():
    client = boto3.client("s3")
    names = [
        r"\\ant.amazon.com\dept-eu\Amazon-Flex-Europe\Data\OE\AMZL\UTR Model\UTRChangeLog.xlsx",                             # UTR Buffers
        r"\\ant\dept-eu\TBA\UK\Business Analyses\CentralOPS\Scheduling\UK\FlexData\SPR Planner3.xlsx",                       # SPRs
        r"\\ant\dept-eu\TBA\UK\Business Analyses\CentralOPS\Scheduling\UK\FlexData\UK_Flex_Schedule_Ahead_Percentage.xlsm",  # SA Table
        r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_AMZL_Flex_SCMS_Attributes_21d.txt",                             # SCMS
        r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_CVP_Plan_14d.txt",                                              # CVP Data + 2W SnOP Forecast
        r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL\UK_CVP_Plan_All.txt",                                              # CVP Data + SnOP Forecasgott
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
        r"\\ant\dept-eu\EUCentralOPS\Volume-Management\Control Tower\Forecast\EU_SameDay\logs\SD_forecaster_daily_logs.csv", # CO 48H Forecast ND
        r"\\ant\dept-eu\EUCentralOPS\Volume-Management\Control Tower\Forecast\EU_SameDay\logs\SD_forecaster_daily_logs.csv"  # CO 48H Forecast SD
    ]

    for file in names:
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
            Bucket= "uk-flex-scheduling",
            Key = f"{name}{save_fmt}",
            Body = buffer.getvalue(),
            ContentType="application/octet-stream"
            )

        print(f"✅ Uploaded {name}.parquet")