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

def s3_download(*,Bucket,Key,LocalPath):
    
    try:
        s3.download_file(
            Bucket,
            Key,
            LocalPath
        )
    except ClientError as e:
        print(f'ClientError:\nBucket: {Bucket}\nKey: {Key}\n{e}')
        raise
    else:
        print('No ClientError download_file')
        return True

def s3_download_dir(*,Bucket, Prefix=None, LocalPath):
    print(f'Begin s3_download_dir\nBucket:\n{Bucket}\nPrefix:\n{Prefix}\nLocalPath:\n{LocalPath}')
    paginator = s3.get_paginator('list_objects')
    
    if Prefix:
        pagination = paginator.paginate(Bucket=Bucket, Delimiter='/', Prefix=Prefix)
    else:
        pagination = paginator.paginate(Bucket=Bucket, Delimiter='/')
            
    for result in pagination:
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                s3_download_dir(
                    Prefix = subdir.get('Prefix'),
                    LocalPath = LocalPath,
                    Bucket = Bucket
                )
        for file in result.get('Contents', []):
            dest_pathname = os.path.join(LocalPath, file.get('Key'))
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            if not file.get('Key').endswith('/'):
                s3_download(
                    Bucket=Bucket,
                    Key=file.get('Key'),
                    LocalPath=dest_pathname
                )
                
def run_bash(*, BashPath):
    subprocess.run(["chmod","u+rx", BashPath])
    output = subprocess.run(["sh", f"{BashPath}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    
def re_search(RegexGroup,SearchMe):
    m = re.search(RegexGroup,SearchMe)
    try:
        return m.group(1)
    except AttributeError:
        print(f'Regex:\n{RegexGroup}')
        print(f'SearchMe:\n{SearchMe}')
        raise

def mkdir(Dir):
    p = Path(Dir)
    p.mkdir(parents=True,exist_ok=True)
    return str(p)
    
        
def lambda_handler(event, context):
    
    print(event)
    
    opa_policies_bucket = event['OpaPolicies']['Bucket']
    
    json_input = event['JsonInput']
    
    # get policies
    
    policy_path_root = mkdir('/tmp/opa-policies')
    
    s3_download_dir(
        Bucket = opa_policies_bucket,
        LocalPath = policy_path_root
    )
    
    # get json_input
    
    json_input_path = '/tmp/input.json'
    
    s3_download(
        Bucket = json_input['Bucket'],
        Key = json_input['Key'],
        LocalPath = json_input_path
    )
    
    # to tmp

    shutil.copy('./opa','/tmp/opa')
    
    os.chmod('/tmp/opa',755)
        
    shutil.copy('./opa-eval.sh','/tmp/opa-eval.sh')
    
    # # eval
    
    opa_eval_result = run_bash(BashPath='/tmp/opa-eval.sh')
    
    print(f'eval_result:\n{opa_eval_result}\n{type(opa_eval_result)}')

    stdout_ = json.loads(opa_eval_result.get('stdout'))
    print(f'stdout_:\n{stdout_}\n{type(stdout_)}')
    
    opa_eval_results = [{"PackagePlaceholder":stdout_[i]} for i in stdout_]
    print(f'opa_eval_results:\n{opa_eval_results}\n{type(opa_eval_results)}')
    
    return {
        "OpaEvalResults": opa_eval_results
    }