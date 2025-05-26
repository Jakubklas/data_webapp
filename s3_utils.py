import boto3
from botocore.exceptions import ClientError
from io import BytesIO, StringIO
import pandas as pd

s3_client = boto3.client("s3")

def get_s3_object(bucket, prefix):
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
            else:
                raise ValueError(f"Unsupported file type. File must be .csv or .parquet: {key}")
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

        elif format == "xlsx":
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            buffer.seek(0)
            body = buffer.read()
            content_type = (
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
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


    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f"Successfully saved CSV to {key}")
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
    path = r"\\ant\dept-eu\Amazon-Flex-Europe\EU-OE\LPnS\ETL"
    client = boto3.client("s3")
    names = [
        "UK_AMZL_Flex_SCMS_Attributes_21d",
        "UK_CVP_Plan_14d",
        "UK_CVP_Plan_All",
        "UK_AMZL_Flex_SCMS_Attributes_120d",
        "UK_AMZL_Route_Summary_SPR",
        "UK_AMZL_Route_Planning_Agg_Pivot",
        "UK_AMZL_RoBL_Data_For_UTR_Mod",
        "UK_AMZL_Provider_Demand",
        "UK_Siphon_Data_Pivot",
        "UK_AMZL_Routing_DSP_to_Flex",
        "UK_AMZL_Routing_DSP_to_Flex_21d",
        "UK_AMZL_Date_Station_Cycle",
        "UK_AMZL_Flex_Fill_At_Sequence",
        "UK_AMZL_DEA_PM_Data_Grp_Pivot",
        "UK_AMZL_RoBL_Data_For_RLD_Mod",
        "UK_Flex_Block_Actuals_by_Cycle"
    ]

    for name in names:
        buffer = BytesIO()

        file = f"{path}\{name}.txt" 
        df = pd.read_csv(file, sep="\t")
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        client.put_object(
        Bucket= "uk-flex-scheduling",
        Key = f"{name}.parquet",
        Body = buffer.getvalue(),
        ContentType="application/octet-stream"
        )

        print(f"✅ Uploaded {name}.parquet")