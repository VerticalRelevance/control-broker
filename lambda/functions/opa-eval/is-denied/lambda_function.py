import json
import boto3
from botocore.exceptions import ClientError
import os
import re
import pandas as pd

s3 = boto3.client('s3')

def s3_download(*,Bucket,Key,LocalPath):
    
    try:
        s3.download_file(
            Bucket,
            Key,
            LocalPath
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print('No ClientError download_file')
        return True

def normalize(Dict):
                    
    df = pd.json_normalize(Dict, sep='.')
    
    normalized = df.to_dict(orient='records')
    
    try:
        normalized = normalized[0]
    except KeyError:
        return Dict
    else:
        return normalized

def lambda_handler(event, context):
    
    print(f'event:\n{event}')
    
    template = event['CFN']
    print(f'template:\n{template}')
    resource_dict_key = list(template.keys())[0] # assume only one key in dict
    resource = template[resource_dict_key]
    resource_properties = resource['Properties']
    
    opa_package = os.environ.get('OPAPackage')
    print(f'opa_package:\n{opa_package}')
    
    opa_eval_result = event['OpaEvalPythonSubprocess']['OPAEvalResult']
    
    stdout = opa_eval_result['stdout']
    
    if 'error' in stdout:
        
        return {
            'StatusCode':2,
            'StatusMessage': 'OPAEvalResult contains "error"'
        }
    
    else:
        package_result = json.loads(stdout)[opa_package]
        
        if not package_result:
            
            return {
                'StatusCode':0,
                'StatusMessage': 'IsDenied == False'
            }
    
        
        else:
            denied_rules = list(package_result.keys())
            print(f'denied_rules:\n{denied_rules}')
            
            policy_path = '/tmp/policy.rego'
        
            key = f'{resource["Type"].replace("::","/")}.rego'
            print(f'key:\n{key}')
            
            s3_download(
                Bucket = os.environ['OPAPolicyS3Bucket'],
                Key = key,
                LocalPath = policy_path
            )
            
            with open(policy_path,'r') as f:
                policy = f.read()
                print(f'policy:\n{policy}')
            
            
            
            def find_rule (*,RuleName,Policy):
                m = re.search(f'^({RuleName}.*?^}})',Policy,re.DOTALL|re.MULTILINE)
                if m:
                    r = m.group(1)
                    r = r.split('\n')
                    r = [i.strip() for i in r]
                    r = [item for item in r if item and not item.startswith('#')]
                    r = '\n'.join(r)
                    print(r)
                    return r
            
            def rule_name_to_resource(RuleName):
                return RuleName.split('deny_if_condition_true_')[1].replace('_','.')
                    
            denied_resources = [rule_name_to_resource(denied_rule) for denied_rule in denied_rules]
            print(f'denied_resources:\n{denied_resources}')
            
            normalized_resource_properties = normalize(Dict=resource_properties)
            print(f'normalized_resource_properties:\n{normalized_resource_properties}')
            
            
            
            helpful_errors = [
                {
                    'DeniedRule': find_rule(RuleName=denied_rule,Policy=policy),
                    'OffendingResourcePropertyKey': rule_name_to_resource(denied_rule),
                    'OffendingResourcePropertyOffendingValue': normalized_resource_properties[rule_name_to_resource(denied_rule)],
                } for denied_rule in denied_rules
            ]
            
            # TODO: parse tracer to identify exact failure. compare expected value (from policy) to actual value (from template).
                
            return {
                'StatusCode':1,
                'StatusMessage': 'IsDenied == True',
                'HelpfulErrors': helpful_errors
            }