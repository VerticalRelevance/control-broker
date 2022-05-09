import json
import subprocess
import shutil
import re
import os
from pathlib import Path

import requests

import boto3
from botocore.exceptions import ClientError

eb = boto3.client('events')
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
        print(f'no ClientError get_object:\nbucket:\n{bucket}\nkey:\n{key}\n')
        body = r['Body']
        content = json.loads(body.read().decode('utf-8'))
        return content


def put_event_entry(*,
    event_bus_name:str,
    detail:dict,
    source:str=os.environ['AWS_LAMBDA_FUNCTION_NAME'],
    detail_type:str=os.environ['AWS_LAMBDA_FUNCTION_NAME'],
):
    try:
        r = eb.put_events(
            Entries = [
                {
                    'EventBusName':event_bus_name,
                    'Detail':json.dumps(detail),
                    'DetailType':detail_type,
                    'Source':source,
                }
            ]
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        return False
    else:
        print(r)
        print(f'no ClientError: put_events')
        return True

def handle_infraction(infraction:dict):
    
    print(f'begin processing infraction:\n{infraction}')

    put_event_entry(
        event_bus_name = os.environ['InfractionsEventBusName'],
        detail = infraction
    )
    

def handle_infractions(infractions:list):
    
    for infraction in infractions:
        
        handle_infraction(infraction)

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
        print(f'no ClientError write_get_object_response:\nrequest_route:\n{request_route}\nrequest_token:\n{request_token}')

    return {'status_code': 200}    

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

    # get original
    
    original_object_response = requests.get(original_object_s3_url)
    
    original_object = json.loads(original_object_response.content.decode('utf-8'))
    
    print(f'original_object:\n{original_object}\n')

    # parse pac results

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
    
    # put response
    
    return s3_object_lambda_send_response(
        request_route=request_route,
        request_token=request_token,
        response_object=results_report
    )
