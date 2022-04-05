import json
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from boto3.session import Session
import os
import re
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

def s3_download(*,Client,Bucket,Key,LocalPath):
    
    try:
        Client.download_file(
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

def upload_file(*,Client,FileName,Bucket,Key):

    try:
        response = Client.upload_file(FileName, Bucket, Key)
    except ClientError as e:
        print(f'ClientError upload_file:\nBucket: {Bucket}\nFileName: {FileName}\n{e}')
        return False
    else:
        print(f'No ClientError: upload_file:\nBucket: {Bucket}\nFileName: {FileName}\n')
        return True
        
def lambda_handler(event, context):
    
    # set paths
    
    path_to_input_artifact = '/tmp/input_artifact'
    path_to_output_artifact = '/tmp/output_artifact'
    
    e = Path('/tmp/extracted_artifact')
    e.mkdir(parents=True,exist_ok=True)
    extracted_artifact_path = str(e)
    
    # parse event
    
    print(event)
    
    job_id = event['CodePipeline.job']['id']
    
    input_artifact = event['CodePipeline.job']['data']['inputArtifacts'][0]['location']['s3Location']
    
    user_params = json.loads(event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters'])
    synthed_templates_bucket = user_params['SynthedTemplatesBucket']
    eval_engine_sfn_arn = user_params['EvalEngineSfnArn']

    artifacts_creds = event['CodePipeline.job']['data']['artifactCredentials']

    # temp creds

    session = Session(
        aws_access_key_id = artifacts_creds['accessKeyId'],
        aws_secret_access_key= artifacts_creds['secretAccessKey'],
        aws_session_token= artifacts_creds['sessionToken']
    )
    
    s3_temp_codepipeline_creds = session.client(
        's3',
        config = Config(signature_version='s3v4')
    )

    # get artifact
    
    if not s3_download(
        Client = s3_temp_codepipeline_creds,
        Bucket = input_artifact['bucketName'],
        Key = input_artifact['objectKey'],
        LocalPath = path_to_input_artifact
    ):
        fail_pipeline(JobId=job_id,Message='input artifact download failed')
    
    # unzip templates only
    
    artifact_object = zipfile.ZipFile(path_to_input_artifact)
    
    for file in artifact_object.namelist():
        m = re.search('cdk.out/.*\.template\.json',file)
        if m:
        # if file.endswith('.template.json'):
            print(file)
            artifact_object.extract(file,extracted_artifact_path)
    
    # for each template
    
    templates = {
        'Bucket': synthed_templates_bucket,
        'Keys': []
    }
    
    s3_lambda_iam_role_creds = boto3.client('s3')
            
    for root, dirs, files in os.walk(extracted_artifact_path):
        for filename in files:
            
            path = os.path.join(root, filename)
            
            if not upload_file(
                Client = s3_lambda_iam_role_creds,
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
        fail_pipeline(JobId=job_id,Message='failed to start_sync_execution')
    else:
        if r['status'] in ['FAILED','TIMED_OUT']:
            fail_pipeline(JobId=job_id,Message='eval engine root sfn failed or timeout')
        else:
            
            outer_sfn_exec_id = r['executionArn']
            
            output = json.loads(r['output'])
            print(f'output:\n{output}')
            
            nested_results = output['ForEachTemplate']
            
            results = [ {
                'Status' : i.get('TemplateToNestedSFN').get('Status'),
                'Cause': i.get('TemplateToNestedSFN').get('Cause'),
                'EvalResultsTablePk': f"{outer_sfn_exec_id}#{i.get('TemplateToNestedSFN').get('ExecutionArn')}"
            } for i in nested_results]
            
            print(f'results:\n{results}')
            
            if all(i['Status'] == 'SUCCEEDED' for i in results):
                
                pass_message = 'EvalEngineErrored == False\nAllNestedSFNReturnedSUCCEEDED == True\nInfractionsExist == False\nPipelineProceeds == True '
                
                pass_pipeline(JobId=job_id,Message=pass_message)
                
            elif [i for i in results if i['Status'] != 'SUCCEEDED' and i['Cause'] != 'InfractionsExist']:
                
                fail_message = 'EvalEngineErrored == True | AllNestedSFNReturnedSUCCEEDED == False | InfractionsExist == Unknown | PipelineProceeds == False | EvalEngine return status != "SUCCEEDED" with Cause != "InfractionsExist"'
                
                fail_pipeline(JobId=job_id,Message=fail_message)
                
            elif [i for i in results if i['Status'] != 'SUCCEEDED' and i['Cause'] == 'InfractionsExist']:
                
                fail_message = 'EvalEngineErrored == False | AllNestedSFNReturnedSUCCEEDED == False | InfractionsExist == True | PipelineProceeds == False'
                
                fail_pipeline(JobId=job_id,Message=fail_message)
                
            else:
                
                fail_message = 'Wrapper Unable to Parse SFN Response. Failing pipeline by default.'
                
                fail_pipeline(JobId=job_id,Message=fail_message)