import json, os, random
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

config = boto3.client("config")

class ConfigCompliance:
    def __init__(self, *, ResourceType, ResourceId, ResultToken, Compliant):

        self.resource_type = ResourceType
        self.resource_id = ResourceId
        self.result_token = ResultToken
        self.compliant = Compliant

    def evaluate_compliant(self):
        print(
            f"begin put_evaluations COMPLIANT\n{self.resource_type}\n{self.resource_id}"
        )
        try:
            r = config.put_evaluations(
                Evaluations=[
                    {
                        "ComplianceResourceType": self.resource_type,
                        "ComplianceResourceId": self.resource_id,
                        "ComplianceType": "COMPLIANT",
                        # 'Annotation': 'string', #TODO add useful metadata
                        "OrderingTimestamp": datetime(2015, 1, 1),  # FIXME
                    },
                ],
                ResultToken=self.result_token,
            )
        except ClientError as e:
            print(f"ClientError\n{e}")
            raise
        else:
            return True

    def evaluate_noncompliant(self):
        print(
            f"begin put_evaluations NON_COMPLIANT\n{self.resource_type}\n{self.resource_id}"
        )
        try:
            r = config.put_evaluations(
                Evaluations=[
                    {
                        "ComplianceResourceType": self.resource_type,
                        "ComplianceResourceId": self.resource_id,
                        "ComplianceType": "NON_COMPLIANT",
                        # 'Annotation': 'string',
                        "OrderingTimestamp": datetime(2015, 1, 1),  # FIXME
                    },
                ],
                ResultToken=self.result_token,
            )
        except ClientError as e:
            print(f"ClientError\n{e}")
            raise
        else:
            return True

    def put_compliant_status(self):
        if self.compliant:
            evaluation_completion_status = self.evaluate_compliant()
        else:
            evaluation_completion_status= self.evaluate_noncompliant()
        
        return evaluation_completion_status

def lambda_handler(event, context):
    
    print(event)
    
    invoking_event = json.loads(event["invokingEvent"])
    print(f"invoking_event:\n{invoking_event}")
    
    configuration_item = invoking_event["configurationItem"]
    print(f"configuration_item:\n{configuration_item}")

    item_status = configuration_item["configurationItemStatus"]
    print(f"item_status:\n{item_status}")
    
    if item_status == 'ResourceDeleted':
        return True

    resource_type = configuration_item["resourceType"]
    print(f"resource_type:\n{resource_type}")

    resource_configuration = configuration_item["configuration"]
    print(f"resource_configuration:\n{resource_configuration}")

    resource_id = configuration_item["resourceId"]
    print(f"resource_id:\n{resource_id}")

    result_token = event["resultToken"]
    print(f"result_token:\n{result_token}")
    
    config_rule_name = event["configRuleName"]
    print(f"config_rule_name:\n{config_rule_name}")


    # dev

    c = ConfigCompliance(
        ResourceType=resource_type,
        ResourceId=resource_id,
        ResultToken=result_token,
        Compliant=bool(random.getrandbits(1)), #DEV
    )
    
    evaluation_completion_status = c.put_compliant_status()
    print(f"evaluation_completion_status\n{evaluation_completion_status}")
    
    return {
        "EvaluationCompletionStatus": evaluation_completion_status
    }