import json
import shutil
import boto3
from botocore.exceptions import ClientError
import os
import logging
from pathlib import Path
import zipfile

s3 = boto3.client('s3')
cp = boto3.client('codepipeline')


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
        
      
def lambda_handler(event, context):
    
    print(event)
    
    job_id = event['CodePipeline.job']['id']
    
    input_artifact = event['CodePipeline.job']['data']['inputArtifacts'][0]['location']['s3Location']
    output_artifact = event['CodePipeline.job']['data']['outputArtifacts'][0]['location']['s3Location']
    
    user_params = json.loads(event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters'])
    buildspec = user_params['Buildspec']
    
    # set paths
    
    path_to_input_artifact = '/tmp/input_artifact'
    path_to_output_artifact = '/tmp/output_artifact'
    
    p = Path('/tmp/repo_and_buildspec')
    p.mkdir(parents=True,exist_ok=True)
    repo_and_buildspec_path = str(p)
    
    # get buildspec
    
    if not s3_download(
        Bucket = buildspec['Bucket'],
        Key = buildspec['Key'],
        LocalPath = f'{repo_and_buildspec_path}/buildspec.yaml'
    ):
        fail_pipeline(JobId=job_id,Message='buildspec download failed')
    
    # get repo
    
    if not s3_download(
        Bucket = input_artifact['bucketName'],
        Key = input_artifact['objectKey'],
        LocalPath = path_to_input_artifact
    ):
        fail_pipeline(JobId=job_id,Message='buildspec download failed')
    
    artifact_object = zipfile.ZipFile(path_to_input_artifact)
    
    for file in artifact_object.namelist():
        artifact_object.extract(file,repo_and_buildspec_path)
    
    shutil.make_archive(path_to_output_artifact,'zip',repo_and_buildspec_path)
    
    path_to_output_artifact = f'{path_to_output_artifact}.zip'
    
    if not upload_file(
        FileName = path_to_output_artifact,
        Bucket = output_artifact['bucketName'],
        Key = output_artifact['objectKey']
    ):
        fail_pipeline(JobId=job_id,Message='artifact upload failed')
    else:
        pass_pipeline(JobId=job_id)