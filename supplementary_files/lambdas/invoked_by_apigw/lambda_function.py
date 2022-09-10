import json, os, typing

import boto3

from botocore.exceptions import ClientError

lambda_ = boto3.client('lambda')

def invoke_lambda(*, function_name:str=None, payload:typing.Mapping[str, str]=None):
    if function_name == None:
        raise Exception('ERROR: function_name parameter cannot be NULL')
    payloadStr = json.dumps(payload)
    payloadBytesArr = bytes(payloadStr, encoding='utf8')
    try:
        r=lambda_.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=payloadBytesArr
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        output=r["Payload"].read()

def lambda_handler(event, context):

    print(event)
    
    body=json.loads(event['body'])
    
    eval_engine_input =  {
        "InputToBeEvaluated": body,
        "ConsumerMetadata": None, 
        "Context": None,
        "InputType": "ConfigEvent",
        "ResponseExpectedByConsumer": None
    }
    
    invoke_lambda(
        function_name=os.environ['EvalEngineLambda'],
        paload=eval_engine_input
    )

    