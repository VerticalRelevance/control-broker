import json

import boto3
from botocore.exceptions import ClientError

def lambda_handler(event,context):
    print(event)
    
    return True