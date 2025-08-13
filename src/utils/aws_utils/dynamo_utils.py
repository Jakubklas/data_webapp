import boto3
from typing import Any
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timedelta
from decimal import Decimal

class Config():

    def __init__(self, resource: boto3) -> None:
        self.dynamodb = resource
        self.table = self.dynamodb.Table("eoa-config")


    def index_config(self, input_data: dict) -> dict[list]:
        """
        Adds or changes EOA config.
        """
        results = {"success": [], "fail": []}
        items = []

                for k, v in input_data.items():
            if isinstance(v, float):
                v = Decimal(str(v))
            items.append({
                    "config": k,
                    "value": v
                })
        
                with self.table.batch_writer() as batch:
            for item in items:
                try:
                    batch.put_item(Item=item)
                    results["success"].append(item)
                except Exception as e:
                    results["fail"].append(item)
        
        print(f"Uploaded config:\n {results["success"]}")
        if results["fail"]:
            print(f"Failed to upload following config:\n {results["fail"]}")
        
        return results


    def get_config(self, config_name: str = None) -> dict:
        """
        Fetches the current specified config
        """
                if not config_name:
            response = self.table.scan()["Items"] 
            return response
        else:
            response = self.table.get_item(
                Key = {
                    "config": config_name
                }
            )
            value = response["Item"]["value"]
            if isinstance(value, Decimal):
                value = float(value)
        return value


class Exclusions():

    def __init__(self, resource: boto3, timezone: Any):
        self.dynamodb = resource
        self.table = self.dynamodb.Table("eoa-exclusions")
        self.timezone = timezone

    def exclude_providers(self, provider_ids: list, permanent: bool = False) -> str:
        """
        Updates weekly targeting quota for DPs or add new
        DPs to DynamoDB table incl. the last update time.  
        """
        results = {"success":0, "fail":0}
        current_date = datetime.now(self.timezone).strftime("%Y-%m-%d")

                for provider_id in provider_ids:
            try:
                response = self.table.update_item(
                    Key={
                        "provider_id": provider_id
                    },
                    UpdateExpression="SET num_targeted = if_not_exists(num_targeted, :zero) + :incr, last_saved = :date, permanent = :state",
                    ExpressionAttributeValues={
                        ":zero": Decimal(0),
                        ":incr": Decimal(1),
                        ":date": current_date,
                        ":state": permanent
                    },
                    ReturnValues="UPDATED_NEW"
                )
                results["success"] += 1

            except Exception as e:
                results["fail"] += 1
                print(e)

        return f"Increased DP targeting quota: {results}"


    def fully_exclude_providers(self, provider_ids: list, permanent: bool = False) -> str:
            """
            Updates weekly targeting quota for DPs or add new
            DPs to DynamoDB table incl. the last update time.  
            """
            results = {"success":0, "fail":0}
            current_date = datetime.now(self.timezone).strftime("%Y-%m-%d")

                        for provider_id in provider_ids:
                try:
                    response = self.table.update_item(
                        Key={
                            "provider_id": provider_id
                        },
                        UpdateExpression="SET num_targeted = if_not_exists(num_targeted, :inf) + :inf, last_saved = :date, permanent = :state",
                        ExpressionAttributeValues={
                            ":inf": 99,
                            ":date": current_date,
                            ":state": permanent
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    results["success"] += 1

                except Exception as e:
                    results["fail"] += 1
                    print(e)

            return f"Removed providers from this week's targeting: {results}"


    def get_exclusions(self, targets_quota: int = 2, persistance: int = 5, erase_old: bool = True) -> dict[list]:
        """
        Erases any old provider records and returns the
        current active list of excluded providers.
        """
        if erase_old:
            # Find the old providers (e.g. last excluded 5 days ago)
            threshold_date = (datetime.now(self.timezone) - timedelta(days=persistance)).strftime("%Y-%m-%d")
            response = self.table.scan(
                FilterExpression="last_saved < :thres and permanent = :state",
                ExpressionAttributeValues={
                    ":thres": threshold_date,
                    ":state": False
                }
            )

            # Delete the old records
            results = {"success":0, "fail":0}
            for item in response["Items"]:
                try:
                    self.table.delete_item(
                        Key={
                            "provider_id": item["provider_id"]
                        }
                    )
                    results["success"] +=1
                except Exception as e:
                    results["fail"] +=1
                    print(e)
            print(f"Removing all records submitted before {threshold_date}:")
            print(f"Found and removed {results["success"]} old provider_id exclusions")

        # Fetch the current up-to-date exclusions
        response = self.table.scan(
            FilterExpression=Attr('num_targeted').gte(targets_quota)
        )

        exclusions = {"items": [], "fail": []}
        for item in response["Items"]:
            try:
                exclusions["items"].append(item["provider_id"])
            except Exception as e:
                exclusions["fail"].append(item["provider_id"])
                print(f"Error processing {item.get('provider_id', 'unknown')}: {str(e)}")

        return exclusions


    def remove_all_exclusions(self, permanent: bool = False) -> dict[list]:
        """
        Remove all non-permanent exclusion records.
        """
        results = {"success":0, "fail":0}

                response = self.table.scan(
            FilterExpression="permanent = :state",
            ExpressionAttributeValues={
                ":state": permanent 
            },
            ProjectionExpression="provider_id"
        )

                items = list(set([item["provider_id"] for item in response.get("Items", [])]))
        print(items[:15])

                batch_size = 25
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            try:
                with self.table.batch_writer() as batch_writer:
                    for provider_id in batch:
                        batch_writer.delete_item(
                            Key={
                                "provider_id": provider_id
                            }
                        )    
                results["success"] += len(batch)

            except Exception as e:
                results["fail"] += len(batch)
                print(e)
        
        return results