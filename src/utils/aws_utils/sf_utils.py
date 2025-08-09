import boto3
import json
import time
from datetime import datetime


def stepfunction_invoke(command: str, arn: str) -> None:
    """
    Invokes an AWS step-functions state-machine to run compute
    intensitve ECS/Lambda workflows. Example 'command' input:
    """

    # Set up the client & invoke state-machine ARN
    commands = ["predict_churn", "match_offers"]
    if command in commands:
        payload = {
            "run": command
        }
    else:
        print(f"Incorrect command. Valid commands: {[c for c in commands]}")
        return
        
    sf = boto3.client("stepfunctions")
    response = sf.start_execution(
        stateMachineArn = arn,
        name = f"{payload["run"]}_{datetime.now().strftime("%A_%d_+%m_%Y_%H_%M_%S")}",
        input = json.dumps(payload)
    )

    # Monitor progress
    while True:
        desc = sf.describe_execution(executionArn=response["executionArn"])
        status = desc["status"]
        print("Current status:", status)
        if status != "RUNNING":
            break
        time.sleep(5)

    # Stop on the final status
    if status == "SUCCEEDED":
        output = json.loads(desc["output"])
        print("✅ Workflow succeeded, output:", output)    
    else:
        error = desc.get("cause", desc.get("error", "Unknown"))
        print(f"❌ Workflow failed ({status}):", error)
    
    return status
