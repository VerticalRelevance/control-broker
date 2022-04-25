import json

import boto3
from botocore.exceptions import ClientError

def lambda_handler(event,context):
    print(event)
    
    headers = event.get('headers')
    
    auth_header = headers.get('authortization')
    
    return {
      "isAuthorized": True,
      "context": {
        "AuthHeader": auth_header
      }
    }