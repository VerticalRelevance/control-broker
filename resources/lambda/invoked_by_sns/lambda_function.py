import json, os

import boto3
from botocore.exceptions import ClientError

def parse_event_for_sns_message(event):
    
    try:
        records=event['Records']
    except KeyError:
        return False
    else:
        try:
            first_record=records[0]
        except IndexError:
            return False
        else:
            try:
                sns_block=first_record['Sns']
            except KeyError:
                return False
            else:
                try:
                    message=sns_block['Message']
                except KeyError:
                    return False
                else:
                    return json.loads(message)

def process_configuration_item(configuration_item):
    print(f'beging process_configuration_item')

def lambda_handler(event, context):
    
    print(event)
    
    sns_message=parse_event_for_sns_message(event)

    if not sns_message:
        return False
        
    spoke_account_ids=os.environ['SpokeAccountIds']
    print(spoke_account_ids)
    print(type(spoke_account_ids))

    configuration_item=sns_message['configurationItem']
    print(f'configuration_item:\n{configuration_item}')
    
    if configuration_item['awsAccountId'] not in spoke_account_ids:
        print(f"configuration_item.awsAccountId ({configuration_item['awsAccountId']}) not in spoke_account_ids:\n{spoke_account_ids}")
        return False
        
    process_configuration_item(configuration_item)