import json, os

def process_message(message):
    print('begin process_message')

def lambda_handler(event, context):

    print(event)

    for record in event['Records']:
        
        body=json.loads(record['body'])
        
        message=json.loads(body['Message'])
        
        message_account_id=message['configurationItem']['awsAccountId']
        
        spoke_accounts=json.loads(os.environ['SpokeAccounts'])
        
        if message_account_id in spoke_accounts:
            
            print(f'message_account_id ({message_account_id}) is in spoke_accounts:\n{spoke_accounts}')
            
            process_message(message)
        
        