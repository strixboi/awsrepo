import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class UuidGenerator(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Generate and pass UUIDs
        """
        try:
            unique_ids = [str(uuid.uuid4()) for i in range(10)]
            j_dump = json.dumps({
                'ids': unique_ids})

            name = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            boto3.client('s3').put_object(
                Bucket=os.getenv('target_bucket', 'uuid-storage'),
                Key= f"{name}",
                Body=j_dump,
                ContentType='application/json'
            )
            _LOG.info(f"Success {name}")
        except Exception as e:
            _LOG.error(f'Error:{e}')
            raise e

    

HANDLER = UuidGenerator()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
