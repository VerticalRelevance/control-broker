import json
import subprocess
import shutil
import re
import os
from pathlib import Path

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

def s3_download(*,bucket,key,local_path):
    
    try:
        s3.download_file(
            bucket,
            key,
            local_path
        )
    except ClientError as e:
        print(f'ClientError:\nbucket: {bucket}\nkey:\n{key}\n{e}')
        raise
    else:
        # print(f'No ClientError download_file\nbucket:\n{bucket}\nkey:\n{key}')
        return True

def s3_download_dir(*,bucket, prefix=None, local_path):
    # print(f'Begin s3_download_dir\nbucket:\n{bucket}\nprefix:\n{prefix}\nlocal_path:\n{local_path}')
    paginator = s3.get_paginator('list_objects')
    
    if prefix:
        pagination = paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=prefix)
    else:
        pagination = paginator.paginate(Bucket=bucket, Delimiter='/')
            
    for result in pagination:
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                s3_download_dir(
                    prefix = subdir.get('Prefix'),
                    local_path = local_path,
                    bucket = bucket
                )
        for file in result.get('Contents', []):
            dest_pathname = os.path.join(local_path, file.get('Key'))
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            if not file.get('Key').endswith('/'):
                s3_download(
                    bucket=bucket,
                    key=file.get('Key'),
                    local_path=dest_pathname
                )


def lambda_handler(event,context):
    print(f'event\n{event}\ncontext:\n{context}')
    
    # reserved_keys = ['ApprovedContext','EvaluationContext','InputType']

    # for k in reserved_keys:
    #     opa_eval_results.pop(k,None)
    
    # print(f'opa_eval_results:\n{opa_eval_results}\n{type(opa_eval_results)}')
    
    # infractions = [ {i:opa_eval_results[i]}for i in opa_eval_results if opa_eval_results[i].get('allow') == False]

    # print(f'infractions:\n{infractions}\n{type(infractions)}')
    
    # return {
    #     "EvalEngineLambdalith": {
    #         "Evaluation": {
    #             "IsAllowed": not bool(infractions)
    #         },
    #         "Infractions":infractions
    #     }
    # }