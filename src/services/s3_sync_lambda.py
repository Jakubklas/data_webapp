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
def invoke_offer_prioritization():
    """
    This lambda synchronizes data in the back-end
    """
    return None


# Only to test things out...
if __name__ == "__main__":
    invoke_offer_prioritization()