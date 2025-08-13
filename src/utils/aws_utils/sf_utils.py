import boto3
import json
import time
from datetime import datetime


def stepfunction_invoke(command: str, client: boto3, arn: str) -> dict[str]:
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
        
    response = client.start_execution(
        stateMachineArn = arn,
        name = f"{payload["run"]}_{datetime.now().strftime("%A_%d_+%m_%Y_%H_%M_%S")}",
        input = json.dumps(payload)
    )

    # Monitor progress
    while True:
        desc = client.describe_execution(executionArn=response["executionArn"])
        print("Current status:", desc["status"])
        if desc["status"] != "RUNNING":
            break
        time.sleep(5)

    # Stop on the final status
    if desc["status"] == "SUCCEEDED":
        output = json.loads(desc["output"])
        print("✅ Workflow succeeded, output:", output)    
    else:
        error = desc.get("cause", desc.get("error", "Unknown"))
        print(f"❌ Workflow failed ({desc["status"]}):", error)
    
    return desc
