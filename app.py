#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.handlers_stack import HandlersStack
from stacks.pipeline_stack import GitHubCDKPipelineStack

STACK_VERSION = "V0x10x0"

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

handlers_stack = HandlersStack(
    app,
    f"CBHandlersStack{STACK_VERSION}",
    env=env,
    pac_framework=app.node.try_get_context("control-broker/pac-framework"),
)

if app.node.try_get_context("control-broker/continuous-deployment/enabled"):
    github_config = app.node.try_get_context("control-broker/continuous-deployment/github-config")
    pipeline_stack = GitHubCDKPipelineStack(
        app,
        f"CBPipelineStack{STACK_VERSION}",
        env=env,
        github_repo_name = github_config["github_repo_name"],
        github_repo_owner = github_config["github_repo_owner"],
        github_repo_branch = github_config["github_repo_branch"],
    )

app.synth()