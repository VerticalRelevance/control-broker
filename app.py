#!/usr/bin/env python3
import os
from pathlib import Path
from typing import List

import aws_cdk as cdk

from blueprint_pipelines.control_broker_eval_engine_stack import (
    ControlBrokerEvalEngineStack,
)

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

application_team_cdk_app = {
    "PipelineOwnershipMetadata": "./supplementary_files/pipeline-ownership-metadata/business-unit-a/eval-engine-metadata.json",
}

control_broker_stack = ControlBrokerEvalEngineStack(
    app,
    "ControlBrokerEvalEngineCdkStackV5x0",
    application_team_cdk_app=application_team_cdk_app,
    env=env,
)

app.synth()
