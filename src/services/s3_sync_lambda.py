import boto3
import json
from botocore.config import Config
from src.utils.logging import *

config = Config(
    connect_timeout=30,
    read_timeout=120,
    retries={'max_attempts': 3,
             'mode': 'adaptive'
             }
)
lambda_client = boto3.client('lambda', config=config)

@log_msg
def invoke_offer_prioritization(CHUNKS, OFFERS_PER_DP, WEEKLY_DP_TARGETS):
    # Create Lambda client
    
    # Function name and payload
    function_name = 'arn:aws:lambda:us-east-1:533267382787:function:offer-prioritization'
    payload = {
        "CHUNKS": CHUNKS,
        "OFFERS_PER_DP": OFFERS_PER_DP,
        "WEEKLY_DP_TARGETS": WEEKLY_DP_TARGETS
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload
        
    except Exception as e:
        print(f"Error invoking Offer Prioritization: {str(e)}")
        return None


# Only to test things out...
if __name__ == "__main__":
    invoke_offer_prioritization(
        CHUNKS=150,
        OFFERS_PER_DP=3,
        WEEKLY_DP_TARGETS=2
    )