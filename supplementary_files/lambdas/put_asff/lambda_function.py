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
        resource_aws_id,
        resource_type,
        resource_id,
        region,
        is_compliant,
    ):
        
        now=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        useful_root=f'ControlBroker-IsCompliant-{is_compliant}'
        
        finding_type="ControlBroker/CfnGuard/expected_schema_config_event_invoking_event"
        
        finding_id=f'{useful_root}/{now}'
        
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
            # 	"AwsAccountId": resource_aws_id,
            	"Compliance": {
            # 		"RelatedRequirements": ["string"],
            		"Status": mapping['Compliance']['Status']['is_compliant'][is_compliant],
            # 		"StatusReasons": [{
            # 			"Description": "string",
            # 			"ReasonCode": "string"
            # 		}]
            	},
            	"CreatedAt": now,
            	"Description": useful_root,
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
            	"Title": useful_root,
            	"Types": [
            	    finding_type
            	 ],
            	"UpdatedAt": now,
            } 
            
        ] 

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
        
    def get_resource_arn(self,*,
        resource_aws_id,
        resource_type,
        resource_id,
        region,
        partition='aws'
    ):
        
        def resource_type_to_service(resource_type):
            print(resource_type)
            
            return self.re_search('AWS::(\w+?)::\w+',resource_type).lower()
        
        def service_to_arn_region_section(service,region):
            
            global_services=[
                "iam",
                "route53",
                "s3",
                "sts",
                "waf",
            ]
            
            if service in global_services:
                return ""
                
            else:
                return region
        
        def service_to_arn_account_section(service,account_id):
            
            global_services=[
                "iam",
                "route53",
                "s3",
                "sts",
                "waf",
            ]
            
            if service in global_services:
                return ""
                
            else:
                return f"{account_id}"
                
        def resource_type_to_arn_suffix_prefix(resource_type):
            
            no_prefix=[
                'AWS::SQS::Queue',
                'AWS::S3::Bucket',
            ]
            
            prefix_is_lowercase_of_type=[
                'AWS::EC2::Instance'
            ]
            
            custom_prefixes={
                'AWS::RDS::DBInstance':'db:'
            }
            
            if resource_type in no_prefix:
                return ''
                
            elif resource_type in prefix_is_lowercase_of_type:
                return f'{resource_type.lower()}/'
            
            else:
                try:
                    return f'{custom_prefixes[resource_type]}/'
                except KeyError:
                    raise
         
        def resource_id_to_arn_suffix_suffix(resource_type,resource_id):
            
            print(resource_type)
            
            resource_type_to_regex={
                'AWS::SQS::Queue':'https://sqs\..+?\.amazonaws.com/\d{12}/(.+)'
            }
        
            try:
                regex=resource_type_to_regex[resource_type]
            except KeyError:
                return resource_id
            else:
                resource_id= self.re_search(
                    regex,
                    resource_id
                )
                
                print(f'\n\n{resource_id}\n\n')
                
                return resource_id
        
        service=resource_type_to_service(resource_type)
   
        arn_items=[
            'arn',
            partition,
            service,
            service_to_arn_region_section(service,region),
            service_to_arn_account_section(service,resource_aws_id),
            f'{resource_type_to_arn_suffix_prefix(resource_type)}{resource_id_to_arn_suffix_suffix(resource_type,resource_id)}'
        ]
        
        print(arn_items)
            
        arn=':'.join(arn_items)
        
        print(arn)
        
        return arn
            
    
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
    
    c=ControlBrokerASFF(
        resource_aws_id=event['ResourceAwsId'],
        region=event['Region'],
        resource_type=event['ResourceType'],
        resource_id=event['ResourceId'],
        is_compliant=event['IsCompliant']
    )
    c.main()