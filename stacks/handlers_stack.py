import os
import json
from typing import List, Sequence
from os import path

from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    aws_lambda,
    aws_iam,
    aws_logs,
    aws_apigatewayv2,
    aws_apigatewayv2_alpha,  # experimental as of 4.25.22
    aws_apigatewayv2_authorizers_alpha,
    aws_apigatewayv2_integrations_alpha,  # experimental as of 4.25.22,
    aws_logs,
    RemovalPolicy,
)

from components.control_broker_api import ControlBrokerApi


class HandlersStack(Stack):
    def __init__(
        self,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)

        self.eval_engine()
        self.endpoint()

        self.api = ControlBrokerApi(self.lambda_eval_engine_lamdalith, None)

    def endpoint(self):

        # auth - lambda

        lambda_authorizer = aws_lambda.Function(
            self,
            "CBEndpointAuthorizer",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas_handlers_stack/apigw_authorizer"
            ),
        )

        authorizer_lambda = aws_apigatewayv2_authorizers_alpha.HttpLambdaAuthorizer(
            "CBEndpointAuthorizer",
            lambda_authorizer,
            response_types=[
                aws_apigatewayv2_authorizers_alpha.HttpLambdaResponseType.SIMPLE
            ],
            results_cache_ttl=Duration.seconds(0),
            identity_source=[
                "$request.header.Authorization",  # Authorization must be present in headers or 401, e.g. r = requests.post(url,auth = auth, ...)
            ],
        )

        # integration

        lambda_invoked_by_apigw_cloudformation = aws_lambda.Function(
            self,
            "InvokedByApigwCloudFormation",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas_handlers_stack/invoked_by_apigw_cloudformation"
            ),
            environment={
                "EvalEngineLambdalithFunctionName": self.eval_engine_lamdalith.function_name
            },
        )

        lambda_invoked_by_apigw_cloudformation.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "lambda:Invoke",
                ],
                resources=[self.lambda_eval_engine_lamdalith.lambda_function_arn],
            )
        )

        self.api.add_api_handler(
            "CloudFormation", lambda_invoked_by_apigw_cloudformation, "/CloudFormation"
        )

    def eval_engine(self):

        self.lambda_eval_engine_lamdalith = aws_lambda.Function(
            self,
            "EvalEngineLambdalith",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas_handlers_stack/eval_engine_lamdalith"
            ),
        )
