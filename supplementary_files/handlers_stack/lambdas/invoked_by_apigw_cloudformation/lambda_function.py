import json
import re
import os

import boto3
from botocore.exceptions import ClientError

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

session = boto3.session.Session()
region = session.region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')

def get_host(*,full_invoke_url):
    m = re.search('https://(.*)/.*',full_invoke_url)
    return m.group(1)

def get_evaluation_context(*,requested_evaluation_status,authorization_header):
    
    pass

    return "Prod"
    
def lambda_handler(event,context):
    
    print(f'event:\n{event}\ncontext:\n{context}')
    
    request_json_body = json.loads(event['body'])
    
    print(f'request_json_body:\n{request_json_body}')

    headers = event['headers']
    
    print(f'headers:\n{headers}')
    
    authorization_header = headers['Authorization']
    
    print(f'authorization_header:\n{authorization_header}')
    
    eval_engine_invoke_url = headers['x-eval-engine-invoke-url']
    
    print(f'eval_engine_invoke_url:\n{eval_engine_invoke_url}')
    
    host = get_host(full_invoke_url=eval_engine_invoke_url)
    
    auth = BotoAWSRequestsAuth(
        aws_host= host,
        aws_region=region,
        aws_service='execute-api'
    )
    
    print(f'BotoAWSRequestsAuth:\n{auth}')
    
    requested_evaluation_status = request_json_body['ConsumerMetadata']['RequestedEvaluationContext']
    
    print(f'requested_evaluation_status:\n{requested_evaluation_status}')
    
    evaluation_context = get_evaluation_context(
        requested_evaluation_status = requested_evaluation_status,
        authorization_header = authorization_header
    )
    
    eval_engine_input = {
        "ConsumerMetadata":request_json_body['ConsumerMetadata'],
        "InputAnalyzed":request_json_body['InputAnalyzed'],
        "EvalEngineConfiguration": {
            "EvaluationContext":evaluation_context
        }
    }
    
    print(f'eval_engine_input:\n{eval_engine_input}')
    
    r = requests.post(
        eval_engine_invoke_url,
        auth = auth,
        json = eval_engine_input
    )
    
    print(f'headers:\n{dict(r.request.headers)}')
    
    content = json.loads(r.content)
    
    r = {
        'StatusCode':r.status_code,
        'Content': content
    }
    
    print(f'apigw formatted response:\n{r}')
    
    return content