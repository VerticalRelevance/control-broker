import json
import re
import os
import uuid

import boto3
from botocore.exceptions import ClientError

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

session = boto3.session.Session()
region = session.region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')

class RequestParser():
    
    def __init__(self,*,
    event
    ):
        self.event = event
        
        self.request_json_body = json.loads(event['body'])
        self.headers = event['headers']
        self.consumer_request_context = self.request_json_body['Context']
        
        self.main()

    def requestor_is_authorized(self):
        # TODO
        self._requestor_is_authorized = True
        return True
    
    def input_grants_required_read_access(self):
        # TODO
        self._input_grants_required_read_access = True
        return True
        
    def get_validated_input_type(self):
        # TODO
        
        # go to that provided object
        
        # validate it matches type expected by this handler i.e. CloudFormation
        self.validated_input_type = "CloudFormation"
        return "CloudFormation"
    
    def fail_fast(self):

        fail_fast=None
        
        request = {
            "Request":{
                "Requestor": {
                    "IsAuthorized": self.requestor_is_authorized(),
                },
                "Input": {
                    "GrantsRequiredReadAccess": self.input_grants_required_read_access()
                },
                "InputType":{
                    "Validated":bool(self.get_validated_input_type())
                },
                "Context":{
                    "IsApproved":bool(self.approved_context)
                }
            }
        }
        
        def any_false_leaf(d):
            if isinstance(d, dict):
                return any(any_false_leaf(v) for v in d.values())
            return not d
            
        if any_false_leaf(request):
            fail_fast = request
            
        print(f'fail_fast:{fail_fast}')
        return fail_fast
    
    def get_consumer_metadata(self):

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
    
        self.consumer_metadata = {
            "SSOAttributes": integrate_with_my_identity_provider(self.event)
        }
        
        return self.consumer_metadata
    
    def get_approved_context(self):
    
        def integrate_with_my_entitlement_system(consumer_metadata,consumer_request_context):
            
            # make external call per enterprise implementation
            
            # if consumer is authorized to call the CB with the context it provided, then return the unmodified context
            
            # if not, return failure
            
            # demo check below
            
            return consumer_metadata['SSOAttributes']['Org'] == "OrgA"
        
        if integrate_with_my_entitlement_system(self.consumer_metadata,self.consumer_request_context):
            
            self.approved_context = self.consumer_request_context
            
            return self.approved_context
        
        else:
        
            return False
    
        
    def main(self):
        
        self.get_consumer_metadata()
        
        self.get_approved_context()
        
            
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
    
    return True
    
def generate_uuid():
    return str(uuid.uuid4())

def generate_s3_uuid_uri(*,bucket):
    
    uuid = generate_uuid()

    s3_uri = f's3://{bucket}/{uuid}'
    
    return s3_uri
    
def lambda_handler(event,context):
    
    print(f'event:\n{event}\ncontext:\n{context}')
    
    # instantiate
    
    r = RequestParser(event=event)
    
    # parse event
    
    request_json_body = json.loads(event['body'])
    
    print(f'request_json_body:\n{request_json_body}')

    headers = event['headers']
    
    print(f'headers:\n{headers}')
    
    authorization_header = headers['authorization']
    
    print(f'authorization_header:\n{authorization_header}')
    
    # fail fast
    
    fail_fast = r.fail_fast()
    
    if fail_fast:
        return fail_fast
    
    # set response
    
    response_expected_by_consumer = {
        "ResultsReport": {
            "Key": f'cb-{generate_uuid()}',
            "Buckets": {
                "Raw": os.environ['RawPaCResultsBucket'],
                "OutputHandlers":json.loads(os.environ['OutputHandlers'])
            }
        }
    }
    
    # set input
    
    eval_engine_input =  {
        "InputAnalyzed":request_json_body['Input'],
        "ConsumerMetadata": r.consumer_metadata, 
        "Context": r.approved_context,
        "InputType": r.validated_input_type,
        "ResponseExpectedByConsumer": response_expected_by_consumer
    }
    
    print(f'eval_engine_input:\n{eval_engine_input}')
    
    # sign request
    
    sign_request(
        full_invoke_url = headers['x-eval-engine-invoke-url'],
        region = region,
        input = eval_engine_input
    )
    
    # set response
    
    control_broker_request_status = {
        "Request":{
            "Requestor": {
                "IsAuthorized": r._requestor_is_authorized
            },
            "Input": {
                "GrantsRequiredReadAccess": r._input_grants_required_read_access
            },
            "InputType":{
                "Validated":bool(r.validated_input_type)
            },
            "Context":{
                "IsApproved":bool(r.approved_context)
            }
        },
        "Response": response_expected_by_consumer
    }
    
    print(f'control_broker_request_status:\n{control_broker_request_status}')
    
    return control_broker_request_status