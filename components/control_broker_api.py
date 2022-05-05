import json

import aws_cdk
from aws_cdk import (
    CfnOutput,
    aws_apigatewayv2,
    aws_apigatewayv2_alpha,
    aws_apigatewayv2_integrations_alpha,
    aws_iam,
    aws_lambda,
    aws_logs,
    aws_s3,
    aws_stepfunctions,
)
from os import path


class ControlBrokerApiBroken(aws_apigatewayv2_alpha.HttpApi):
    CONTROL_BROKER_EVAL_ENGINE_INVOCATION_PATH = "/EvalEngine"

    def __init__(
        self,
        *args,
        control_broker_invocation_lambda_function: aws_lambda.Function,
        control_broker_results_bucket: aws_s3.Bucket,
        access_log_retention: aws_logs.RetentionDays = aws_logs.RetentionDays.ONE_DAY,
        **kwargs,
    ):
        super().__init__(self, id, *args, **kwargs)
        
        self.control_broker_invocation_lambda_function_name: str = (
            control_broker_invocation_lambda_function.function_name
        )
        
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
                    {
                        "requestId":"$context.requestId",
                        "ip": "$context.identity.sourceIp",
                        "requestTime":"$context.requestTime",
                        "httpMethod":"$context.httpMethod",
                        "routeKey":"$context.routeKey",
                        "status":"$context.status",
                        "protocol":"$context.protocol",
                        "responseLength":"$context.responseLength",
                        "integrationErrorMessage":"$context.integrationErrorMessage"
                    }
                ),
            },
        )
        self.urls = []

    def _add_control_broker_eval_engine_invocation_route(self):
        """Adds a route, which only handlers can call, that directly invokes the Control Broker Eval Engine."""

        self.handler_invocation_integration = (
            aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
                "ControlBrokerControlPlaneInvocation",
                handler=self.control_broker_invocation_lambda_function,
            )
        )
        self.add_routes(
            path=self.CONTROL_BROKER_EVAL_ENGINE_INVOCATION_PATH,
        )
        eval_engine_url = path.join(
            self.http_api.url.rstrip("/"),
            self.CONTROL_BROKER_EVAL_ENGINE_INVOCATION_PATH.strip("/"),
        )
        self.urls.append(eval_engine_url)
        self.eval_engine_invocation_url_mapping.overwrite_header(
            "x-control-broker-invoke-url", eval_engine_url
        )
        CfnOutput(self, f"EvalEngineUrl", eval_engine_url)
        self.handler_invocation_url_mapping = aws_apigatewayv2_alpha.ParameterMapping()

    def add_api_handler(
        self,
        name: str,
        lambda_function: aws_cdk.aws_lambda.Function,
        path: str,
        **kwargs,
    ):
        """Add a Control Broker Handler to process requests. Expected to invoke the Control Broker upon successful completion.

        :param name: _description_
        :type name: str
        :param lambda_function: _description_
        :type lambda_function: aws_cdk.aws_lambda.Function
        :param path: _description_
        :type path: str
        """

        # TODO: Test that users cannot inject their own eval engine URL when calling the API with that header
        integration = aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            name, lambda_function, parameter_mapping=self.handler_invocation_url_mapping
        )
        
        self.add_routes(
            path=path,
            methods=[aws_apigatewayv2_alpha.HttpMethod.POST],
            integration=integration,
            **kwargs,
        )
        
        handler_url = path.join(self.http_api.url.rstrip("/"), path.strip("/"))
        
        self.urls.append(handler_url)
        
        CfnOutput(self, f"{name}HandlerUrl", handler_url)

class ControlBrokerApi(aws_apigatewayv2_alpha.HttpApi): # does not deploy
    def __init__(
        self,
        *args,
        **kwargs
    ):
        
        super().__init__(self, id, *args, **kwargs)

        pass