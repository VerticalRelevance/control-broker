import os
import json
from typing import List, Sequence
from os import path

from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    aws_s3,
    aws_lambda,
    aws_stepfunctions,
    aws_iam,
    aws_apigatewayv2_alpha,  # experimental as of 4.25.22
    aws_apigatewayv2_integrations_alpha,  # experimental as of 4.25.22
    aws_apigatewayv2_authorizers_alpha,  # experimental as of 4.25.22
)
from constructs import Construct


class HandlersStack(Stack):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        
        super().__init__(*args, **kwargs)
