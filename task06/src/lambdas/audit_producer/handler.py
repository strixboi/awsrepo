import os
import uuid
from datetime import datetime, timezone

import boto3
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class AuditProducer(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        dynamo = boto3.resource("dynamodb")
        audit_table = dynamo.Table(os.getenv('table_name'))

        config_item = event.get("Records")[0]


        if config_item['eventName'] == "INSERT":
            audit_item = {
                "id": str(uuid.uuid4()),
                "itemKey": config_item["dynamodb"]["NewImage"]["key"]["S"],
                "modificationTime": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "newValue": { "key": config_item["dynamodb"]["NewImage"]["key"]["S"],
                              "value": int(config_item["dynamodb"]["NewImage"]["value"]["N"])}
            }
            audit_table.put_item(Item=audit_item)

        if config_item['eventName'] == "MODIFY":
            audit_item = {
                    "id": str(uuid.uuid4()),
                    "itemKey": config_item["dynamodb"]["NewImage"]["key"]["S"],
                    "modificationTime": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                    "updatedAttribute": "value",
                    "oldValue": int(config_item["dynamodb"]["OldImage"]["value"]["N"]),
                    "newValue": int(config_item["dynamodb"]["NewImage"]["value"]["N"]),
            }
            audit_table.put_item(Item=audit_item)



HANDLER = AuditProducer()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
