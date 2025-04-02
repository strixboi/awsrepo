import json

import requests
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Handling weather request
        """

        request_context = event.get('requestContext',{})
        info = request_context.get('http',{})
        method = info.get('method')
        path = info.get('path')
        response = {}

        if info.get('path') == '/weather' and info.get('method') == "GET":
            weather_request = requests.get("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")

            response = {
                "statusCode": 200,
                "body": weather_request.json(),
                "headers": {
                    "content-type": "application/json"}
            }
        else:
            response = {
            "statusCode": 400,
            "body": {
              "statusCode": 400,
              "message": f"Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}"},
            "headers": {
              "content-type": "application/json"},
            "isBase64Encoded": False
          }
        return response




HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
