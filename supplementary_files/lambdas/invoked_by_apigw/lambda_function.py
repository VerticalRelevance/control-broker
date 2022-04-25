import json

import boto3
from botocore.exceptions import ClientError

def lambda_handler(event,context):
    print(event)
    
    headers = event.get('headers')
    
    auth_header = headers.get('authorization')
    
    print(f'auth_header:\n{auth_header}')
    
    return True