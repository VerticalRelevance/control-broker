import json
import subprocess
import shutil
import re
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

eb = boto3.client('events')
s3 = boto3.client('s3')

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

def put_object(bucket,key,object_:dict):
    print(f'put_object\nbucket:\n{bucket}\nKey:\n{key}')
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(object_)
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        return True
        
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

def handle_infraction(*,infraction:dict,original_object_key:str):
    
    print(f'begin processing infraction:\n{infraction}')

    put_event_entry(
        event_bus_name = os.environ['InfractionsEventBusName'],
        source='ControlBroker',
        detail = infraction,
        detail_type=original_object_key
    )
    
def handle_infractions(*,infractions:list,original_object_key:str):
    
    for infraction in infractions:
        
        handle_infraction(
            infraction=infraction,
            original_object_key=original_object_key
        )

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
    
    invoked_by = {
        'Bucket': event['Records'][0]['s3']['bucket']['name'],
        'Key': event['Records'][0]['s3']['object']['key']
    }
    
    print(f'invoked_by:\n{invoked_by}')

    invoked_by_object = get_object(
        bucket = invoked_by['Bucket'],
        key = invoked_by['Key']
    )
    
    print(f'invoked_by_object:\n{invoked_by_object}')
    
    # parse pac results

    pac_results = invoked_by_object
    
    infractions, is_allowed = parse_pac_results(pac_results)
    
    handle_infractions(
        infractions=infractions,
        original_object_key=invoked_by['key']
    )

    results_report = {
        "EvalEngineLambdalith": {
            "Evaluation": {
                "IsCompliant": is_allowed
            },
            "Infractions":infractions
        }
    }
    
    print(f'results_report:\n{results_report}\n')
    
    return put_object(
        bucket = os.environ['OutputHandlerProcessedResultsBucket'],
        key = invoked_by['key'],
        object_ = results_report
    )