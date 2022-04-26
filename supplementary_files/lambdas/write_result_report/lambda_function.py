import os
import json

import boto3
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    
    print(event)
    
    sfn_exec_id = os.environ.get('OuterEvalEngineSfnExecutionId')
    
    print(f'sfn_exec_id:\n{sfn_exec_id}')
    
    return True