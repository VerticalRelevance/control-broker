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

def get_approved_context(*,consumer_request_context,authorization_header):
    
    # some Authz call
    
    return consumer_request_context # auto-approve for now, pending full implementation
    
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
    
    consumer_request_context = request_json_body['Context']
    
    print(f'consumer_request_context:\n{consumer_request_context}')
    
    approved_context = get_approved_context(
        consumer_request_context = consumer_request_context,
        authorization_header = authorization_header
    )
    
    eval_engine_input = {
        "ConsumerRequestContext":consumer_request_context,
        "InputAnalyzed":request_json_body['Input'],
        "EvalEngineConfiguration": {
            "ApprovedContext":approved_context
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