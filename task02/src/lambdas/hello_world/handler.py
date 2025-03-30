from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

import json
_LOG = get_logger(__name__)


class HelloWorld(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):

        request_info = event.get('requestContext', {}).get('http', {})
        method = request_info.get('method', 'UNKNOWN')
        path = request_info.get('path', '')

        if method == 'GET' and path == '/hello':
            response_body = {
                "statusCode": 200,
                "message": "Hello from Lambda"
            }
            return {
                "statusCode": 200,
                "body": json.dumps(response_body)
            }
        else:
            error_message = {
                "statusCode": 400,

            }
            return {
                "statusCode": 400,
                "body": json.dumps(error_message)
            }


HANDLER = HelloWorld()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
