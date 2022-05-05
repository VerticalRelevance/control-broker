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

        self.endpoint()

    def endpoint(self):
        
        # api

        self.http_api = aws_apigatewayv2_alpha.HttpApi(
            self,
            "ControlBrokerEndpoint",
        )
        
        self.paths = {
            "CloudFormation":"/CloudFormation"
        }
        
        routes = self.http_api.add_routes(
            path=self.paths['CloudFormation'],
            methods=[aws_apigatewayv2_alpha.HttpMethod.POST],
            # integration=integration,
            # authorizer=authorizer_lambda
            # authorizer=authorizer_iam
        )
        
        self.invoke_cloudformation = path.join(
            self.http_api.url.rstrip("/"), self.paths['CloudFormation'].strip("/")
        )

        CfnOutput(self, "ApigwInvokeUrl", value=self.invoke_cloudformation)