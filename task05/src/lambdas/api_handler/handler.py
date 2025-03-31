import datetime
import os
import uuid

import boto3
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        # Add validation logic to ensure the event contains required fields
        required_keys = ["principalId", "content"]
        missing_keys = [key for key in required_keys if key not in event]
        if missing_keys:
            _LOG.error(f"Missing required keys: {missing_keys}")
            return {"is_valid": False, "error": f"Missing required keys: {missing_keys}"}
        return {"is_valid": True}

    def handle_request(self, event, context):
        # Validate the event before processing
        validation_result = self.validate_request(event)
        if not validation_result["is_valid"]:
            return {
                "statusCode": 400,
                "body": {"error": validation_result["error"]}
            }

        record = {
            "uuid": str(uuid.uuid4()),
            "principalId": event.get("principalId"),
            "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
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
                "event": record
            }
        }


HANDLER = ApiHandler()


def lambda_handler(event, context):
    try:
        response = HANDLER.lambda_handler(event=event, context=context)
        _LOG.info(f"Response: {response}")
        return response
    except Exception as ex:
        _LOG.error(f"Unexpected error: {str(ex)}")
        return {
            "statusCode": 500,
            "body": {"error": "An unexpected error occurred"}
        }