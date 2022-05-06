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

    input_analyzed = request_json_body['InputAnalyzed']
    
    print(f'input_analyzed:\n{input_analyzed}')

    input_analyzed_object = get_object(
        bucket = input_analyzed['Bucket'],
        key = input_analyzed['Key']
    )
    
    print(f'input_analyzed_object:\n{input_analyzed_object}')

    return {
        "EvalEngineLambdalith": {
            "Evaluation": {
                "IsAllowed": get_is_allowed_decision()
            }
        }
    }