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

def lambda_handler(event,context):
    
    print(event)
    
    full_invoke_url = os.environ.get('ApigwInvokeUrl')
    
    def get_host(*,FullInvokeUrl):
        m = re.search('https://(.*)/.*',FullInvokeUrl)
        return m.group(1)
    
    
    host = get_host(FullInvokeUrl=full_invoke_url)
    
    auth = BotoAWSRequestsAuth(
        aws_host= host,
        aws_region=region,
        aws_service='execute-api'
    )
    
    headers = {'Authorization':'foo'}
    
    control_broker_consumer_input = {"foo":"bar"} # FIXME
    
    r = requests.post(
        full_invoke_url,
        auth = auth,
        data = control_broker_consumer_input
    )
    
    print(f'headers:\n{dict(r.request.headers)}')
    
    content = json.loads(r.content)
    
    r = {
        'StatusCode':r.status_code,
        'Content': content
    }
    
    print(f'apigw formatted response:\n{r}')
    
    return content