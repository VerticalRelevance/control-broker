import json, os, datetime, time

import boto3
from botocore.exceptions import ClientError

sh = boto3.client('securityhub')


class ControlBrokerASFF():
    
    def __init__(self,*,
        resource_aws_id,
        resource_type,
        resource_id,
        is_compliant,
    ):
        
        now=datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        useful_root=f'ControlBroker-IsCompliant-{is_compliant}'
        
        finding_type="ControlBroker/CfnGuard/expected_schema_config_event_invoking_event"
        
        finding_id=f'{useful_root}/{now}'
        
        mapping={
            'Severity':{
                'is_compliant':{
                    True:'INFORMATIONAL',
                    False:'MEDIUM',
                }
                    
            }
        }
        
        self.findings=[
           {
            	"AwsAccountId": resource_aws_id,
            	"Compliance": {
            # 		"RelatedRequirements": ["string"],
            		"Status": is_compliant,
            # 		"StatusReasons": [{
            # 			"Description": "string",
            # 			"ReasonCode": "string"
            # 		}]
            	},
            	"CreatedAt": now,
            	"Description": useful_root,
            	"GeneratorId": finding_id,
            	"Id": finding_id,
            	"ProductArn": "string",
            	"Resources": [{
            # 		"DataClassification": {
            # 			"DetailedResultsLocation": "string",
            # 			"Result": {
            # 				"AdditionalOccurrences": "boolean",
            # 				"CustomDataIdentifiers": {
            # 					"Detections": [{
            # 						"Arn": "string",
            # 						"Count": "integer",
            # 						"Name": "string",
            # 						"Occurrences": {
            # 							"Cells": [{
            # 								"CellReference": "string",
            # 								"Column": "integer",
            # 								"ColumnName": "string",
            # 								"Row": "integer"
            # 							}],
            # 							"LineRanges": [{
            # 								"End": "integer",
            # 								"Start": "integer",
            # 								"StartColumn": "integer"
            # 							}],
            # 							"OffsetRanges": [{
            # 								"End": "integer",
            # 								"Start": "integer",
            # 								"StartColumn": "integer"
            # 							}],
            # 							"Pages": [{
            # 								"LineRange": {
            # 									"End": "integer",
            # 									"Start": "integer",
            # 									"StartColumn": "integer"
            # 								},
            # 								"OffsetRange": {
            # 									"End": "integer",
            # 									"Start": "integer",
            # 									"StartColumn": "integer"
            # 								},
            # 								"PageNumber": "integer"
            # 							}],
            # 							"Records": [{
            # 								"JsonPath": "string",
            # 								"RecordIndex": "integer"
            # 							}]
            # 						}
            # 					}],
            # 					"TotalCount": "integer"
            # 				},
            # 				"MimeType": "string",
            # 				"SensitiveData": [{
            # 					"Category": "string",
            # 					"Detections": [{
            # 						"Count": "integer",
            # 						"Occurrences": {
            # 							"Cells": [{
            # 								"CellReference": "string",
            # 								"Column": "integer",
            # 								"ColumnName": "string",
            # 								"Row": "integer"
            # 							}],
            # 							"LineRanges": [{
            # 								"End": "integer",
            # 								"Start": "integer",
            # 								"StartColumn": "integer"
            # 							}],
            # 							"OffsetRanges": [{
            # 								"End": "integer",
            # 								"Start": "integer",
            # 								"StartColumn": "integer"
            # 							}],
            # 							"Pages": [{
            # 								"LineRange": {
            # 									"End": "integer",
            # 									"Start": "integer",
            # 									"StartColumn": "integer"
            # 								},
            # 								"OffsetRange": {
            # 									"End": "integer",
            # 									"Start": "integer",
            # 									"StartColumn": "integer"
            # 								},
            # 								"PageNumber": "integer"
            # 							}],
            # 							"Records": [{
            # 								"JsonPath": "string",
            # 								"RecordIndex": "integer"
            # 							}]
            # 						},
            # 						"Type": "string"
            # 					}],
            # 					"TotalCount": "integer"
            # 				}],
            # 				"SizeClassified": "integer",
            # 				"Status": {
            # 					"Code": "string",
            # 					"Reason": "string"
            # 				}
            # 			}
            # 		},
            # 		"Details": {
            # 		},
            # 		"Other": {
            # 			"string": "string"
            # 		},
            		"Id": resource_id,
            # 		"Partition": "string",
            # 		"Region": "string",
            # 		"ResourceRole": "string",
            # 		"Tags": {
            # 			"string": "string"
            # 		},
            		"Type": resource_type
            	}],
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
        resource_type=event['ResourceType'],
        resource_id=event['ResourceId'],
        is_compliant=event['IsCompliant']
    )
    c.main()