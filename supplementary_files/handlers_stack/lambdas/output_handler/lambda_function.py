import json
import subprocess
import shutil
import re
import os
from pathlib import Path

import requests

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
s3r = boto3.resource('s3')

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

def handle_infractions(infractions):
    
    for infraction in infractions:
        
        print(f'begin processing infractions:\n{infraction}')

        # TODO

def parse_pac_results(pac_results):
    
    opa_eval_results = pac_results
    
    reserved_keys = ['ApprovedContext','EvaluationContext','InputType']

    for k in reserved_keys:
        opa_eval_results.pop(k,None)
    
    print(f'opa_eval_results:\n{opa_eval_results}')
    
    infractions = [ {i:opa_eval_results[i]}for i in opa_eval_results if opa_eval_results[i].get('allow') == False]
    
    print(f'infractions:\n{infractions}\n')
    
    is_allowed = not bool(infractions)
    
    return infractions, is_allowed  

def s3_object_lambda_send_response(*,request_route,request_token,response_object:dict):
    
    try:
        s3.write_get_object_response(
            RequestRoute=request_route,
            RequestToken=request_token,
            Body=json.dumps(response_object).encode('utf-8'),
        )
    except ClientError as e:
        print(f'ClientError:\nrequest_route:\n{request_route}\nrequest_token:\n{request_token}\n{e}')
        raise
    else:
        print(f'no ClientError write_get_object_response:\nrequest_route:\n{request_route}\nrequest_token:\n{request_token}\n{e}')

    return {'status_code': 200}    

def lambda_handler(event,context):
    
    print(f'event\n{event}\ncontext:\n{context}')
    
    ### event- driven
    
    # invoked_by = {
    #     'Bucket': event['Records'][0]['s3']['bucket']['name'],
    #     'Key': event['Records'][0]['s3']['object']['key']
    # }
    
    # print(f'invoked_by:\n{invoked_by}')

    # invoked_by_object = get_object(
    #     bucket = invoked_by['Bucket'],
    #     key = invoked_by['Key']
    # )
    
    # print(f'invoked_by_object:\n{invoked_by_object}')
    
    ### s3 object lambda

    object_get_context = event["getObjectContext"]
    request_route = object_get_context["outputRoute"]
    request_token = object_get_context["outputToken"]
    original_object_s3_url = object_get_context["inputS3Url"]

    # Get object from S3
    
    original_object_response = requests.get(original_object_s3_url)
    
    original_object = json.loads(original_object_response.content.decode('utf-8'))
    
    print(f'original_object:\n{original_object}\n')

    pac_results = original_object
    
    infractions, is_allowed = parse_pac_results(pac_results)
    
    handle_infractions(infractions)

    results_report = {
        "EvalEngineLambdalith": {
            "Evaluation": {
                "IsAllowed": is_allowed
            },
            "Infractions":infractions
        }
    }
    
    print(f'results_report:\n{results_report}\n')
    
    return s3_object_lambda_send_response(
        request_route=request_route,
        request_token=request_token,
        response_object=results_report
    )
