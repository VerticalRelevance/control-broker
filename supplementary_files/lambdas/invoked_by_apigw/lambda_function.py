import json
import os
import re
import uuid

import boto3
from botocore.exceptions import ClientError

sfn = boto3.client('stepfunctions')


def extract_acces_key_id(*,aws4_authorization):
    m = re.search('AWS4-HMAC-SHA256 Credential=(\w*)/.*',aws4_authorization)
    return m.group(1)
    
def generate_uuid():
    return str(uuid.uuid4())
    
def get_result_report_s3_uri(*,eval_results_reports_bucket):
    
    uuid = generate_uuid()

    s3_uri = f's3://{eval_results_reports_bucket}/cb-{uuid}'
    
    return s3_uri

def get_requestor_authorization_status(*,authorization_header):
    return True
    # TODO

def get_eval_engine_read_access_to_inputs_status():
    return True
    #TODO

def async_sfn(*, sfn_arn, input: dict):
    try:
        r = sfn.start_execution(stateMachineArn=sfn_arn, input=json.dumps(input))
    except ClientError as e:
        print(f"ClientError\n{e}")
        raise
    else:
        print(f'no ClientError start_execution:\nsfn_arn:\n{sfn_arn}\ninput:\n{input}')
        return r["executionArn"]


def lambda_handler(event,context):
    
    print(f'event:\n{event}\ncontext:\n{context}')
    
    post_request_json_body = json.loads(event['body'])
    
    eval_engine_sfn_arn = os.environ.get('ControlBrokerOutersfn_arn')
    print(f'eval_engine_sfn_arn:\n{eval_engine_sfn_arn}')
    
    eval_results_reports_bucket = os.environ.get('ControlBrokerEvalResultsReportsBucket')
    print(f'eval_results_reports_bucket:\n{eval_results_reports_bucket}')
    
    headers = event.get('headers')
    
    authorization_header = headers.get('authorization')
    
    print(f'authorization_header:\n{authorization_header}')
    
    result_report_s3_path = get_result_report_s3_uri(
        eval_results_reports_bucket = eval_results_reports_bucket
    )
    
    eval_engine_sfn_input = {
        "InvokedByApigw": post_request_json_body,
        "ResultsReportS3Uri": result_report_s3_path
    }
    
    eval_engine_sfn_execution_arn = async_sfn(
        sfn_arn = eval_engine_sfn_arn,
        input = eval_engine_sfn_input
    )
    
    control_broker_request_status = {
        "RequestorIsAuthorized": get_requestor_authorization_status(authorization_header=authorization_header),
        "EvalEngineHasReadAccessToinputs": get_eval_engine_read_access_to_inputs_status(),
        "ResultsReportS3Uri": result_report_s3_path,
        "EvalEngineSfnExecutionArn": eval_engine_sfn_execution_arn
    }
    
    print(f'control_broker_request_status:\n{control_broker_request_status}')
    
    return {
        "ControlBrokerRequestStatus": control_broker_request_status
    }