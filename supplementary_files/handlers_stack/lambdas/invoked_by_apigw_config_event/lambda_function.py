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

s3 = boto3.client('s3')
cfn = boto3.client('cloudformation')
cloudcontrol = boto3.client('cloudcontrol')

def get_object(*,bucket,key):
    
    try:
        r = s3.get_object(
            Bucket = bucket,
            Key = key
        )
    except ClientError as e:
        print(f'ClientError:\nbucket:\n{bucket}\nkey:\n{key}\n{e}')
        raise
    else:
        print(f'no ClientError get_object:\nbucket:\n{bucket}\nkey:\n{key}')
        body = r['Body']
        content = json.loads(body.read().decode('utf-8'))
        return content

def put_object(*,bucket,key,object_:dict):
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

class CloudControl():
    
    def __init__(self,type_name,identifier):
        self.type_name = type_name
        self.identifier = identifier
    
    def get_resource_schema(self,*,resource_type):
        try:
            r = cfn.describe_type(
                Type = 'RESOURCE',
                TypeName = resource_type,
            )
        except cfn.exceptions.TypeNotFoundException:
            print(f'TypeNotFoundException: {resource_type}')
            return None
        except ClientError as e:
            raise
        else:
            schema = json.loads(r['Schema'])
            print(schema)
            return schema
    
    def cloudcontrol_get(self,*,type_name,identifier):   
        try:
            r = cloudcontrol.get_resource(
                TypeName = type_name,
                Identifier = identifier
            )
        except ClientError as e:
            print(f'ClientError\n{e}')
            raise
        else:
            properties = json.loads(r['ResourceDescription']['Properties'])
            print(f'cloudcontrol.get_resource properties\ntype_name:\n{type_name}\nidentifier:\n{identifier}\nProperties:\n{properties}')
            return properties

    def get_cfn(self):
        
        cloudcontrol_properties = self.cloudcontrol_get(type_name=self.type_name,identifier=self.identifier)
        
        resource_schema = self.get_resource_schema(resource_type=self.type_name)
        print(f'resource_schema:\n{resource_schema}')
        
        schema_properties = resource_schema['properties']
        
        read_only_properties = [i.split('/properties/')[1] for i in resource_schema['readOnlyProperties']]
        for read_only_property in read_only_properties:
            cloudcontrol_properties.pop(read_only_property,None)
        
        cfn = {
            "Resources" : {
              "ConfigEventResource" : {
                "Type" : self.type_name,
                "Properties" : cloudcontrol_properties,
              }
            }
        }
        print(f'cfn:\n{cfn}')
        return cfn

class ConfigEventToCloudFormationConverter():
    
    def __init__(
        self,
        config_event_input_analyzed:dict
    ):
        
        self.config_event_s3_path = {
            "Bucket":config_event_input_analyzed['Bucket'],
            "Key":config_event_input_analyzed['Key']
        }
        
        self.config_event = get_object(
            bucket = self.config_event_s3_path['Bucket'],
            key = self.config_event_s3_path['Key']
        )
        
    def parse_config_event(self):
        
        print(f'config_event:\n{self.config_event}')
    
        invoking_event = json.loads(self.config_event["invokingEvent"])
        print(f'invoking_event:\n{invoking_event}')
        
        rule_parameters = self.config_event.get("ruleParameters")
        if rule_parameters:
            rule_parameters = json.loads(rule_parameters)
            print(f'rule_parameters:\n{rule_parameters}')
        
        configuration_item = invoking_event["configurationItem"]
        print(f'configuration_item:\n{configuration_item}')
        
        item_status = configuration_item["configurationItemStatus"]
        print(f'item_status:\n{item_status}')
        
        self.resource_type = configuration_item['resourceType']
        print(f'resource_type:\n{self.resource_type}')
        
        resource_configuration = configuration_item['configuration']
        print(f'resource_configuration:\n{resource_configuration}')
        
        if resource_configuration:
            resource_configuration_keys = list(resource_configuration.keys())
            print(f'resource_configuration_keys:\n{resource_configuration_keys}')
        
        self.resource_id = configuration_item['resourceId']
        print(f'resource_id:\n{self.resource_id}')
    
    def get_converted_cloudformation(self):
        
        c = CloudControl(type_name=self.resource_type,identifier=self.resource_id)
    
        self.cfn = c.get_cfn()
        
        return self.cfn
        
    def put_converted_cloudformation(self):
        
        self.converted_s3_path = {
            'Bucket' : os.environ['ConfigEventsConvertedInputBucket'],
            'Key' : self.config_event_s3_path['Key'],
        }
        
        put_object(
            bucket = self.converted_s3_path['Bucket'],
            key = self.converted_s3_path['Key'],
            object_ = self.cfn
        )
    
    def get_converted_s3_path(self):
        
        self.parse_config_event()
        self.get_converted_cloudformation()
        self.put_converted_cloudformation()
        
        return self.converted_s3_path
    
def convert_config_event_to_cfn(*,config_event_input_analyzed):
        
    c = ConfigEventToCloudFormationConverter(config_event_input_analyzed)
    
    modified_input_analyzed = c.get_converted_s3_path()
    
    return modified_input_analyzed
    
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
    
    original_input_analyzed = request_json_body['Input']
    
    print(f'original_input_analyzed:\n{original_input_analyzed}')
    
    converted_input_analyzed = convert_config_event_to_cfn(
        config_event_input_analyzed = original_input_analyzed
    )
    
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
            "Content": request_json_body,
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