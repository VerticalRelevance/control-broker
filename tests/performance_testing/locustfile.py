import time
import json
from typing import Collection, List
import boto3
from locust import User, task, constant, events


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "S3_BUCKET", type=str, help="S3 Bucket to store test CFN templates in"
    )
    parser.add_argument(
        "CFN_TEMPLATE_PATH",
        type=str,
        help="Local path to JSON template to use as input data",
    )
    parser.add_argument(
        "SFN_ARN", type=str, help="ARN of the state machine to invoke during tests"
    )


class BotoClient:
    def __init__(self):
        self.s3_client = boto3.client("s3")
        self.stepfunctions_client = boto3.client("stepfunctions")

    def send(self, sfn_arn, input_bucket: str, input_keys: List[str]):

        request_meta = {
            "request_type": "Invoke Control Broker",
            "name": "ControlBroker",
            "start_time": time.time(),
            "response_length": 0,
            "response": None,
            "context": {},
            "exception": None,
        }
        start_perf_counter = time.perf_counter()

        try:
            response = self.stepfunctions_client.start_sync_execution(
                stateMachineArn=sfn_arn,
                input=json.dumps({"CFN": {"Bucket": input_bucket, "Keys": input_keys}}),
            )
            
        except Exception as e:
            request_meta["exception"] = e

        request_meta["response_time"] = (
            time.perf_counter() - start_perf_counter
        ) * 1000

        events.request.fire(**request_meta)


class BotoUser(User):
    abstract = True

    def __init__(self, env):
        super().__init__(env)
        self.client = BotoClient()

    wait_time = constant(1)


class ControlBrokerUser(BotoUser):

    wait_time = constant(1)

    def __init__(self, env):
        super().__init__(env)
        self.cfn_template_bucket = self.environment.parsed_options.S3_BUCKET
        self.sfn_arn = self.environment.parsed_options.SFN_ARN
        self.local_cfn_path = self.environment.parsed_options.CFN_TEMPLATE_PATH
        self.cfn_template_key = "performance_testing_example_cfn_template.json"
        self.client.s3_client.upload_file(
            self.local_cfn_path,
            self.cfn_template_bucket,
            self.cfn_template_key,
        )

    @task
    def send_request(self):
        self.client.send(
            self.sfn_arn, self.cfn_template_bucket, [self.cfn_template_key]
        )
