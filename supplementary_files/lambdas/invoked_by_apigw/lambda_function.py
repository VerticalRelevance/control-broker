import json
import os

import boto3
from botocore.exceptions import ClientError

sfn = boto3.client('stepfunctions')

def get_result_report_s3_uri(*,AuthHeader):
    return 's3://cschneider-terraform-backend/foo.json'
    # FIXME - form path based on auth, make sure EvalEngine writes to that same path

def get_requestor_authorization_status(*,AuthHeader):
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
        return r["executionArn"]


def lambda_handler(event,context):
    
    print(event)
    
    eval_engine_sfn_arn = os.environ.get('ControlBrokerOuterSfnArn')
    print(f'eval_engine_sfn_arn:\n{eval_engine_sfn_arn}')
    
    headers = event.get('headers')
    
    auth_header = headers.get('authorization')
    
    print(f'auth_header:\n{auth_header}')
    
    
    """
    TODO:
    
    StartExecution (async) of Eval Engine
    
    
    """
    
    control_broker_request_status = {
        "RequestorIsAuthorized": get_requestor_authorization_status(AuthHeader=auth_header), # TODO
        "EvalEngineHasReadAccessToInputs": get_eval_engine_read_access_to_inputs_status(), # TODO
        "ResponseReportS3Path": get_result_report_s3_uri(AuthHeader=auth_header),
    }
    
    print(f'control_broker_request_status:\n{control_broker_request_status}')
    
    return {
        "ControlBrokerRequestStatus": control_broker_request_status
    }