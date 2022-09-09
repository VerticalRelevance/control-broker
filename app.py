#!/usr/bin/env python3
import os, json

import aws_cdk as cdk

# from stacks.control_broker_stack import ControlBrokerStack
from stacks.hub_stack import HubStack

STACK_VERSION = "V0x16x1"

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

spoke_account_path='./ignored/spoke_accounts.json' # not committed
with open(spoke_account_path,'r') as f:
    spoke_accounts=json.loads(f.read())

hub_stack = HubStack(
    app,
    f"HubStack{STACK_VERSION}",
    env=env,
    pac_framework=app.node.try_get_context("control-broker/pac-framework"),
    config_sns_topic=app.node.try_get_context("control-broker/config-sns-topic"),
    spoke_accounts=spoke_accounts,
    is_dev=True,
)

app.synth()