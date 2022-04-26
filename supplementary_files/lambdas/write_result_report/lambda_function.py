import os
import json

import boto3
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    
    print(event)
    
