import json
import os
import uuid
from decimal import Decimal
import boto3
import requests

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class Processor(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        #https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m
        path = event.get('requestContext', {}).get('http', {}).get('path')


        _LOG.info(f"{path}")
        if path in ['/weather', '/']:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(os.getenv('table_name'))
            request = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
            request_info = request.json()
            _LOG.info("Getting to creation")

            # record = {'id': str(uuid.uuid4()),
            #         'forecast': {
            #     "elevation": request_info['elevation'],
            #     "generationtime_ms": request_info["generationtime_ms"],
            #     "hourly": {
            #         "temperature_2m": request_info['hourly']['temperature_2m'],
            #         "time": request_info['hourly']['time'],
            #     },
            #     "hourly_units": {
            #         "temperature_2m": str(request_info['hourly_units']['temperature_2m']),
            #         "time": str(request_info['hourly_units']['time']),
            #     },
            #     "latitude": request_info["latitude"],
            #     "longitude": request_info["longitude"],
            #     "timezone": request_info["timezone"],
            #     "timezone_abbreviation": request_info["timezone_abbreviation"],
            #     "utc_offset_seconds": request_info["utc_offset_seconds"]
            # }}

            record = {{"id": "1b472527-d5d1-4aea-84c7-328a508d3cb5", "forecast": {"latitude": 50.4375, "longitude": 30.5, "generationtime_ms": 0.025033950805664062, "utc_offset_seconds": 7200, "timezone": "Europe/Kiev", "timezone_abbreviation": "EET", "elevation": 188.0, "hourly_units": {"time": "iso8601", "temperature_2m": "°C"}, "hourly": {"time": ["2023-12-04T00:00", "2023-12-04T01:00", "2023-12-04T02:00", "..."], "temperature_2m": [-2.4, -2.8, -3.2, "..."]}}}}

            item = json.loads(json.dumps(record), parse_float=Decimal)
            table.put_item(Item = item)


            response ={
                    "headers": {
                        "Content-Type": "application/json"
                        },
                    "statusCode": 200,
                    "body": request_info
                    }
            return response
        return 200

HANDLER = Processor()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
