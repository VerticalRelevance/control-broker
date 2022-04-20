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
        return True

def lambda_handler(event, context):
    
    print(event)
    
    event_bus_name = os.environ.get('EventBusName')
    
    infraction_key = list(event['Infraction'].keys())[0]
    
    # to ddb
    
    update_item(
        Table = os.environ.get('TableName'),
        Pk = event['OuterEvalEngineSfnExecutionId'],
        Sk = infraction_key,
        Attributes = [
            {'Metadata':'someMetadata'},
            {'OuterEvalEngineSfnExecutionId':event['OuterEvalEngineSfnExecutionId']}
        ]
    )
    
    # to eb
    
    put_event_entry(
        EventBusName = os.environ.get('EventBusName'),
        Detail = {
            'Infraction':event['Infraction'],
            'Metadata':'someMetadata',
            'OuterEvalEngineSfnExecutionId':event['OuterEvalEngineSfnExecutionId']
        }
    )
