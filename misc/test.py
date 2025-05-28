from config import *
import boto3
import pytz

s3_client = boto3.client("s3")
london_tz = pytz.timezone("Europe/London")

def list_s3_objects(bucket, prefix):
    """List objects in S3 bucket with given prefix and return the latest updated time in datetime"""
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = response.get('Contents', [])
    if not contents:
        return None
    return contents

for i in list_s3_objects(BUCKET, OUTPUT_KEY):
    london_time = i["LastModified"].astimezone(london_tz)
    print(i["Key"], " ", london_time)
