import os
import json

import boto3
from botocore.exceptions import ClientError

ddb = boto3.client('dynamodb')
s3 = boto3.client('s3')

def put_object(*,S3Uri,Dict):
    
    def s3_uri_to_bucket_key(*,Uri):
        path_parts=Uri.replace("s3://","").split("/")
        bucket=path_parts.pop(0)
        key="/".join(path_parts)
        return bucket, key
        
    bucket, key = s3_uri_to_bucket_key(Uri=S3Uri)
    
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(Dict)
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print(f'no ClientError s3.put_object()\nS3Uri:\n{S3Uri}')
        return True

def simple_pk_query(*,
    Table,
    Pk,
    AllStringAttributes = True
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
        
        if AllStringAttributes:
            items = [{k:i[k]['S'] for k in i} for i in items]
        print(items)
        
        return items

def determine_compliance(*,InfractionItems,AllNestedSfnsSucceeded):
    no_infractions = not bool(InfractionItems)

    return no_infractions and AllNestedSfnsSucceeded

def determine_if_all_nested_sfns_succeeded(*,NestedSfns):
    return not bool([i for i in NestedSfns if i['InvokeInnerEvalEngineSfn']['Status']!='SUCCEEDED'])


def lambda_handler(event, context):
    
    print(event)
    
    invoking_sfn_for_each_input = event['ForEachInput']
    
    all_nested_sfns_succeeded = determine_if_all_nested_sfns_succeeded(NestedSfns=invoking_sfn_for_each_input)
    
    sfn_exec_id = event['OuterEvalEngineSfnExecutionId']
    
    print(f'sfn_exec_id:\n{sfn_exec_id}')
    
    eval_results_table = os.environ.get('EvalResultsTable')
    
    print(f'eval_results_table:\n{eval_results_table}')
    
    infraction_items = simple_pk_query(
        Table = eval_results_table,
        Pk = sfn_exec_id
    )
    
    compliance = determine_compliance(
        InfractionItems = infraction_items,
        AllNestedSfnsSucceeded = all_nested_sfns_succeeded
    )
    
    eval_results_report = {
        "ControlBrokerResultsReport": {
            "Metadata": {
                "Consumer": {
                    "To":"Do"
                },
                "ControlBroker":{
                    "EvalResultsTable":eval_results_table,
                    "OuterEvalEngineSfnExecutionId":sfn_exec_id
                }
            },
            "Evaluation": {
                "IsCompliant" : compliance,
                "InfractionItems" : infraction_items
            }
        }
    }
    
    print(f'eval_results_report:\n{eval_results_report}')
    
    put_object(
        S3Uri = event['ResultsReportS3Uri'],
        Dict = eval_results_report
    )
    
    return True