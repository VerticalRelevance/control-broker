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

def put_object(*,bucket,key,object_:dict):
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(object_)
        )
    except ClientError as e:
        print(f'ClientError:\nbucket:\n{bucket}\nkey:\n{key}\n{e}')
        raise
    else:
        print(f'no ClientError put_object:\nbucket:\n{bucket}\nkey:\n{key}')
        return True
        
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

def mkdir(dir_):
    p = Path(dir_)
    p.mkdir(parents=True,exist_ok=True)
    return str(p) 

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

def write_to_tmp(object_,filename):
    
    with open(f'/tmp/{filename}','w') as f:
        json.dump(object_,f,indent=2)

def lambda_handler(event,context):
    print(f'event\n{event}\ncontext:\n{context}')
    
    request_json_body = json.loads(event['body'])
    
    print(f'request_json_body:\n{request_json_body}')

    input_to_be_evaluated = request_json_body['InputToBeEvaluated']
    
    print(f'input_to_be_evaluated:\n{input_to_be_evaluated}')
    
    # write InputType to tmp
    
    input_type = {
        "InputType":request_json_body['InputType']
    }
    
    write_to_tmp(input_type,'input_type.json')
    
    # write approved_context to tmp
    
    approved_context = {
        "ApprovedContext":request_json_body['Context']
    }
    
    write_to_tmp(approved_context,'approved_context.json')
    
    # get evaluation context
    
    evaluation_context_path = '/tmp/evaluation_context.json'
    
    evaluation_context = json.loads(os.environ['EvaluationContext'])
    
    s3_download(
        bucket = evaluation_context['Bucket'],
        key = evaluation_context['Key'],
        local_path = evaluation_context_path
    )
    
    # write ConsumerMetadata to /tmp
    
    consumer_metadata= request_json_body['ConsumerMetadata']
    
    print(f'consumer_metadata:\n{consumer_metadata}')

    write_to_tmp(consumer_metadata,'consumer_metadata.json')

    # write input_analyzed_object to /tmp
    
    input_to_be_evaluated_object_path = '/tmp/input_to_be_evaluated_object.json'
    
    s3_download(
        bucket = input_to_be_evaluated['Bucket'],
        key = input_to_be_evaluated['Key'],
        local_path = input_to_be_evaluated_object_path
    )
    
    # get PaC Framework Policies
    
    policy_path_root = mkdir('/tmp/pac_policies')
    
    s3_download_dir(
        bucket = os.environ['PaCPoliciesBucket'],
        local_path = policy_path_root,
        prefix = os.environ['PaCFramework']
    )

    # opa to tmp

    shutil.copy('./opa','/tmp/opa')
    
    os.chmod('/tmp/opa',755)
        
    shutil.copy('./opa-eval.sh','/tmp/opa-eval.sh')
    
    # eval
    
    opa_eval_result = run_bash(bash_path='/tmp/opa-eval.sh')
    
    print(f'eval_result:\n{opa_eval_result}\n{type(opa_eval_result)}')

    stdout_ = json.loads(opa_eval_result.get('stdout'))
    print(f'stdout_:\n{stdout_}\n{type(stdout_)}')
    
    opa_eval_results = stdout_
    print(f'opa_eval_results:\n{opa_eval_results}\n{type(opa_eval_results)}')
    
    # put raw pac results
    
    response_expected_by_consumer = request_json_body['ResponseExpectedByConsumer']
    
    put_object(
        bucket=response_expected_by_consumer['ControlBrokerEvaluation']['Raw']['Bucket'],
        key=response_expected_by_consumer['ControlBrokerEvaluation']['Raw']['Key'],
        object_ = opa_eval_results
    )
    
    return True
    