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
        )
        
        self.paths = {
            "CloudFormation":"/CloudFormation"
        }
        
        routes = self.http_api.add_routes(
            path=self.paths['CloudFormation'],
            methods=[aws_apigatewayv2_alpha.HttpMethod.POST],
            integration=integration,
            # authorizer=authorizer_lambda
            # authorizer=authorizer_iam
        )
        
        self.invoke_cloudformation = path.join(
            self.http_api.url.rstrip("/"), self.paths['CloudFormation'].strip("/")
        )

        CfnOutput(self, "ApigwInvokeUrl", value=self.invoke_cloudformation)