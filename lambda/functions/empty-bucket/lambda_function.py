import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
cp = boto3.client('codepipeline')

def fail_pipeline(*,JobId,Message):
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

def pass_pipeline(*,JobId,Message):
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
  

def lambda_handler(event, context):
    print(event)
    params = json.loads(event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters'])
    job_id = event['CodePipeline.job']['id']
    
    bucket = params['BucketToEmpty']
    
    try:
        contents = s3.list_objects_v2(Bucket=bucket)
    except ClientError as error:
        message = error.response['Error']['Message']
        fail_pipeline(JobId=job_id,Message=message)
    else:
        try:
            contents = [item['Key'] for item in contents['Contents']]
        except KeyError:
            print("No Contents Found.")
            pass_pipeline(JobId=job_id,Message='Already empty')
        else:
            print(f"\nWithin bucket ({bucket}):")
            for item in contents:
                print(f"\tDeleting... {item}")
                try:
                    s3.delete_object(Bucket=bucket,Key=item)
                except ClientError as error:
                    message = error.response['Error']['Message']
                    fail_pipeline(JobId=job_id,Message=message)
                else:
                    print(f"\tDeleted: {item}")
            pass_pipeline(JobId=job_id,Message='Emptied')
