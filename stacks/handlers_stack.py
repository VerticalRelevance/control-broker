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
            "InvokedByApigw",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas_handlers_stack/invoked_by_apigw"
            ),
        )

        # lambda_invoked_by_apigw_cloudformation.role.add_to_policy(
        #     aws_iam.PolicyStatement(
        #         actions=[
        #             "states:StartExecution",
        #         ],
        #         resources=[self.control_broker_outer_state_machine.state_machine_arn],
        #     )
        # )
        
        integration_cloudformation = aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            "HandlerCloudFormation", lambda_invoked_by_apigw_cloudformation
        )
        
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
            integration=integration_cloudformation,
            authorizer=authorizer_lambda
        )
        
        self.invoke_cloudformation = path.join(
            self.http_api.url.rstrip("/"), self.paths['CloudFormation'].strip("/")
        )

        CfnOutput(self, "ApigwInvokeUrl", value=self.invoke_cloudformation)
        