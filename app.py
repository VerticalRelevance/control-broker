#!/usr/bin/env python3
import os

import aws_cdk as cdk

from blueprint_pipelines.control_broker_eval_engine_stack import ControlBrokerEvalEngineStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)

# Input parameters
application_team_cdk_app = {
    'PipelineOwnershipMetadata': './supplementary_files/pipeline-ownership-metadata/business-unit-a/eval-engine-metadata.json'
}



ControlBrokerEvalEngineStack(
    app,
    "ControlBrokerEvalEngineCdkStackV4x6",
    application_team_cdk_app = application_team_cdk_app,
    env = env
    )

app.synth()