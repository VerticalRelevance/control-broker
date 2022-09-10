import json, os, re
import subprocess
import shutil
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import errno

s3 = boto3.client('s3')
s3r = boto3.resource('s3')
lambda_ = boto3.client('lambda')

def invoke_lambda_async(*, function_name:str=None, payload:typing.Mapping[str, str]=None):
    if function_name == None:
        raise Exception('ERROR: function_name parameter cannot be NULL')
    payloadStr = json.dumps(payload)
    payloadBytesArr = bytes(payloadStr, encoding='utf8')
    try:
        r=lambda_.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=payloadBytesArr
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print(r)
        return True

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
 
def copyanything(source, destination):
    try:
        if os.path.exists(destination):
            print('Using existing .guard - lambda reused') 
            return True
        shutil.copytree(source, destination)
    except OSError as e:
        if e.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(source, destination)
        else:
            raise

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
    
def re_search(regex,item):
    m = re.search(regex,item)
    return m.group(1)
    
def lambda_handler(event, context):
    
    print(event)
    
    # get rules
    
    rules_dir = '/tmp/rules'
    
    rules_s3=json.loads(os.environ['RulesS3'])
    
    s3_download_dir(
        bucket = rules_s3['Bucket'],
        prefix = rules_s3['Prefix'],
        local_path = rules_dir
    )
    
    # get cfn
    
    input_to_be_analyzed_path = '/tmp/input_to_be_analyzed.json'
    
    # s3_download(
    #     bucket = event['InputToBeAnalyzed']['Bucket'],
    #     key = event['InputToBeAnalyzed']['Key'],
    #     local_path = input_to_be_analyzed_path
    # )
    
    with open(input_to_be_analyzed_path,'w') as f:
        json.dump(event['InputToBeEvaluated']['Input'],f,indent=2)
    
    copyanything('./.guard','/tmp/.guard')
    
    os.chmod('/tmp/.guard',755)
        
    shutil.copy('./cfn-guard-validate.sh','/tmp/cfn-guard-validate.sh')
    
    # eval
    
    cfn_guard_validate_result = run_bash(bash_path='/tmp/cfn-guard-validate.sh')
    
    print(f'CfnGuardValidateResult:\n{cfn_guard_validate_result}')
    print(type(cfn_guard_validate_result))
    
    stdout_ = cfn_guard_validate_result['stdout']
    print(f'stdout_:\n{stdout_}')
    print(type(stdout_))
    
    # result_dict = json.loads(stdout_.split('---')[1])
    # print(f'result_dict:\n{result_dict}')
    # print(type(result_dict))
    
    result_path='/tmp/result.json'
        
    try:
        Path(result_path).resolve(strict=True)
    except FileNotFoundError:
        # doesn't exist
        raise
    else:
    
        with open(result_path,'r') as f:
            lines=f.readlines()
            results=[]
            for line in lines:
                print(line)
                
                try:
                    result=json.loads(line)
                except json.decoder.JSONDecodeError:
                    pass
                else:
                    results.append(result)
                    
            print(f'results:\n{results}')
            
            output = {
                'CfnGuardValidateResults': results
            }
            
            invoke_lambda_async(
                function_name=os.environ['OutputHandlerLambda'],
                payload=output
            )
            
            return output