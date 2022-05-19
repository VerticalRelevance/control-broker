import json
import re
import os
import uuid

import boto3
from botocore.exceptions import ClientError

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

s3 = boto3.client('s3')

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

    def get_requestor_is_authorized(self):
        # TODO
        self.requestor_is_authorized = True
        return True
    
    def get_validated_input_type(self):
        # TODO
        
        # go to that provided object
        
        # validate it matches type expected by this handler
        self.validated_input_type = "Terraform"
        return self.validated_input_type
    
    def fail_fast(self):

        fail_fast=None
        
        request = {
            "Request":{
                "Requestor": {
                    "IsAuthorized": self.get_requestor_is_authorized(),
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

def put_object(*,bucket,key,object_:dict):
    
    print(f'begin put_object\nbucket:\n{bucket}\nkey:\n{key}')
    
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(object_)
        )
    except ClientError as e:
        print(f'ClientError:\nbucket:\n{bucket}\nkey:\n{key}\n{e}')
        raise
    else:
        print(f'no ClientError put_object:\nbucket:\n{bucket}\nkey:\n{key}')
        return True
    
def generate_uuid():
    return str(uuid.uuid4())

def generate_s3_uuid_uri(*,bucket):
    
    uuid = generate_uuid()

    s3_uri = f's3://{bucket}/{uuid}'
    
    return s3_uri

def generate_presigned_url(bucket,key,client_method="get_object",ttl=3600):
    try:
        url = s3.generate_presigned_url(
            ClientMethod=client_method,
            Params={
                'Bucket':bucket,
                'Key':key
            },
            ExpiresIn=ttl
        )
    except ClientError:
        raise
    else:
        print(f"Presigned URL:\n{url}")
        return url

def format_response_expected_by_consumer(response_expected_by_consumer):
    
    from collections.abc import MutableMapping
    from contextlib import suppress
    
    def delete_keys_from_dict(dictionary, keys):
        for key in keys:
            with suppress(KeyError):
                del dictionary[key]
        for value in dictionary.values():
            if isinstance(value, MutableMapping):
                delete_keys_from_dict(value, keys)
    
    delete_keys_from_dict(response_expected_by_consumer,['Bucket','Key'])
    
    return response_expected_by_consumer
    
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
    
    evaluation_key = f'cb-{generate_uuid()}'
    
    response_expected_by_consumer = {
        "ControlBrokerEvaluation": {
            "Raw": {
                "PresignedUrl": generate_presigned_url(
                    bucket = os.environ['RawPaCResultsBucket'],
                    key = evaluation_key
                ),
                "Bucket": os.environ['RawPaCResultsBucket'],
                "Key": evaluation_key
            },
            "OutputHandlers":{
                "OPA": {
                    "PresignedUrl": generate_presigned_url(
                        bucket = json.loads(os.environ['OutputHandlers'])['OPA']['Bucket'],
                        key = evaluation_key
                    ),
                    "Bucket": json.loads(os.environ['OutputHandlers'])['OPA']['Bucket'],
                    "Key": evaluation_key
                }
            }
        }
    }
    
    # set input
    
    input_to_be_evaluated = {
        'Bucket':os.environ['TerraformInputsBucket'],
        'Key':evaluation_key
    }
    
    put_object(
        bucket = input_to_be_evaluated['Bucket'],
        key = input_to_be_evaluated['Key'],
        object_ = request_json_body['Input']
    )
    
    eval_engine_input =  {
        "InputToBeEvaluated": input_to_be_evaluated,
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
            # "Content": request_json_body,
            "Requestor": {
                "IsAuthorized": r.requestor_is_authorized
            },
            "InputType":{
                "Validated":bool(r.validated_input_type)
            },
            "Context":{
                "IsApproved":bool(r.approved_context)
            }
        },
        "Response": format_response_expected_by_consumer(response_expected_by_consumer)
    }
    
    print(f'control_broker_request_status:\n{control_broker_request_status}')
    
    return control_broker_request_status