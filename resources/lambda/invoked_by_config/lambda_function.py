import json
import boto3
import os
from botocore.exceptions import ClientError
from botocore.config import Config

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
            
def lambda_handler(event, context):
    
    print(event)
    
    invoking_event = json.loads(event["invokingEvent"])
    print(f"invoking_event:\n{invoking_event}")
    
    configuration_item = invoking_event["configurationItem"]
    print(f"configuration_item:\n{configuration_item}")

    item_status = configuration_item["configurationItemStatus"]
    print(f"item_status:\n{item_status}")
    
    if item_status == 'ResourceDeleted':
        return True

    resource_type = configuration_item["resourceType"]
    print(f"resource_type:\n{resource_type}")

    resource_configuration = configuration_item["configuration"]
    print(f"resource_configuration:\n{resource_configuration}")

    resource_id = configuration_item["resourceId"]
    print(f"resource_id:\n{resource_id}")

    result_token = event["resultToken"]
    print(f"result_token:\n{result_token}")
    
    config_rule_name = event["configRuleName"]
    print(f"config_rule_name:\n{config_rule_name}")

    # invoke sfn, pass event as input    
    
    execution_arn = async_sfn(sfn_arn=os.environ['ProcessingSfnArn'],input_=event)
    print(f'sfn execution_arn:\n{execution_arn}')