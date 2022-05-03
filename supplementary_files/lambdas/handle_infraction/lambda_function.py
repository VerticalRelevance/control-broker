import os
import json

import boto3
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb')
eb = boto3.client('events')

def update_item(*,
    table,
    pk,
    sk,
    attributes:dict[str,str]
):
    
    def ddb_compatible_type(Item):
        if type(Item) == float:
            return str(Item)
        else:
            return Item
    
    table = ddb.Table(table)
    
    expression_attribute_values = {}
    
    update_expressions = []
    
    for index, (key, value) in enumerate(attributes.items()):

        placeholder = f':{chr(97+index)}'

        expression_attribute_values[placeholder] = ddb_compatible_type(value)

        update_expressions.append(f'{key}={placeholder}')
        
    update_expression = ', '.join(update_expressions)
    
    update_expression = f'set {update_expression}'
    
    try:
        r = table.update_item(
            Key = {
                'pk':pk,
                'sk':sk
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
    event_bus_name,
    source,
    detail:dict
):
    try:
        r = eb.put_events(
            Entries = [
                {
                    'EventBusName':event_bus_name,
                    'Detail':json.dumps(detail),
                    'DetailType':os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
                    'source':source,
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
    
    outer_eval_enginge_sfn_execution_id = event['OuterEvalEngineSfnExecutionId']
    
    infraction_key = list(event['Infraction'].keys())[0]
    
    consumer_metadata = event.get('ConsumerMetadata')
    
    inner_sfn_json_input = event.get('JsonInput')
    
    template_key = inner_sfn_json_input['Key']
    
    sk = f'{template_key}#{infraction_key}'
    
    # to ddb
    
    update = update_item(
        table = os.environ['TableName'],
        pk = outer_eval_enginge_sfn_execution_id,
        sk = sk,
        attributes = consumer_metadata
    )
    
    # to eb
    
    put = put_event_entry(
        event_bus_name = os.environ['EventBusName'],
        source = outer_eval_enginge_sfn_execution_id,
        detail = {
            'Infraction':event.get('Infraction'),
            'ConsumerMetadata':consumer_metadata,
            'OuterEvalEngineSfnExecutionId':event.get('OuterEvalEngineSfnExecutionId')
        }
    )
    
    return update and put
