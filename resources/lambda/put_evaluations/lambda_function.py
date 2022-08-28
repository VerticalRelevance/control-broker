import json
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime

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
    
    c = ConfigCompliance(
        ResourceType=event['ResourceType'],
        ResourceId=event['ResourceId'],
        ResultToken=event['ConfigResultToken'],
        Compliant=event['Compliance'],
    )
    
    evaluation_completion_status = c.put_compliant_status()
    print(f"evaluation_completion_status\n{evaluation_completion_status}")
    
    return {
        "EvaluationCompletionStatus": evaluation_completion_status
    }