#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.control_broker_stack import ControlBrokerStack
from stacks.pipeline_stack import GitHubCDKPipelineStack

from git import Repo

from utils.environment import is_pipeline_synth

STACK_VERSION = "V0x10x0"

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

handlers_stack = ControlBrokerStack(
    deploy_stage or app,
    f"CBHandlersStack{STACK_VERSION}",
    env=env,
    pac_framework=app.node.try_get_context("control-broker/pac-framework"),
)

if continuously_deployed:
    pipeline_stack = GitHubCDKPipelineStack(
        app,
        f"CBCICDDeployment{STACK_VERSION}",
        env=env,
        **app.node.try_get_context(
            "control-broker/continuous-deployment/github-config"
        ),
    )
    pipeline_stack.pipeline.add_stage(deploy_stage)

app.synth()