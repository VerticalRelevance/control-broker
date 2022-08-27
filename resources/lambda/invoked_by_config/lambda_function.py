import json
import boto3
import os
from botocore.exceptions import ClientError
from botocore.config import Config

sfn = boto3.client('stepfunctions')

def sync_sfn(*,SfnArn,Input:dict):
    try:
        r = sfn.start_sync_execution(
            stateMachineArn = SfnArn,
            input = json.dumps(Input)
        )
    except ClientError as e:
        print(f'ClientError\n{e}')
        raise
    else:
        print(r)
        if r['status'] != 'SUCCEEDED':
            print(f'ProcessingSfn Status not SUCCEEDED')
            return False
        else:
            output = r['output']
            print(f'output:\n{output}\n{type(output)}')
            return output

def async_sfn(*,SfnArn,Input:dict):
    try:
        r = sfn.start_execution(
            stateMachineArn = SfnArn,
            input = json.dumps(Input)
        )
    except ClientError as e:
        print(f'ClientError\n{e}')
        raise
    else:
        return r['executionArn']
            
def lambda_handler(event, context):
    
    print(event)
    
    invoking_event = json.loads(event["invokingEvent"])
    print(f'invoking_event:\n{invoking_event}')
    
    rule_parameters = json.loads(event["ruleParameters"])
    print(f'rule_parameters:\n{rule_parameters}')
    
    configuration_item = invoking_event["configurationItem"]
    print(f'configuration_item:\n{configuration_item}')
    
    item_status = configuration_item["configurationItemStatus"]
    print(f'item_status:\n{item_status}')
    
    resource_type = configuration_item['resourceType']
    resource_configuration = configuration_item['configuration']
    print(f'resource_configuration:\n{resource_configuration}')
    
    # invoke sfn, pass event as input    
    
    # processed = sync_sfn(SfnArn=os.environ['ProcessingSfnArn'],Input=event)
    # print(f'processed:\n{processed}')
    # return bool(processed)
    
    # begun = async_sfn(SfnArn=os.environ['ProcessingSfnArn'],Input=event)
    # print(f'begun:\n{begun}')