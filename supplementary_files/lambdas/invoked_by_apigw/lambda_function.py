import json
import os
import re

import boto3
from botocore.exceptions import ClientError

sfn = boto3.client('stepfunctions')


def extract_acces_key_id(*,Aws4Authorization):
    m = re.search('AWS4-HMAC-SHA256 Credential=(\w*)/.*',Aws4Authorization)
    return m.group(1)

def get_result_report_s3_uri(*,AuthorizationHeader):
    
    access_key_id = extract_acces_key_id(AuthorizationHeader=AuthorizationHeader)
    
    return 's3://cschneider-terraform-backend/foo.json'
    # FIXME - form path based on auth, make sure EvalEngine writes to that same path

def get_requestor_authorization_status(*,AuthorizationHeader):
    return True
    # TODO

def get_eval_engine_read_access_to_inputs_status():
    return True
    #TODO

def async_sfn(*, SfnArn, Input: dict):
    try:
        r = sfn.start_execution(stateMachineArn=SfnArn, input=json.dumps(Input))
    except ClientError as e:
        print(f"ClientError\n{e}")
        raise
    else:
        print(f'no ClientError start_execution:\nSfnArn:\n{SfnArn}\nInput:\n{Input}')
        return r["executionArn"]


def lambda_handler(event,context):
    
    print(event)
    
    post_request_json_body = json.loads(event['body'])
    
    eval_engine_sfn_arn = os.environ.get('ControlBrokerOuterSfnArn')
    print(f'eval_engine_sfn_arn:\n{eval_engine_sfn_arn}')
    
    headers = event.get('headers')
    
    authorization_header = headers.get('authorization')
    
    print(f'authorization_header:\n{authorization_header}')
    
    eval_engine_sfn_input = {
        "InvokedByApigw": post_request_json_body,
        "ResponseReportS3Path": get_result_report_s3_uri(AuthorizationHeader=authorization_header)
    }
    
    eval_engine_sfn_execution_arn = async_sfn(
        SfnArn = eval_engine_sfn_arn,
        Input = eval_engine_sfn_input
    )
    
    control_broker_request_status = {
        "RequestorIsAuthorized": get_requestor_authorization_status(AuthorizationHeader=authorization_header),
        "EvalEngineHasReadAccessToInputs": get_eval_engine_read_access_to_inputs_status(),
        "ResponseReportS3Path": get_result_report_s3_uri(AuthorizationHeader=authorization_header),
        "EvalEngineSfnExecutionArn": eval_engine_sfn_execution_arn
    }
    
    print(f'control_broker_request_status:\n{control_broker_request_status}')
    
    return {
        "ControlBrokerRequestStatus": control_broker_request_status
    }