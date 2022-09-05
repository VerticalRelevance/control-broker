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

def parse_sns_message_for_configuration_item(sns_message):
    try:
        configuration_item=sns_message['configurationItem']
    except KeyError:
        return False
    else:
        print(f'configuration_item:\n{configuration_item}')
        return configuration_item


def lambda_handler(event, context):
    
    print(event)
    
    sns_message=parse_event_for_sns_message(event)
    print(f'sns_message\n{sns_message}')

    if not sns_message:
        print('cannot resolve sns_message')
        return False
        
    configuration_item=parse_sns_message_for_configuration_item(sns_message)
    
    if not configuration_item:
        print('cannot resolve configuration_item')
        return False
    
    if configuration_item['awsAccountId'] not in json.loads(os.environ['SpokeAccountIds']):
        print(f"configuration_item.awsAccountId ({configuration_item['awsAccountId']}) not in spoke_account_ids:\n{json.loads(os.environ['SpokeAccountIds'])}")
        return False
        
    execution_arn = async_sfn(sfn_arn=os.environ['ProcessingSfnArn'],input_=sns_message)
    print(f'sfn execution_arn:\n{execution_arn}')