from cgitb import handler
import json

import aws_cdk
from aws_cdk import (
    CfnOutput,
    aws_apigatewayv2,
    aws_apigatewayv2_alpha,
    aws_apigatewayv2_integrations_alpha,
    aws_iam,
    aws_logs,
    aws_s3,
    aws_stepfunctions,
)
from constructs import Construct


class ControlBrokerApi(aws_apigatewayv2_alpha.HttpApi):
    def __init__(
        self,
        *args,
        control_broker_state_machine: aws_stepfunctions.StateMachine,
        control_broker_results_bucket: aws_s3.Bucket,
        access_log_retention: aws_logs.RetentionDays = aws_logs.RetentionDays.ONE_DAY,
        **kwargs
    ):
        super().__init__(self, id, *args, **kwargs)
        self.control_broker_state_machine = control_broker_state_machine
        self.control_broker_results_bucket = control_broker_results_bucket
        api_log_group = aws_logs.LogGroup(
            self, f"{id}AccessLogs", retention=access_log_retention
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
        self.urls = []

    def add_api_handler(
        self, name: str, lambda_function: aws_cdk.aws_lambda.Function, path: str, **kwargs
    ):
        """Add a Control Broker Handler to process requests. Expected to invoke the Control Broker upon successful completion.

        :param name: _description_
        :type name: str
        :param lambda_function: _description_
        :type lambda_function: aws_cdk.aws_lambda.Function
        :param path: _description_
        :type path: str
        """
        integration = aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            name, lambda_function, 
        )
        self.add_routes(
            path=path,
            methods=[aws_apigatewayv2_alpha.HttpMethod.POST],
            integration=integration,
            **kwargs
        )
        handler_url = path.join(
            self.http_api.url.rstrip("/"), path.strip("/")
        )
        self.urls.append(handler_url)
        CfnOutput(self, f"{name}HandlerUrl", handler_url)