#!/usr/bin/env python3
import os
from pathlib import Path
from typing import List

import aws_cdk as cdk
from aws_cdk import aws_config

from stacks.control_broker_stack import (
    ControlBrokerStack,
)

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

application_team_cdk_app = {
    "PipelineOwnershipMetadata": "./supplementary_files/pipeline-ownership-metadata/business-unit-a/eval-engine-metadata.json",
}

control_broker_stack = ControlBrokerStack(
    app,
    "ControlBrokerEvalEngineCdkStackV5x0",
    application_team_cdk_app=application_team_cdk_app,
    config_rule_enabled=app.node.try_get_context("control-broker/config-rule/enabled"),
    config_rule_scope=aws_config.RuleScope.from_resources(
        resource_types=[aws_config.ResourceType.SQS_QUEUE]
    ),
    env=env,
)

app.synth()
