import boto3
import json
from botocore.config import Config
# from src.utils.logging import *

config = Config(
    connect_timeout=30,
    read_timeout=120,
    retries={'max_attempts': 3,
             'mode': 'adaptive'
             }
)

lambda_client = boto3.client('lambda', config=config)

# @log_msg
def invoke_offer_prioritization(chunk_size, offers_per_dp, weekly_dp_targets):
    """
    This lambda invokes EOA offer matching to DPs and specifies the chunk size
    in which they're processed (to memory requirements). 
    """
    function_name = 'arn:aws:lambda:us-east-1:533267382787:function:offer-prioritization'
    payload = {
        "chunk_size": chunk_size,
        "offers_per_dp": offers_per_dp,
        "weekly_dp_targets": weekly_dp_targets
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
        chunk_size = 150,
        offers_per_dp = 3,
        weekly_dp_targets = 2
    )



# python run src.services.eoa_lambda.py