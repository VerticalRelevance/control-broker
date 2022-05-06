from random import getrandbits
import json

import boto3
from botocore.exceptions import ClientError

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
        print(f'no ClientError get_object:\nbucket:\n{bucket}\nkey:\n{key}')
        body = r['Body']
        content = json.loads(body.read().decode('utf-8'))
        return content

def get_is_allowed_decision():
    return bool(getrandbits(1))

def lambda_handler(event,context):
    print(f'event\n{event}\ncontext:\n{context}')
    
    
    request_json_body = json.loads(event['body'])
    
    print(f'request_json_body:\n{request_json_body}')
    
    return {
        "EvalEngineLambdalith": {
            "Evaluation": {
                "IsAllowed": get_is_allowed_decision()
            }
        }
    }