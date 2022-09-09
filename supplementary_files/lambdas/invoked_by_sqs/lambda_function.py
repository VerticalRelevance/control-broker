import json, os

def process_message(message):
    print('begin process_message')

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
            
            process_message(message)
        
        