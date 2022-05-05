#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.handlers_stack import HandlersStack

STACK_VERSION = "V0x8x0"

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

handlers_stack = HandlersStack(
    app,
    f"CBHandlersStack{STACK_VERSION}",
    env=env,
)
app.synth()