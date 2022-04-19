import json
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime

sfn = boto3.client("stepfunctions")
config = boto3.client("config")


def sync_sfn(*, SfnArn, Input: dict):
    try:
        r = sfn.start_sync_execution(stateMachineArn=SfnArn, input=json.dumps(Input))
    except ClientError as e:
        print(f"ClientError\n{e}")
        raise
    else:
        print(r)
        if r["status"] != "SUCCEEDED":
            print(f"ProcessingSfn Status not SUCCEEDED")
            return False
        else:
            output = r["output"]
            print(f"output:\n{output}\n{type(output)}")
            return output


def async_sfn(*, SfnArn, Input: dict):
    try:
        r = sfn.start_execution(stateMachineArn=SfnArn, input=json.dumps(Input))
    except ClientError as e:
        print(f"ClientError\n{e}")
        raise
    else:
        return r["executionArn"]


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

    def main(self):
        if self.compliant:
            self.evaluate_compliant()
        else:
            self.evaluate_noncompliant()


def lambda_handler(event, context):

    print(event)

    invoking_event = json.loads(event["invokingEvent"])
    print(f"invoking_event:\n{invoking_event}")

    rule_parameters = event.get("ruleParameters")
    if rule_parameters:
        rule_parameters = json.loads(rule_parameters)
        print(f"rule_parameters:\n{rule_parameters}")

    configuration_item = invoking_event["configurationItem"]
    print(f"configuration_item:\n{configuration_item}")

    item_status = configuration_item["configurationItemStatus"]
    print(f"item_status:\n{item_status}")

    resource_type = configuration_item["resourceType"]
    print(f"resource_type:\n{resource_type}")

    resource_configuration = configuration_item["configuration"]
    print(f"resource_configuration:\n{resource_configuration}")

    resource_id = configuration_item["resourceId"]
    print(f"resource_id:\n{resource_id}")

    result_token = event["resultToken"]
    print(f"result_token:\n{result_token}")

    processed = sync_sfn(SfnArn=os.environ["ProcessingSfnArn"], Input={"Config": event})
    print(f"processed:\n{processed}")

    # return to Config compliance status - let Config notify

    c = ConfigCompliance(
        ResourceType=resource_type,
        ResourceId=resource_id,
        ResultToken=result_token,
        Compliant=bool(processed),
    )
    c.main()
