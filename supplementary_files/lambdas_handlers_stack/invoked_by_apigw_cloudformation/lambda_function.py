import json
import os
import re
import uuid

import boto3
from botocore.exceptions import ClientError

lambda_ = boto3.client('lambda')

def get_result_report_s3_uri(*,eval_results_reports_bucket):
    
    def generate_uuid():
        return str(uuid.uuid4())

    uuid = generate_uuid()

    s3_uri = f's3://{eval_results_reports_bucket}/cb-{uuid}'
    
    return s3_uri

def invoke_lambda_async(*,function_name,payload:dict):

    try:
        r = lambda_.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            # LogType='None'|'Tail',
            # ClientContext='string',
            Payload=bytes(payload, 'utf-8'),
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print(r)

def lambda_handler(event,context):
    
    print(f'event:\n{event}\ncontext:\n{context}')
    
    post_request_json_body = json.loads(event['body'])
    
    invoke_lambda_async(
        function_name = os.environ.get('EvalEngineLambdalithFunctionName'),
        payload = post_request_json_body
    )
    
    return True