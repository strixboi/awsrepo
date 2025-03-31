import datetime
import os
import uuid

import boto3
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        record = {
            "uuid":str(uuid.uuid4()),
            "principalId":event.get("principalId",1),
            "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
            "body":event.get("content",{})
        }

        dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("region", "eu-central-1"))
        table_name = os.environ.get("target_table")
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
