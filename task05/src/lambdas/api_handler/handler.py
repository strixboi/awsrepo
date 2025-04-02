import os
import uuid
from datetime import datetime, timezone

import boto3
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):

        record = {
            "id": str(uuid.uuid4()),
            "principalId": event.get("principalId",1),
            "createdAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "body": event.get("content", {})
        }

        dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("region", "eu-central-1"))
        table_name = os.environ.get("target_table")
        if not table_name:
            _LOG.error("Environment variable 'target_table' is not set.")
            return {
                "statusCode": 500,
                "body": {"error": "'target_table' environment variable is missing"}
            }

        table = dynamodb.Table(table_name)

        try:
            table.put_item(Item=record)
        except Exception as e:
            _LOG.error("Error saving to DynamoDB: %s", str(e))
            return {
                "statusCode": 500,
                "body": {"error": "Failed to save event to database"}
            }

        return {
            "statusCode": 201,
            "body": {
                "event": record,
                "statusCode": 201
            }
        }

    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
