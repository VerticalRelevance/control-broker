import os
import json

import boto3
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb')
eb = boto3.client('events')

def update_item(*,
    Table,
    Pk,
    Sk,
    Attributes:list
):
    """
    Attributes: list of dicts
    [{Attribute1Name:Attribute1Value}]
    """
    def ddb_compatible_type(Item):
        if type(Item) == float:
            return str(Item)
        else:
            return Item
    
    table = ddb.Table(Table)
    
    expression_attribute_values = {}
    
    update_expressions = []
    
    for i,v in enumerate(Attributes):
        key = list(v.keys())[0]
        print(v[key])
        
        placeholder = f':{chr(97+i)}'
        expression_attribute_values[placeholder] = ddb_compatible_type(v[key])
        
        update_expressions.append(f'{key}={placeholder}')
        
    update_expression = ', '.join(update_expressions)
    update_expression = f'set {update_expression}'
    
    try:
        r = table.update_item(
            
            Key = {
                'pk':Pk,
                'sk':Sk
            },
            UpdateExpression = update_expression,
            ExpressionAttributeValues = expression_attribute_values
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        return False
    else:
        print(r)
        print(f'no ClientError: update_item')
        return True

def put_event_entry(*,
    EventBusName,
    Detail:dict
):
    try:
        r = eb.put_events(
            Entries = [
                {
                    'EventBusName':EventBusName,
                    'Detail':json.dumps(Detail)
                }
            ]
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        return False
    else:
        print(r)
        print(f'no ClientError: put_events')
        return True

def lambda_handler(event, context):
    
    print(event)
    
    infraction_key = list(event['Infraction'].keys())[0]
    
    pipeline_ownership_metadata = event.get('Metadata')
    
    inner_sfn_json_input = event.get('JsonInput')
    
    template_key = inner_sfn_json_input['Key']
    
    sk = f'{template_key}#{infraction_key}'
    
    # to ddb
    
    update = update_item(
        Table = os.environ['TableName'],
        Pk = event['OuterEvalEngineSfnExecutionId'],
        Sk = sk,
        Attributes = [
            {'BusinessUnit':pipeline_ownership_metadata.get('BusinessUnit')},
            {'BillingCode':pipeline_ownership_metadata.get('BillingCode')},
            {'TargetProvisioningEnvironment':pipeline_ownership_metadata.get('TargetProvisioningEnvironment')},
            {'PipelineOwnerName':pipeline_ownership_metadata.get('PipelineOwner').get('Name')},
            {'PipelineOwnerEmail':pipeline_ownership_metadata.get('PipelineOwner').get('Email')},
        ]
    )
    
    # to eb
    
    put = put_event_entry(
        EventBusName = os.environ.get('EventBusName'),
        Detail = {
            'Infraction':event.get('Infraction'),
            'PipelineOwnershipMetadata':pipeline_ownership_metadata,
            'OuterEvalEngineSfnExecutionId':event.get('OuterEvalEngineSfnExecutionId')
        }
    )
    
    return update and put
