from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import boto3
import json
import os
import uuid
from decimal import Decimal


_LOG = get_logger(__name__)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return float(obj) if isinstance(obj, Decimal) else super().default(obj)

class ApiHandler(AbstractLambda):
    def __init__(self):
        env = os.getenv
        self.cognito = boto3.client("cognito-idp")
        self.db = boto3.resource("dynamodb")
        self.user_pool, self.client_id = env("cup_id"), env("cup_client_id")
        self.tables, self.reservations = self._get_table("tables"), self._get_table("reservations")

    def _get_table(self, name):
        return self.db.Table(os.getenv(name, f"default_{name}"))

    def _response(self, status, message, details=None):
        return {"statusCode": status, "body": json.dumps({"message": message, "details": details}, cls=JSONEncoder)}

    def signup(self, event):
        body = json.loads(event["body"])
        try:
            res = self.cognito.sign_up(
                ClientId=self.client_id,
                Username=body["email"],
                Password=body["password"],
                UserAttributes=[{"Name": k, "Value": body[v]} for k, v in {"email": "email", "given_name": "firstName", "family_name": "lastName"}.items()]
            )
            if not res.get("UserConfirmed"):
                self.cognito.admin_confirm_sign_up(UserPoolId=self.user_pool, Username=body["email"])
            return self._response(200, "User registered", res)
        except Exception as e:
            return self._response(400, "Signup failed", str(e))

    def authenticate(self, event):
        body = json.loads(event["body"])
        try:
            res = self.cognito.admin_initiate_auth(
                UserPoolId=self.user_pool, ClientId=self.client_id,
                AuthFlow="ADMIN_NO_SRP_AUTH", AuthParameters={"USERNAME": body["email"], "PASSWORD": body["password"]}
            )
            return self._response(200, "Authenticated", res.get("AuthenticationResult", {}).get("IdToken"))
        except Exception as e:
            return self._response(400, "Authentication failed", str(e))

    def get_tables(self, _):
        try:
            return self._response(200, "Tables retrieved", sorted(self.tables.scan()["Items"], key=lambda x: x["id"]))
        except Exception as e:
            return self._response(400, "Error retrieving tables", str(e))

    def handle_request(self, event, _):
        routes = {("POST", "/signup"): self.signup, ("POST", "/signin"): self.authenticate, ("GET", "/tables"): self.get_tables}
        return routes.get((event["httpMethod"], event.get("resource")), lambda _: self._response(400, "Invalid request"))(event)

    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
