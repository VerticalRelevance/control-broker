import json, os
import boto3
from botocore.exceptions import ClientError

sqs = boto3.client('sqs')

def set_sqs_cbd(*,queue_url,cbd):
    
    try:
        sqs.set_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames={
                'ContentBasedDeduplication':cbd
            }
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        return True

def get_queue_cbd(queue_url):
    
    try:
        r=sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=[
                'ContentBasedDeduplication'
            ]
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        return r['Attributes']['ContentBasedDeduplication']

def toggle_sqs_cbd(queue_url):

    set_sqs_cbd(
        queue_url=queue_url,
        cbd = not get_queue_cbd(queue_url)
    )

def lambda_handler(event, context):
    
    print(event)
    
    queue_url=os.environ['QueueUrl']
    
    toggle_sqs_cbd(queue_url)
    