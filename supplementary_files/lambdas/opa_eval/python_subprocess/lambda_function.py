import json
import subprocess
import shutil
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
import re

s3 = boto3.client('s3')
s3r = boto3.resource('s3')

def s3_download(*,bucket,key,local_path):
    
    try:
        s3.download_file(
            bucket,
            key,
            local_path
        )
    except ClientError as e:
        print(f'ClientError:\nbucket: {bucket}\nkey: {key}\n{e}')
        raise
    else:
        print(f'No ClientError download_file\nbucket:\n{bucket}\nkey:\n{key}')
        return True

def s3_download_dir(*,bucket, prefix=None, local_path):
    print(f'Begin s3_download_dir\nbucket:\n{bucket}\nprefix:\n{prefix}\nlocal_path:\n{local_path}')
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
                
def run_bash(*, bash_path):
    subprocess.run(["chmod","u+rx", bash_path])
    output = subprocess.run(["sh", f"{bash_path}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('raw subprocess output:')
    print(output)
    print('stdout:')
    stdout = output.stdout.decode('utf-8')
    print('stderr:')
    stderr = output.stderr.decode('utf-8')
    return {
        'stdout': stdout,
        'stderr': stderr
    }
    
def re_search(regex_group,search_me):
    m = re.search(regex_group,search_me)
    try:
        return m.group(1)
    except AttributeError:
        print(f'Regex:\n{regex_group}')
        print(f'search_me:\n{search_me}')
        raise

def mkdir(dir_):
    p = Path(dir_)
    p.mkdir(parents=True,exist_ok=True)
    return str(p)
    
def lambda_handler(event, context):
    
    print(event)
    
    opa_policies_bucket = event['OpaPolicies']['Bucket']
    
    json_input = event['JsonInput']
    
    # get policies
    
    policy_path_root = mkdir('/tmp/opa-policies')
    
    print(f'begin: Get Policies')
    
    s3_download_dir(
        bucket = opa_policies_bucket,
        local_path = policy_path_root
    )
    
    # get json_input
    
    json_input_path = '/tmp/input.json'
    
    print(f'begin: Get json_input')
    
    s3_download(
        bucket = json_input['Bucket'],
        key = json_input['Key'],
        local_path = json_input_path
    )
    
    # to tmp

    shutil.copy('./opa','/tmp/opa')
    
    os.chmod('/tmp/opa',755)
        
    shutil.copy('./opa-eval.sh','/tmp/opa-eval.sh')
    
    # # eval
    
    opa_eval_result = run_bash(bash_path='/tmp/opa-eval.sh')
    
    print(f'eval_result:\n{opa_eval_result}\n{type(opa_eval_result)}')

    stdout_ = json.loads(opa_eval_result.get('stdout'))
    print(f'stdout_:\n{stdout_}\n{type(stdout_)}')
    
    opa_eval_results = stdout_
    print(f'opa_eval_results:\n{opa_eval_results}\n{type(opa_eval_results)}')
    
    return {
        "OpaEvalResults": opa_eval_results
    }