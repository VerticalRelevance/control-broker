#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.control_broker_stack import (
    ControlBrokerStack,
)
from stacks.pipeline_stack import GitHubCDKPipelineStack
from stacks.test_stack import TestStack
from stacks.endpoint_stack import EndpointStack
from utils.environment import is_pipeline_synth

STACK_VERSION = "V0x7x0"

app = cdk.App()
continuously_deployed = (
    app.node.try_get_context("control-broker/continuous-deployment/enabled")
    or is_pipeline_synth()
)
deploy_stage = None
if continuously_deployed:
    deploy_stage = cdk.Stage(app, "Deploy")

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

control_broker_stack = ControlBrokerStack(
    deploy_stage or app,
    f"ControlBrokerEvalEngineCdkStack{STACK_VERSION}",
    env=env,
)

if app.node.try_get_context("control-broker/post-deployment-testing/enabled"):
    TestStack(
        deploy_stage or app,
        f"ControlBrokerTestStack{STACK_VERSION}",
        control_broker_outer_state_machine=control_broker_stack.outer_eval_engine_state_machine,
        control_broker_roles=control_broker_stack.Input_reader_roles,
        env=env,
    )
if app.node.try_get_context("control-broker/client/enabled"):
    EndpointStack(
        deploy_stage or app,
        f"ControlBrokerEndpointStack{STACK_VERSION}",
        control_broker_outer_state_machine=control_broker_stack.outer_eval_engine_state_machine,
        control_broker_roles=control_broker_stack.Input_reader_roles,
        control_broker_eval_results_bucket=control_broker_stack.eval_results_reports_bucket,
        env=env,
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
