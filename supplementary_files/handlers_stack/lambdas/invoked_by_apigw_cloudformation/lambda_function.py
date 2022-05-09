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


def get_approved_context(*,consumer_metadata,consumer_request_context):
    
    def integrate_with_my_entitlement_system(consumer_metadata,consumer_request_context):
        
        # make external call per enterprise implementation
        
        # if consumer is authorized to call the CB with the context it provided, then return the unmodified context
        
        # if not, return failure
        
        # demo check below
        
        return consumer_metadata['SSOAttributes']['Org'] == "OrgA"
    
    if integrate_with_my_entitlement_system(consumer_metadata,consumer_request_context):
        return consumer_request_context
    else:
        return False
 
def validate_input_type(request_json_body):
    
    # go to that provided object
    
    # validate it matches type expected by this handler i.e. CloudFormation
    
    return "CloudFormation"

def get_consumer_metadata(event):

    def integrate_with_my_identity_provider(event):
    
        headers = event['headers']
    
        authorization_header = headers['authorization']

        # make external call per enterprise implementation
        # demo values below
        
        return {
            "Org":"OrgA",
            "BusinessUnit":"BU1",
            "BillingCode":"bu-01",
            "Name":"Jane Ray"
        }

    return {
        "SSOAttributes": integrate_with_my_identity_provider(event)
    }

def control_broker_has_read_acces_to_input(event):
    #TODO
    return True

class RequestParser():
    
    def __init__(self,*,
    event
    ):
        self.event = event
        
        self.request_json_body = json.loads(event['body'])
        self.headers = event['headers']

def sign_request(*,
    full_invoke_url:str,
    region:str,
    input:dict,
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
    
    print(f'begin request\nfull_invoke_url\n{full_invoke_url}\njson input\n{input}')
    
    r = requests.post(
        full_invoke_url,
        auth = auth,
        json = input
    )
    
    print(f'signed request headers:\n{dict(r.request.headers)}')
    
    content = json.loads(r.content)
    
    r = {
        'StatusCode':r.status_code,
        'Content': content
    }
    
    print(f'formatted response:\n{r}')
    
def lambda_handler(event,context):
    
    print(f'event:\n{event}\ncontext:\n{context}')
    
    r = RequestParser(event=event)
    
    request_json_body = json.loads(event['body'])
    
    print(f'request_json_body:\n{request_json_body}')

    headers = event['headers']
    
    print(f'headers:\n{headers}')
    
    authorization_header = headers['authorization']
    
    print(f'authorization_header:\n{authorization_header}')
    
    consumer_request_context = request_json_body['Context']
    
    consumer_metadata = get_consumer_metadata(event)
    
    print(f'consumer_request_context:\n{consumer_request_context}')
    
    approved_context = get_approved_context(
        consumer_metadata = consumer_metadata,
        consumer_request_context = consumer_request_context
    )
    
    if not approved_context:
        fail_fast = {
            "RequestorAuthorizedForProvidedContext": False
        }
        print(f'fail_fast:{fail_fast}')
        return fail_fast
    
    if not control_broker_has_read_acces_to_input(event):
        fail_fast = {
            "ControlBrokerHasReadAccessToInputS3Path": False
        }
        print(f'fail_fast:{fail_fast}')
        return fail_fast

    eval_engine_input =  {
        "Input":request_json_body['Input'],
        "Context": approved_context,
        "InputType": validate_input_type(request_json_body),
        "ConsumerMetadata": consumer_metadata, 
            # NB renamed from an object manually provided by the user to things we know about requestor based on the authentication system
    }
    
    print(f'eval_engine_input:\n{eval_engine_input}')
    
    sign_request(
        full_invoke_url = headers['x-eval-engine-invoke-url'],
        region = region,
        input = eval_engine_input
    )
    
    control_broker_request_status = {
        "Request":{
            "Requestor": {
                "IsAuthorized": "",
            },
            "Input": {
                "GrantsRequiredReadAccess": control_broker_has_read_acces_to_input(event),
            },
            "InputType":{
                "Validated":""
            },
            "Context":{
                "IsApproved":""
            }
        },
        "Response": {
            "ResultReport":{
                "Raw":{
                    "S3Uri":""
                },
                "OutputHandlers":[
                    {
                        "DefaultParsed": {
                            "S3Uri":""
                        }
                    }
                ]
            }
        }   
    }
    
    return control_broker_request_status