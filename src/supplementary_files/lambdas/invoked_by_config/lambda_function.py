import json
import boto3
import os
import re

from botocore.exceptions import ClientError
from datetime import datetime

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

session = boto3.session.Session()
region = session.region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')

sfn = boto3.client("stepfunctions")
s3 = boto3.client("s3")

def put_object(bucket,key,object_:dict):
    print(f'put_object\nbucket:\n{bucket}\nKey:\n{key}')
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(object_)
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        return True

class SimpleControlBrokerClient():
    def __init__(self,*,
        invoke_url,
        input_bucket,
        input_object:dict,
    ):
        
        self.invoke_url = invoke_url
        self.input_bucket = input_bucket
        self.input_object = input_object
        
        
    def put_input(self):
        
        put = put_object(
            bucket=self.input_bucket,
            key='SimpleControlBrokerClient-input.json',
            object_ = self.input_object
        )
        
    def invoke_endpoint(self):
        
        def get_host(*,full_invoke_url):
            m = re.search('https://(.*)/.*',full_invoke_url)
            return m.group(1)
        
        host = get_host(full_invoke_url=self.invoke_url)
            
        auth = BotoAWSRequestsAuth(
            aws_host= host,
            aws_region=region,
            aws_service='execute-api'
        )
        
        r = requests.post(
            self.invoke_url,
            auth = auth,
            json = self.input_object
        )
        
        print(f'headers:\n{dict(r.request.headers)}\n')
        
        content = json.loads(r.content)
        
        r = {
            'StatusCode':r.status_code,
            'Content': content
        }
        
        print(f'\napigw formatted response:\n')
        print(r)
    
        return r
def lambda_handler(event, context):

    print(event)

    invoking_event = json.loads(event["invokingEvent"])
    print(f"invoking_event:\n{invoking_event}")

    rule_parameters = event.get("ruleParameters")
    if rule_parameters:
        rule_parameters = json.loads(rule_parameters)
        print(f"rule_parameters:\n{rule_parameters}")

    configuration_item = invoking_event["configurationItem"]
    print(f"configuration_item:\n{configuration_item}")

    item_status = configuration_item["configurationItemStatus"]
    print(f"item_status:\n{item_status}")
    
    if item_status == 'ResourceDeleted':
        return True

    resource_type = configuration_item["resourceType"]
    print(f"resource_type:\n{resource_type}")

    resource_configuration = configuration_item["configuration"]
    print(f"resource_configuration:\n{resource_configuration}")

    resource_id = configuration_item["resourceId"]
    print(f"resource_id:\n{resource_id}")

    result_token = event["resultToken"]
    print(f"result_token:\n{result_token}")
    
    config_rule_name = event["configRuleName"]
    print(f"config_rule_name:\n{config_rule_name}")

    # process
    
    invoked_by_key = f'{config_rule_name}-{resource_type}-{resource_id}-{invoking_event["notificationCreationTime"]}'

    invoke_url = os.environ['ControlBrokerInvokeUrl']
    
    input_analyzed = {
        "Bucket":os.environ['ConfigEventsRawInputBucket'],
        "Key":invoked_by_key
    }
    
    put_object(
        bucket = input_analyzed['Bucket'],
        key = input_analyzed['Key'],
        object_ = event
    )
    
    cb_input_object = {
        "Context":{
            "EnvironmentEvaluation":"Prod"
        },
        "Input": input_analyzed
    }
    
    s = SimpleControlBrokerClient(
        invoke_url = invoke_url,
        input_bucket = input_analyzed['Bucket'],
        input_object = cb_input_object
    )
    
    s.put_input()
    response = s.invoke_endpoint()