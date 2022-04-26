import json
import os
import re

import boto3
from botocore.exceptions import ClientError

sfn = boto3.client('stepfunctions')


def extract_acces_key_id(*,Aws4Authorization):
    m = re.search('AWS4-HMAC-SHA256 Credential=(\w*)/.*',Aws4Authorization)
    return m.group(1)

def get_result_report_s3_uri(*,EvalResultsReportsBucket,AuthorizationHeader):
    
    access_key_id = extract_acces_key_id(Aws4Authorization=AuthorizationHeader)
    
    result_report_s3_uri = f's3://{EvalResultsReportsBucket}/{access_key_id}/response.json'
    return result_report_s3_uri

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
    
    print(f'event:\n{event}\ncontext:\n{context}')
    
    post_request_json_body = json.loads(event['body'])
    
    eval_engine_sfn_arn = os.environ.get('ControlBrokerOuterSfnArn')
    print(f'eval_engine_sfn_arn:\n{eval_engine_sfn_arn}')
    
    eval_results_reports_bucket = os.environ.get('ControlBrokerEvalResultsReportsBucket')
    print(f'eval_results_reports_bucket:\n{eval_results_reports_bucket}')
    
    headers = event.get('headers')
    
    authorization_header = headers.get('authorization')
    
    print(f'authorization_header:\n{authorization_header}')
    
    result_report_s3_path = get_result_report_s3_uri(
        EvalResultsReportsBucket = eval_results_reports_bucket,
        AuthorizationHeader = authorization_header
    )
    
    eval_engine_sfn_input = {
        "InvokedByApigw": post_request_json_body,
        "ResultsReportS3Uri": result_report_s3_path
    }
    
    eval_engine_sfn_execution_arn = async_sfn(
        SfnArn = eval_engine_sfn_arn,
        Input = eval_engine_sfn_input
    )
    
    control_broker_request_status = {
        "RequestorIsAuthorized": get_requestor_authorization_status(AuthorizationHeader=authorization_header),
        "EvalEngineHasReadAccessToInputs": get_eval_engine_read_access_to_inputs_status(),
        "ResultsReportS3Uri": result_report_s3_path,
        "EvalEngineSfnExecutionArn": eval_engine_sfn_execution_arn
    }
    
    print(f'control_broker_request_status:\n{control_broker_request_status}')
    
    return {
        "ControlBrokerRequestStatus": control_broker_request_status
    }