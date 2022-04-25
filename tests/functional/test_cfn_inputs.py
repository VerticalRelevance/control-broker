import boto3
import json
import logging
from pathlib import Path

import plastic_yellow_bird as pyb
import pytest

logging.basicConfig()
logger = logging.getLogger()

from app import app
from stacks.control_broker_stack import ControlBrokerStack


@pytest.fixture
def outer_state_machine_arn(stack: ControlBrokerStack):
    return stack.sfn_outer_eval_engine.attr_arn


@pytest.fixture
def valid_template_json():
    return (
        Path(__file__).parent / "supplementary_files/valid_template.json"
    ).read_text()


@pyb.test
def test_valid_cfn_template_passes_control_broker_evaluation(
    outer_state_machine_arn, valid_template_json
):
    sfn = boto3.client("stepfunctions")
    r = sfn.start_sync_execution(
        stateMachineArn=outer_state_machine_arn,
        input=json.dumps({"CFN": [valid_template_json]}),
    )
    logger.debug("Full result: %s", r)

    if r["status"] in ["FAILED", "TIMED_OUT"]:
        raise Exception("Sync start failed")

    outer_sfn_exec_id = r["executionArn"]
    output = json.loads(r["output"])
    nested_results = output["ForEachTemplate"]
    results = [
        {
            "Status": i.get("TemplateToNestedSFN").get("Status"),
            "Cause": i.get("TemplateToNestedSFN").get("Cause"),
            "EvalResultsTablePk": outer_sfn_exec_id,
        }
        for i in nested_results
    ]
    logger.debug("Parsed results: %s", results)

    assert all(
        i["Status"] == "SUCCEEDED" for i in results
    ), "A valid template had infractions"
