import json, os, re

import boto3
from botocore.exceptions import ClientError

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

sqs= boto3.client("sqs")
session = boto3.session.Session()
region = session.region_name

def sign_request(*,
    full_invoke_url:str,
    region:str,
    input_:dict,
):
    
    def get_host(full_invoke_url):
        m = re.search('https://(.*)/.*',full_invoke_url)
        return m.group(1)
    
    host = get_host(full_invoke_url)
    
    auth = BotoAWSRequestsAuth(
        aws_host= host,
        aws_region=region,
        aws_service='execute-api'
    )
    
    print(f'begin request\nfull_invoke_url\n{full_invoke_url}\njson input\n{input_}')
    
    r = requests.post(
        full_invoke_url,
        auth = auth,
        json = input_
    )
    
    print(f'signed request headers:\n{dict(r.request.headers)}')
    
    content = json.loads(r.content)
    
    r = {
        'StatusCode':r.status_code,
        'Content': content
    }
    
    print(f'formatted response:\n{r}')
    
    return True

def process_message_subject_to_pac(message):
    print('begin process_message')
    
    cb_input_object = {
        "Context":None,
        "Input": message
    }
    
    print(f'cb_input_object:\n{cb_input_object}')
    
    # sign request
    
    sign_request(
        full_invoke_url = os.environ['ControlBrokerApigwEndpointUrl'],
        region = region,
        input_ = cb_input_object
    )

def delete_message(*,queue_url,receipt_handle):
    
    try:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        return True

def lambda_handler(event, context):

    print(event)
    
    spoke_accounts=json.loads(os.environ['SpokeAccounts'])
    
    resource_types_subject_to_pac=json.loads(os.environ['ResourceTypesSubjectToPac'])
    
    for record in event['Records']:
        
        body=json.loads(record['body'])
        
        message=json.loads(body['Message'])
        
        try:
            configuration_item=message['configurationItem']
        except KeyError:
            delete_message(
                queue_url=os.environ['QueueUrl'],
                receipt_handle=record['receiptHandle']
            )
        else:
            message_account_id=configuration_item['awsAccountId']
            
            message_resource_type=configuration_item['resourceType']
        
            
            if message_account_id in spoke_accounts and message_resource_type in resource_types_subject_to_pac:
                
                print(f'message_account_id ({message_account_id}) is in spoke_accounts:\n{spoke_accounts}')
                
                process_message_subject_to_pac(message)
            
            delete_message(
                queue_url=os.environ['QueueUrl'],
                receipt_handle=record['receiptHandle']
            )