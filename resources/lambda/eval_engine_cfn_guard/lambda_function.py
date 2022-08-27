import json
import subprocess
import shutil
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
import re
import errno

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
 
def copyanything(source, destination):
    try:
        if os.path.exists(destination):
            # shutil.rmtree(destination) # permission error
            print('Using existing .guard - lambda reused') 
            return True
        shutil.copytree(source, destination)
    except OSError as e:
        if e.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(source, destination)
        else:
            raise

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
    return m.group(1)
    
def lambda_handler(event, context):
    
    print(event)
    
    # get rule
    
    rule_path = '/tmp/rule.guard'
    
    s3_download(
        Bucket = event['Rules']['Bucket'],
        Key = event['Rules']['Key'],
        LocalPath = rule_path
    )
    
    # get cfn
    
    input_to_be_analyzed_path = '/tmp/input_to_be_analyzed.json'
    
    s3_download(
        Bucket = event['InputToBeAnalyzed']['Bucket'],
        Key = event['InputToBeAnalyzed']['Key'],
        LocalPath = input_to_be_analyzed_path
    )
    
    copyanything('./.guard','/tmp/.guard')
    
    os.chmod('/tmp/.guard',755)
        
    shutil.copy('./cfn-guard-validate.sh','/tmp/cfn-guard-validate.sh')
    
    # eval
    
    cfn_guard_validate_result = run_bash(BashPath='/tmp/cfn-guard-validate.sh')
    
    print(f'CfnGuardValidateResult:\n{cfn_guard_validate_result}')
    print(type(cfn_guard_validate_result))
    
    stdout_ = cfn_guard_validate_result['stdout']
    print(f'stdout_:\n{stdout_}')
    print(type(stdout_))
    
    result_dict = json.loads(stdout_.split('---')[1])
    print(f'result_dict:\n{result_dict}')
    print(type(result_dict))

    
    r = {
        'CfnGuardValidateResult': result_dict
    }
    
    return r