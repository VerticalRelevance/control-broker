import json, os

import boto3
from botocore.exceptions import ClientError

sfn = boto3.client('stepfunctions')

def async_sfn(*,sfn_arn,input_:dict):
    try:
        r = sfn.start_execution(
            stateMachineArn = sfn_arn,
            input = json.dumps(input_)
        )
    except ClientError as e:
        print(f'ClientError\n{e}')
        raise
    else:
        return r['executionArn']

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

def lambda_handler(event, context):
    
    print(event)
    
    sns_message=parse_event_for_sns_message(event)
    print(f'sns_message\n{sns_message}')

    if not sns_message:
        return False
        
    spoke_account_ids=json.loads(os.environ['SpokeAccountIds'])
    print(f'spoke_account_ids:\n{spoke_account_ids}\n{type(spoke_account_ids)}')


    configuration_item=sns_message['configurationItem']
    print(f'configuration_item:\n{configuration_item}')
    
    if configuration_item['awsAccountId'] not in spoke_account_ids:
        print(f"configuration_item.awsAccountId ({configuration_item['awsAccountId']}) not in spoke_account_ids:\n{spoke_account_ids}")
        return False
        
    execution_arn = async_sfn(sfn_arn=os.environ['ProcessingSfnArn'],input_=configuration_item)
    print(f'sfn execution_arn:\n{execution_arn}')