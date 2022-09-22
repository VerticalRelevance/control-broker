import json, os, datetime, time, re

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config



boto3_config = Config(
    region_name = 'us-east-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)


sh = boto3.client(
    'securityhub',
    config=boto3_config
)

lambda_aws_account_id=boto3.client('sts').get_caller_identity().get('Account')


class ControlBrokerASFF():
    
    def __init__(self,*,
        resource_aws_account_id,
        resource_type,
        resource_id,
        region,
        is_compliant,
        rule
    ):
        
        now=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        finding_id=f'{resource_aws_account_id}/{resource_type}/{resource_id}/{rule}'
        
        finding_type="ControlBroker/CfnGuard"
        
        mapping={
            'Severity':{
                'is_compliant':{
                    True:'INFORMATIONAL',
                    False:'MEDIUM',
                }
                    
            },
            'Compliance':{
                'Status':{
                    'is_compliant':{
                        True:'PASSED',
                        False:'FAILED',
                    }
                }
            }
        }
        
        self.findings=[
           {
            	"AwsAccountId": lambda_aws_account_id,
            # 	"AwsAccountId": resource_aws_account_id,
            	"Compliance": {
            # 		"RelatedRequirements": ["string"],
            		"Status": mapping['Compliance']['Status']['is_compliant'][is_compliant],
            # 		"StatusReasons": [{
            # 			"Description": "string",
            # 			"ReasonCode": "string"
            # 		}]
            	},
            	"CreatedAt": now,
            	"Description": finding_type,
            	"GeneratorId": finding_id,
            	"Id": finding_id,
            	"ProductArn": self.get_security_hub_product_arn(
            	    region=region
            	 ),
            	"Resources": [{
            # 		"Details": {
            # 		},
            # 		"Other": {
            # 			"string": "string"
            # 		},
            		"Id": resource_id,
            # 		"Partition": "string",
            		"Region": region,
            # 		"ResourceRole": "string",
            # 		"Tags": {
            # 			"string": "string"
            # 		},
            		"Type": resource_type
            	}],
        		"Region": region,
                "SchemaVersion": "2018-10-08",
                "Severity": {
            		"Label": mapping['Severity']['is_compliant'][is_compliant],
            # 		"Normalized": "number",
            # 		"Original": "string",
            # 		"Product": "number"
            	},
            	"Title": finding_id,
            	"Types": [
            	    finding_type
            	 ],
            	"UpdatedAt": now,
            } 
            
        ]
        
        print(self.findings)

    def re_search(self,regex,item):
        
        m = re.search(regex,item)
        try:
            return m.group(1)
        except AttributeError:
            return None

    def get_security_hub_product_arn(self,region):
        
        product_arn= f'arn:aws:securityhub:{region}:{lambda_aws_account_id}:product/{lambda_aws_account_id}/default'
        
        print(f'product_arn:\n{product_arn}')
        
        return product_arn
        
    def put_asff(self):
        try:
            r = sh.batch_import_findings(
                Findings=self.findings
            )
        except ClientError as e:
            print(f'ClientError:\n{e}')
            raise
        else:
            print(r)
            return r
            
    def main(self):
        
        self.put_asff()
        
        
def lambda_handler(event, context):
    
    print(event)
    
    if event["InputType"]=='ConfigEvent':
        configuration_item=event['InputToBeEvaluated']['configurationItem']
        resource_aws_account_id=configuration_item['awsAccountId']
        resource_region=configuration_item['awsRegion']
        resource_type=configuration_item['resourceType']
        resource_id=configuration_item['resourceId']
    
    rules_not_compliant=event['RulesNotCompliant']
    
    rules_compliant=event['RulesCompliant']
        
    for rule in rules_not_compliant:
        c=ControlBrokerASFF(
            resource_aws_account_id=resource_aws_account_id,
            region=resource_region,
            resource_type=resource_type,
            resource_id=resource_id,
            is_compliant=False,
            rule=rule
        )
        c.main()
    
    for rule in rules_compliant:
        c=ControlBrokerASFF(
            resource_aws_account_id=resource_aws_account_id,
            region=resource_region,
            resource_type=resource_type,
            resource_id=resource_id,
            is_compliant=True,
            rule=rule

        )
        c.main()