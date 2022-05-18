import json

import boto3
from botocore.exceptions import ClientError

def determine_is_authorized(auth_header):
    # TODO
    return True

def lambda_handler(event,context):
    print(event)
    
    headers = event.get('headers')
    print(f'headers:\n{headers}')
    
    auth_header = headers.get('authorization') # undercase here, even if request is uppercase
    
    is_authorized = determine_is_authorized(auth_header)
    
    auth_decision = {
      "isAuthorized": is_authorized,
      "context": {
        "AuthHeader": auth_header
      }
    }
    
    print(f'auth_decision:\n{auth_decision}')
    
    return auth_decision