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
    
def lambda_handler(event,context):
    
    print(f'event:\n{event}\ncontext:\n{context}')
    
    headers = event['headers']
    
    print(f'headers:\n{headers}')
    
    eval_engine_invoke_url = headers['x-control-broker-invoke-url']
    
    print(f'eval_engine_invoke_url:\n{eval_engine_invoke_url}')
    
    host = get_host(full_invoke_url=eval_engine_invoke_url)
    
    auth = BotoAWSRequestsAuth(
        aws_host= host,
        aws_region=region,
        aws_service='execute-api'
    )
    
    print(f'BotoAWSRequestsAuth:\n{auth}')
    
    control_broker_consumer_input = event
    
    r = requests.post(
        full_invoke_url,
        auth = auth,
        json = control_broker_consumer_input
    )
    
    print(f'headers:\n{dict(r.request.headers)}')
    
    content = json.loads(r.content)
    
    r = {
        'StatusCode':r.status_code,
        'Content': content
    }
    
    print(f'apigw formatted response:\n{r}')
    
    return content