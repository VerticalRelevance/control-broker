#!/usr/bin/env python3
import os
from pathlib import Path
from typing import List

import aws_cdk as cdk
from aws_cdk import aws_config, aws_stepfunctions

from stacks.control_broker_stack import (
    ControlBrokerStack,
)
from stacks.pipeline_stack import GitHubCDKPipelineStack
from stacks.test_stack import TestStack
from stacks.client_stack import ClientStack

STACK_VERSION = "V6x0"

app = cdk.App()
continuously_deployed = app.node.try_get_context(
    "control-broker/continuous-deployment/enabled"
)
deploy_stage = None
if continuously_deployed:
    deploy_stage = cdk.Stage(app, "Deploy")

# TODO: DEPRECATED - define team metadata storage strategy
application_team_cdk_app = {
    "PipelineOwnershipMetadata": "./supplementary_files/pipeline-ownership-metadata/business-unit-a/eval-engine-metadata.json",
}

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

control_broker_stack = ControlBrokerStack(
    deploy_stage or app,
    f"ControlBrokerEvalEngineCdkStack{STACK_VERSION}",
    env=env,
    application_team_cdk_app=application_team_cdk_app,
    config_rule_enabled=app.node.try_get_context("control-broker/config-rule/enabled"),
    config_rule_scope=aws_config.RuleScope.from_resources(
        resource_types=[aws_config.ResourceType.SQS_QUEUE]
    ),
)

if app.node.try_get_context("control-broker/post-deployment-testing/enabled"):
    TestStack(
        deploy_stage or app,
        f"ControlBrokerTestStack{STACK_VERSION}",
        control_broker_outer_state_machine=control_broker_stack.outer_eval_engine_state_machine,
        control_broker_roles=control_broker_stack.template_reader_roles,
        env=env
    )
if app.node.try_get_context("control-broker/client/enabled"):
    ClientStack(
        deploy_stage or app,
        f"ControlBrokerClientStack{STACK_VERSION}",
        control_broker_outer_state_machine=control_broker_stack.outer_eval_engine_state_machine,
        control_broker_roles=control_broker_stack.template_reader_roles,
        control_broker_eval_results_bucket=control_broker_stack.eval_results_reports_bucket,
        env=env
    )

if continuously_deployed:
    pipeline_stack = GitHubCDKPipelineStack(
        app,
        "ControlBrokerCICDDeployment",
        env=env,
        **app.node.try_get_context(
            "control-broker/continuous-deployment/github-config"
        ),
    )
    pipeline_stack.pipeline.add_stage(deploy_stage)
app.synth()
