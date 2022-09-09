import os
import json
from typing import List, Sequence
from os import path

from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_lambda,
    aws_iam,
    aws_config,
    aws_sqs,
    aws_s3,
    aws_s3_deployment,
    aws_s3_notifications,
    aws_logs,
    aws_events,
    aws_events_targets,
    aws_apigatewayv2,
    aws_s3objectlambda,
    # experimental
    aws_apigatewayv2_alpha,
    aws_apigatewayv2_authorizers_alpha,
    aws_apigatewayv2_integrations_alpha,
    aws_lambda_python_alpha,
    aws_s3objectlambda_alpha,
)

from constructs import Construct


class HubStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        pac_framework: str,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        self.pac_framework = pac_framework