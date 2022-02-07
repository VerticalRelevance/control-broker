import json
import re

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def s3_get(*,Bucket,Key):
    
    try:
        r = s3.get_object(
            Bucket=Bucket,
            Key=Key,
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print('No ClientError download_file')
        return r['Body'].read().decode('utf-8')

def lambda_handler(event, context):
    
    print(event)
    
    cfn = s3_get(
        Bucket = event['Bucket'],
        Key = event['Key'],
    )
    
    resources = json.loads(cfn)['Resources']
    
    ignored_resource_types = ['AWS::CDK::Metadata']
    
    resource_types = [resources[i]['Type'] for i in resources if resources[i]['Type'] not in ignored_resource_types]
    
    resource_types = list(set(resource_types))
    
    standard_services = list(set([i.split('::')[1] for i in resource_types if i.startswith('AWS')]))
    
    def service_from_custom_cfn(CustomCfn):
        m = re.search('Custom::AWSCDK-(.*)-.*',CustomCfn)
        return m.group(1)
    
    custom_services = list(set([service_from_custom_cfn(i) for i in resource_types if i.startswith('Custom')]))
    
    active_services = list(set(standard_services + custom_services))
    
    active_services = [i.lower() for i in active_services]
    
    print(f'active_services:\n{active_services}')
    
    return {
        'ActiveServices': active_services
    }
    
    