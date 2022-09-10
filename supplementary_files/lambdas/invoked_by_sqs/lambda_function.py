import json, os
import boto3

from botocore.exceptions import ClientError

sqs= boto3.client("sqs")

def process_message_subject_to_pac(message):
    print('begin process_message')

def delete_message(*,queue_url,receipt_handle):
    
    try:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        return True

def lambda_handler(event, context):

    print(event)
    
    for record in event['Records']:
        
        body=json.loads(record['body'])
        
        message=json.loads(body['Message'])
        
        message_account_id=message['configurationItem']['awsAccountId']
        
        message_resource_type=message['configurationItem']['resourceType']
        
        spoke_accounts=json.loads(os.environ['SpokeAccounts'])
        
        resource_types_subject_to_pac=json.loads(os.environ['ResourceTypesSubjectToPac'])
        
        if message_account_id in spoke_accounts and message_resource_type in resource_types_subject_to_pac:
            
            print(f'message_account_id ({message_account_id}) is in spoke_accounts:\n{spoke_accounts}')
            
            process_message_subject_to_pac(message)
        
        delete_message(
            queue_url=os.environ['QueueUrl'],
            receipt_handle=record['receiptHandle']
        )