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
from components import Construct


class EndpointStack(Stack):
    def __init__(
        self,
        *args,
        control_broker_outer_state_machine: aws_stepfunctions.StateMachine,
        control_broker_roles: List[aws_iam.Role],
        control_broker_eval_results_bucket: aws_s3.Bucket,
        **kwargs,
    ):
        """Create a EndpointStack.

        :param control_broker_outer_state_machine: The outer state machine to call when invoking the control broker during tests.
        :type control_broker_outer_state_machine: aws_stepfunctions.StateMachine
        :param control_broker_principals: The principals to which we need to give S3 access for our input bucket.
        :type control_broker_principals: List[aws_iam.IPrincipal]
        :param control_broker_eval_results_bucket: The bucket owned by ControlBroker to host Evaluation ResultsReports.
        :type control_broker_eval_results_bucket: aws_s3.Bcuket
        """
        super().__init__(*args, **kwargs)

        self.control_broker_outer_state_machine = control_broker_outer_state_machine
        self.control_broker_eval_results_bucket = control_broker_eval_results_bucket

        self.endpoint()

    def endpoint(self):

        # auth - lambda

        lambda_authorizer = aws_lambda.Function(
            self,
            "ControlBrokerClientAuthorizer",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/apigw_authorizer"
            ),
        )

        authorizer_lambda = aws_apigatewayv2_authorizers_alpha.HttpLambdaAuthorizer(
            "ControlBrokerClientAuthorizer",
            lambda_authorizer,
            response_types=[
                aws_apigatewayv2_authorizers_alpha.HttpLambdaResponseType.SIMPLE
            ],
            results_cache_ttl=Duration.seconds(0),
            identity_source=[
                "$request.header.Authorization",  # Authorization must be present in headers or 401, e.g. r = requests.post(url,auth = auth, ...)
            ],
        )

        # auth - iam

        # authorizer_iam = aws_apigatewayv2_authorizers_alpha.HttpIamAuthorizer()

        # integration

        lambda_invoked_by_apigw = aws_lambda.Function(
            self,
            "InvokedByApigw",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/invoked_by_apigw"
            ),
            environment={
                "ControlBrokerOuterSfnArn": self.control_broker_outer_state_machine.state_machine_arn,
                "ControlBrokerEvalResultsReportsBucket": self.control_broker_eval_results_bucket.bucket_name,
            },
        )

        lambda_invoked_by_apigw.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "states:StartExecution",
                ],
                resources=[self.control_broker_outer_state_machine.state_machine_arn],
            )
        )

        integration = aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            "ControlBrokerClient", lambda_invoked_by_apigw
        )

        # api

        self.http_api = aws_apigatewayv2_alpha.HttpApi(
            self,
            "ControlBrokerEndpoint",
            # default_authorizer = authorizer
        )

        self.path = "/"

        routes = self.http_api.add_routes(
            path=self.path,
            methods=[aws_apigatewayv2_alpha.HttpMethod.POST],
            integration=integration,
            authorizer=authorizer_lambda
            # authorizer=authorizer_iam
        )

        self.apigw_full_invoke_url = path.join(
            self.http_api.url.rstrip("/"), self.path.strip("/")
        )

        CfnOutput(self, "ApigwInvokeUrl", value=self.apigw_full_invoke_url)
        
        open_api_definition = f'aws apigatewayv2 export-api --api-id {self.http_api.http_api_id} --output-type YAML --specification OAS30 --stage-name $default stage-definition.yaml'
        
        CfnOutput(self, "CBEndpointOpenApiDefinition", value=open_api_definition)
