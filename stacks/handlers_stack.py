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
    aws_apigatewayv2_integrations_alpha,  # experimental as of 4.25.22,
    aws_logs,
)


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
            "InvokedByApigwCloudFormation",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas_handlers_stack/invoked_by_apigw_cloudformation"
            ),
            environment = {
                'EvalEngineLambdalithFunctionName':self.eval_engine_lamdalith.function_name
            }
        )

        lambda_invoked_by_apigw_cloudformation.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "lambda:Invoke",
                ],
                resources=[self.lambda_eval_engine_lamdalith.lambda_function_arn],
            )
        )
        
        integration_cloudformation = aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            "HandlerCloudFormation", lambda_invoked_by_apigw_cloudformation
        )

        # api

        self.http_api = aws_apigatewayv2_alpha.HttpApi(
            self,
            "ControlBrokerEndpoint",
        )

        self.paths = {"CloudFormation": "/CloudFormation"}

        routes = self.http_api.add_routes(
            path=self.paths["CloudFormation"],
            methods=[aws_apigatewayv2_alpha.HttpMethod.POST],
            integration=integration_cloudformation,
            authorizer=authorizer_lambda,
        )

        api_log_group = aws_logs.LogGroup(
            self, "HttpApiLogs", retention=aws_logs.RetentionDays.ONE_DAY
        )
        api_log_group.grant_write(aws_iam.ServicePrincipal("apigateway.amazonaws.com"))

        cfn_default_stage: aws_apigatewayv2.CfnStage = self.http_api.default_stage.node
        cfn_default_stage.add_property_override(
            "AccessLogSettings",
            {
                "DestinationArn": api_log_group.log_group_arn,
                "Format": json.dumps(
                    '{ "requestId":"$context.requestId", "ip": "$context.identity.sourceIp", "requestTime":"$context.requestTime", "httpMethod":"$context.httpMethod","routeKey":"$context.routeKey", "status":"$context.status","protocol":"$context.protocol", "responseLength":"$context.responseLength", "$context.integrationErrorMessage"}'
                ),
            },
        )

        self.invoke_cloudformation = path.join(
            self.http_api.url.rstrip("/"), self.paths["CloudFormation"].strip("/")
        )

        CfnOutput(self, "InvokeCloudFormation", value=self.invoke_cloudformation)
        
        log_group_invoke_cloudformation = aws_logs.LogGroup(
            self,
            "InvokeCloudFormationLogs",
            log_group_name=f"InvokeCloudFormation",
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # CfnOutput(self, "InvokeCloudFormationLogsArn", value=log_group_invoke_cloudformation.log_group_arn)
    
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
