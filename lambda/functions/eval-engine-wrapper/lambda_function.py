import json
import shutil
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
import zipfile

s3 = boto3.client('s3')
cp = boto3.client('codepipeline')
sfn = boto3.client('stepfunctions')


def fail_pipeline(*,JobId,Message='FailedByLambda'):
    print(f'Failing job ({JobId}).')
    try:
        cp.put_job_failure_result(
            jobId=JobId,
            failureDetails={
                'type': 'JobFailed',
                'message': Message,
            }
        )
    except ClientError as e:
        print(f"\nClientError:\n{e}\n")
        return False
    else:
        return True

def pass_pipeline(*,JobId,Message='PassedByLambda'):
    print(f'Passing job ({JobId}).')
    try:
        cp.put_job_success_result(
            jobId=JobId,
            executionDetails={
                'summary': Message,
            }
        )
    except ClientError as e:
        print(f"\nClientError:\n{e}\n")
        return False
    else:
        return True

def s3_download(*,Bucket,Key,LocalPath):
    
    try:
        s3.download_file(
            Bucket,
            Key,
            LocalPath
        )
    except ClientError as e:
        print(f'ClientError:\nBucket: {Bucket}\nKey: {Key}\n{e}')
        return False
    else:
        print('No ClientError download_file')
        return True

def upload_file(*,FileName, Bucket, Key):

    try:
        response = s3.upload_file(FileName, Bucket, Key)
    except ClientError as e:
        print(f'ClientError upload_file:\nBucket: {Bucket}\nFileName: {FileName}\n{e}')
        return False
    else:
        print(f'No ClientError: upload_file:\nBucket: {Bucket}\nFileName: {FileName}\n')
        return True

# def template_to_sfn(*,):
#     pass

def lambda_handler(event, context):
    
    print(event)
    
    job_id = event['CodePipeline.job']['id']
    input_artifact = event['CodePipeline.job']['data']['inputArtifacts'][0]['location']['s3Location']
    user_params = json.loads(event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters'])

    synthed_templates_bucket = user_params['SynthedTemplatesBucket']
    eval_engine_sfn_arn = user_params['EvalEngineSfnArn']

    # set paths
    
    path_to_input_artifact = '/tmp/input_artifact'
    path_to_output_artifact = '/tmp/output_artifact'
    
    e = Path('/tmp/extracted_artifact')
    e.mkdir(parents=True,exist_ok=True)
    extracted_artifact_path = str(e)

    # get artifact
    
    if not s3_download(
        Bucket = input_artifact['bucketName'],
        Key = input_artifact['objectKey'],
        LocalPath = path_to_input_artifact
    ):
        fail_pipeline(JobId=job_id,Message='input artifact download failed')
    
    # unzip templates only
    
    artifact_object = zipfile.ZipFile(path_to_input_artifact)
    
    for file in artifact_object.namelist():
        if file.endswith('.template.json'):
            print(file)
            artifact_object.extract(file,extracted_artifact_path)
    
    # for each template
    
    templates = {
        'Bucket': synthed_templates_bucket,
        'Keys': []
    }
            
    for root, dirs, files in os.walk(extracted_artifact_path):
        for filename in files:
            
            path = os.path.join(root, filename)
            
            if not upload_file(
                FileName = path,
                Bucket = synthed_templates_bucket,
                Key = filename
            ):
                fail_pipeline(JobId=job_id,Message='upload failed')
            
            templates['Keys'].append(filename)
            
    try:
        r = sfn.start_sync_execution(
            stateMachineArn = eval_engine_sfn_arn,
            input = json.dumps({
                'CFN': templates
            })
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print(r)
        if r['status'] in ['FAILED','TIMED_OUT']:
            fail_pipeline(JobId=job_id,Message='eval engine root sfn failed or timeout')
        else:
            output = json.loads(r['output'])
            
            print(f'output:\n{output}\n{type(output)}')
            
            nested_results = output['ForEachTemplate']
            
            results = [ {
                'Status' : i.get('TemplateToNestedSFN').get('Status'),
                'Cause': i.get('TemplateToNestedSFN').get('Cause')
            } for i in nested_results]
            
            print(results)
            
            if any(i['Status'] != 'SUCCEEDED' for i in results):
                fail_pipeline(JobId=job_id,Message='A eval engine result was not SUCCEEDED')
            elif all(i['Status'] == 'SUCCEEDED' for i in results):
                pass_pipeline(JobId=job_id,Message='All eval engine results were SUCCEEDED')
            else:
                fail_pipeline(JobId=job_id,Message='DefaultFailure')