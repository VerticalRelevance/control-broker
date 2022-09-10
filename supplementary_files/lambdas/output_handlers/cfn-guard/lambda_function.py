import json
import boto3
from botocore.exceptions import ClientError

lambda_ = boto3.client('lambda')

def invoke_lambda_async(*, function_name:str=None, payload:typing.Mapping[str, str]=None):
    if function_name == None:
        raise Exception('ERROR: function_name parameter cannot be NULL')
    payloadStr = json.dumps(payload)
    payloadBytesArr = bytes(payloadStr, encoding='utf8')
    try:
        r=lambda_.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            Payload=payloadBytesArr
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print(r)
        return True

           
def lambda_handler(event, context):
    
    print(event)
    
    results=event.get('CfnGuardValidateResults')
    
    rules_compliant=[i['compliant'] for i in results if i['compliant']]
    print(f'rules_compliant:\n{rules_compliant}')
    
    rules_not_compliant=[i['not_compliant'] for i in results if i['not_compliant']]
    print(f'rules_not_compliant:\n{rules_not_compliant}')
    
    compliance_decision= not bool(rules_not_compliant)
    
    print(f'compliance_decision:\n{compliance_decision}')

    output= {
        "IsCompliant":compliance_decision,
        'InputToBeEvaluated':event['InputToBeEvaluated'],
        "InputType": event["InputType"]
    }
    
    invoke_lambda_async(
        function_name=os.environ['PutAssfLambda'],
        payload=output
    )
    
    return output