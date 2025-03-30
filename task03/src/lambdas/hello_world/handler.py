import json

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class HelloWorld(AbstractLambda):

    def validate_request(self, event) -> dict:
        """
        Validates the request by checking if the path is '/hello'
        If the path has a match, return response, otherwise return None
        """
        response = self._generate_response(event)
        return response if response else None

    def _generate_response(self,event) -> dict:
        """
        Private helper function that creates a response based on the event path.
        """
        if event.get('path') == '/hello':
            return {
            'statusCode': 200,
            'body':json.dumps({
            'statusCode': 200,
            'message': 'Hello from Lambda'
        })
        }
        return None


    def handle_request(self, event, context):
        """
        Handle event
        """
        return {
            'statusCode': 200,
            'message': 'Hello from Lambda'
        }
    

HANDLER = HelloWorld()


def lambda_handler(event, context):
    response = HANDLER.validate_request(event)
    if response is not None:
        return response


    return HANDLER.lambda_handler(event=event, context=context)
