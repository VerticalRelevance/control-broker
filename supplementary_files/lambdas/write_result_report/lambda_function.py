import os
import json

import boto3
from botocore.exceptions import ClientError

ddb = boto3.client('dynamodb')

def simple_pk_query(*,
    Table,
    Pk,
):
    try:
        r = ddb.query(
            TableName=Table,
            ExpressionAttributeValues = {
                ":pk": {
                    "S": Pk
                }
            },
            KeyConditionExpression="pk = :pk"
        )
    except ClientError as e:
        raise
    else:
        print(f'no ClientError ddb.query()\nTable:\n{Table}\nPk:\n{Pk}')
        print(r)
        items = r['Items']
        print(items)
        return items

def lambda_handler(event, context):
    
    print(event)
    
    sfn_exec_id = event['OuterEvalEngineSfnExecutionId']
    
    print(f'sfn_exec_id:\n{sfn_exec_id}')
    
    eval_results_table = os.environ.get('EvalResultsTable')
    
    print(f'eval_results_table:\n{eval_results_table}')
    
    items = simple_pk_query(
        Table = eval_results_table,
        Pk = sfn_exec_id
    )
    
    return True