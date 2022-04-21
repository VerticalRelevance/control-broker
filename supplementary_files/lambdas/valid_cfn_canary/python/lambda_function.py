import json
import logging
from os import environ, path
from pathlib import Path
from uuid import uuid4

import boto3

logging.basicConfig()
logger = logging.getLogger()
logger.root.setLevel(logging.DEBUG)

SCRIPT_DIR = Path(__file__).parent


def lambda_handler(event=None, context=None):
    control_broker_readable_input_bucket = environ[
        "CONTROL_BROKER_READABLE_INPUT_BUCKET"
    ]
    control_broker_input_prefix = environ["CONTROL_BROKER_INPUT_PREFIX"]
    control_broker_outer_state_machine_arn = environ[
        "CONTROL_BROKER_OUTER_STATE_MACHINE_ARN"
    ]
    sfn = boto3.client("stepfunctions")
    s3 = boto3.client("s3")
    test_file_s3_key = f"automated-test-files/valid_cfn-{uuid4()}.template.json"
    s3.upload_file(
        str(SCRIPT_DIR / "valid_cfn.template.json"),
        control_broker_readable_input_bucket,
        path.join(control_broker_input_prefix, test_file_s3_key),
    )
    control_broker_input_object = json.dumps(
        {
            "CFN": {
                "Bucket": control_broker_readable_input_bucket,
                "Keys": [test_file_s3_key],
            }
        }
    )
    state_machine_result = sfn.start_sync_execution(
        stateMachineArn=control_broker_outer_state_machine_arn,
        input=control_broker_input_object,
    )
    logger.debug("Full result: %s", state_machine_result)

    if state_machine_result["status"] in ["FAILED", "TIMED_OUT"]:
        raise Exception("Sync start failed")

    outer_sfn_exec_id = state_machine_result["executionArn"]
    output = json.loads(state_machine_result["output"])
    nested_results = output["ForEachTemplate"]
    results = [
        {
            "Status": i.get("TemplateToNestedSFN").get("Status"),
            "Cause": i.get("TemplateToNestedSFN").get("Cause"),
            "EvalResultsTablePk": f"{outer_sfn_exec_id}#{i.get('TemplateToNestedSFN').get('ExecutionArn')}",
        }
        for i in nested_results
    ]
    logger.debug("Parsed results: %s", results)
    assert all(
        i["Status"] == "SUCCEEDED" for i in results
    ), "A valid template had infractions"
