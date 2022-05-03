import json

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def put_object(bucket,key,object_:dict):
    print(f'put_object\nbucket:\n{bucket}\nKey:\n{key}')
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(object_)
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        return True

def s3_uri_to_bucket_key(*,Uri):
    path_parts=Uri.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key

def lambda_handler(event,context):
    print(event)
    
    bucket = event.get('Bucket')
    key = event.get('Key')
    
    if event.get('BucketArn'):
        bucket = event.get('BucketArn').split('arn:aws:s3:::')[1]
    
    if not bucket and not key:
        bucket, key = s3_uri_to_bucket_key(Uri=event['S3Uri'])

    put_object(
        bucket = bucket,
        key = key,
        object_ = event['Object']
    )

    return {
        "Bucket": bucket,
        "Key": key
    }    
    