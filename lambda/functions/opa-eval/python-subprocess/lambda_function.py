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

def s3_download_dir(*,Bucket, PathToS3Dir, LocalPath):
    paginator = s3.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=Bucket, Delimiter='/', Prefix=PathToS3Dir):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                s3_download_dir(
                    PathToS3Dir = subdir.get('Prefix'),
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
        
def lambda_handler(event, context):
    
    print(event)
    
    # get policy
    
    policy_path = '/tmp/policy.rego'
    
    policies_key = event['Policies']['Key']
    print(policies_key)
    
    service = re_search('(.*)/.*\.rego',policies_key)
    print(f'service:\n{service}')
    
    package_suffix = re_search(f'{service}/(.*)\.rego',policies_key)
    print(f'package_suffix:\n{package_suffix}')
    
    s3_download(
        Bucket = event['Policies']['Bucket'],
        Key = event['Policies']['Key'],
        LocalPath = policy_path
    )
    
    # get cfn
    
    cfn_path = '/tmp/cfn.json'
    
    s3_download(
        Bucket = event['CFN']['Bucket'],
        Key = event['CFN']['Key'],
        LocalPath = cfn_path
    )
    
    # to tmp

    shutil.copy('./opa','/tmp/opa')
    
    os.chmod('/tmp/opa',755)
        
    shutil.copy('./opa-eval.sh','/tmp/opa-eval.sh')
    
    # eval
    
    opa_eval_result = run_bash(BashPath='/tmp/opa-eval.sh')
    
    print(f'opa_eval_result:\n{opa_eval_result}')
    print(type(opa_eval_result))
    
    stdout_ = json.loads(opa_eval_result.get('stdout'))
    print(f'stdout_:\n{stdout_}\n{type(stdout_)}')
    
    deny = stdout_[package_suffix]['deny']
    print(f'deny:\n{deny}\n{type(deny)}')
    
    infractions = stdout_[package_suffix]['infraction']
    print(f'infractions:\n{infractions}\n{type(infractions)}')
    
    return {
        'OPAEvalDenyResult' : str(deny),
        'Infractions': infractions,
    }