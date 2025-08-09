import boto3
import json


def lambda_invoke(command: dict, arn: str, region: str, client: boto3) -> str:
    """
    Invokes an intermediary lambda function to interact with
    DynanmoDB tables. Take the following format for 'command':

    {
        "run": "index_config",
        "input_data": {
            "weekly_dp_targets": 5,
            "risk_threshold": 0.25
        },
        "permanent": "false"
    }

    """
    # Verify commands & create payload dict
    commands = ["remove_all_exclusions", "fully_exclude_providers", "get_config", "index_config"]
    if command["run"] in commands:
        payload = command
    else:
        print(f"Incorrect command. Valid commands: {[c for c in commands]}")
        return
    
    # Invoke lambda
    response = client.invoke(
        FunctionName = arn,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )   

    # Parse & Return responses
    return json.loads(response["Payload"].read())["body"]["response"]