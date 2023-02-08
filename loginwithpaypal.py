import json
import os
import boto3
import requests

def lambda_handler(event, context):
    if event.get("params") and event["params"].get("querystring"):
        query_string_params = event["params"]["querystring"]
        
        if "code" in query_string_params:
            # Exchange authorization code for access token
            authorization_code = query_string_params["code"]
            payload = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": os.environ["REDIRECT_URI"],
                "client_id": os.environ["PAYPAL_CLIENT_ID"],
                "client_secret": os.environ["PAYPAL_CLIENT_SECRET"]
            }
            response = requests.post("https://api.paypal.com/v1/oauth2/token", data=payload)
            access_token = response.json()["access_token"]
            
            # Store access token in DynamoDB
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])
            table.put_item(
                Item={
                    "UserId": event["userId"],
                    "AccessToken": access_token
                }
            )
            
            return {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Fulfilled",
                    "message": {
                        "contentType": "PlainText",
                        "content": "You have successfully logged in with PayPal."
                    }
                }
            }
        else:
            # Redirect user to PayPal's authorization endpoint
            redirect_uri = os.environ["REDIRECT_URI"]
            client_id = os.environ["PAYPAL_CLIENT_ID"]
            authorization_url = f"https://www.paypal.com/webapps/auth/protocol/openidconnect/v1/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"
            
            return {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Fulfilled",
                    "message": {
                        "contentType": "PlainText",
                        "content": "Redirecting to PayPal for authentication..."
                    },
                    "responseCard": {
                        "version": 1,
                        "contentType": "application/vnd.amazonaws.card.redirect",
                        "genericAttachments": [
                            {
                                "title": "Login with PayPal",
                                "buttons": [
                                    {
                                        "text": "Login with PayPal",
                                        "value": authorization_url
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
    else:
        return {
            "dialogAction": {
                "type": "Close",
                "fulfill
