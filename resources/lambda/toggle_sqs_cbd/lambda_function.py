import json, os
import boto3
from botocore.exceptions import ClientError

sqs = boto3.client('sqs')

def set_sqs_cbd(*,queue_url,cbd):
    
    try:
        sqs.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={
                'ContentBasedDeduplication':str(cbd).lower()
            }
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print(f'completed set_queue_attributes\nqueue_url:\n{queue_url}\ncbd:\n{cbd}')
        return True

def str_to_bool(item):
    
    return json.loads(item.lower())

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
        cbd= r['Attributes']['ContentBasedDeduplication']
        return cbd

def toggle_sqs_cbd(queue_url):

    set_sqs_cbd(
        queue_url=queue_url,
        cbd = not str_to_bool(get_queue_cbd(queue_url))
    )

def lambda_handler(event, context):
    
    print(event)
    
    # queue_url=os.environ['QueueUrl']
    queue_url=event['QueueUrl']
    print(f'queue_url:\n{queue_url}')
    
    toggle_sqs_cbd(queue_url)
    