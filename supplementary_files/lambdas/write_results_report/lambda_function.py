import os
import json

import boto3
from botocore.exceptions import ClientError

ddb = boto3.client('dynamodb')
s3 = boto3.client('s3')

def put_object(*,s3_uri,dict_):
    
    def s3_uri_to_bucket_key(*,s3_uri):
        path_parts=s3_uri.replace("s3://","").split("/")
        bucket=path_parts.pop(0)
        key="/".join(path_parts)
        return bucket, key
        
    bucket, key = s3_uri_to_bucket_key(s3_uri=s3_uri)
    
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(dict_)
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print(f'no ClientError s3.put_object()\ns3_uri:\n{s3_uri}')
        return True

def simple_pk_query(*,
    table,
    pk,
    all_string_attributes = True
):
    try:
        r = ddb.query(
            TableName=table,
            ExpressionAttributeValues = {
                ":pk": {
                    "S": pk
                }
            },
            KeyConditionExpression="pk = :pk"
        )
    except ClientError as e:
        raise
    else:
        print(f'no ClientError ddb.query()\nTable:\n{table}\nPk:\n{pk}')
        print(r)
        items = r['Items']
        
        if all_string_attributes:
            items = [{k:i[k]['S'] for k in i} for i in items]
        print(items)
        
        return items

def determine_compliance(*,infraction_items,all_nested_sfns_succeeded):
    no_infractions = not bool(infraction_items)

    return no_infractions and all_nested_sfns_succeeded

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
        table = eval_results_table,
        pk = sfn_exec_id
    )
    
    compliance = determine_compliance(
        infraction_items = infraction_items,
        all_nested_sfns_succeeded = all_nested_sfns_succeeded
    )
    
    print(f'compliance:\n{compliance}')
    
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
        s3_uri = event['ResultsReportS3Uri'],
        dict_ = eval_results_report
    )
    
    return True