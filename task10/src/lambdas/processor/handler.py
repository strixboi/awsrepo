import json
import os
import uuid

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
        request_context = event.get('requestContext',{})
        info = request_context.get('http',{})
        #method = info.get('method')
        path = event.get('requestContext', {}).get('http', {}).get('path')



        dynamo = boto3.resource('dynamodb')

        table_name = os.getenv('table_name')
        if not table_name:
            raise ValueError("Brak nazwy tabeli w zmiennej środowiskowej 'table_name'")

        _LOG.info(f"{path}")
        if path in ['/weather', '/']:
            dynamo_table = dynamo.Table(os.getenv('table_name'))
            request = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
            request_info = request.json()
            _LOG.info("Getting to creation")

            # item = {
            #     "id": str(uuid.uuid4()),
            #     "forecast":{
            #              "elevation": request_info['elevation'],
            #              "generationtime_ms": request_info["generationtime_ms"],
            #              "hourly": {
            #                  "temperature_2m": request_info['hourly']['temperature_2m'],
            #                  #"time": str(request_info['hourly']['time'])
            #                  "time": request_info['hourly']['time'],
            #               },
            #               "hourly_units": {
            #                  "temperature_2m": str(request_info['hourly_units']['temperature_2m']),
            #                  "time": str(request_info['hourly_units']['time']),
            #               },
            #               "latitude": request_info["latitude"],
            #               "longitude": request_info["longitude"],
            #               "timezone": request_info["timezone"],
            #               "timezone_abbreviation": request_info["timezone_abbreviation"],
            #               "utc_offset_seconds": request_info["utc_offset_seconds"]
            #     }
            # }
            item = {}
            item['id'] = str(uuid.uuid4())
            item['forecast'] = {
                         "elevation": request_info['elevation'],
                         "generationtime_ms": request_info["generationtime_ms"],
                         "hourly": {
                             "temperature_2m": request_info['hourly']['temperature_2m'],
                             "time": request_info['hourly']['time'],
                          },
                          "hourly_units": {
                             "temperature_2m": str(request_info['hourly_units']['temperature_2m']),
                             "time": str(request_info['hourly_units']['time']),
                          },
                          "latitude": request_info["latitude"],
                          "longitude": request_info["longitude"],
                          "timezone": request_info["timezone"],
                          "timezone_abbreviation": request_info["timezone_abbreviation"],
                          "utc_offset_seconds": request_info["utc_offset_seconds"]
                }

            record = json.loads(json.dumps(item))
            dynamo_table.put_item(Item = record)

            # "elevation": number,
            # "generationtime_ms": number,
            # "hourly": {
            #     "temperature_2m": [number],
            #     "time": [str]
            # },
            # "hourly_units": {
            #     "temperature_2m": str,
            #     "time": str
            # },
            # "latitude": number,
            # "longitude": number,
            # "timezone": str,
            # "timezone_abbreviation": str,
            # "utc_offset_seconds": number


            # return response to invoked pass
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
