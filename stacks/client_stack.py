import os
import json
from typing import List, Sequence

from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_config,
    aws_dynamodb,
    aws_s3,
    aws_s3_deployment,
    aws_lambda,
    aws_stepfunctions,
    aws_iam,
    aws_logs,
    aws_events,
    aws_apigatewayv2,
    aws_apigatewayv2_integrations, # experimental as of 4.25.22
)
from constructs import Construct

from components.config_rules import ControlBrokerConfigRule


class ClientStack(Stack):
    """Client Layer"""

    def __init__(
        self,
        *args,
        control_broker_outer_state_machine: aws_stepfunctions.StateMachine,
        control_broker_roles: List[aws_iam.Role],
        **kwargs,
    ):
        """Create a ClientStack.

        :param control_broker_outer_state_machine: The outer state machine to call when invoking the control broker during tests.
        :type control_broker_outer_state_machine: aws_stepfunctions.StateMachine
        :param control_broker_principals: The principals to which we need to give S3 access for our input bucket.
        :type control_broker_principals: List[aws_iam.IPrincipal]
        """
        super().__init__(*args, **kwargs)
    
        self.main()
    
    def main(self):
    
        
        # Objective 1.0: enumerate credentials/awsID of requestor that client is aware of of
        
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
        )

        # lambda_invoked_by_apigw.role.add_to_policy(
        #     aws_iam.PolicyStatement(
        #         actions=[
        #             "s3:List*",
        #         ],
        #         resources=[
        #         ],
        #     )
        # )
    
        integration = aws_apigatewayv2_integrations.HttpLambdaIntegration("Integration", lambda_invoked_by_apigw)
    
        http_api = aws_apigatewayv2.HttpApi(self, "HttpApi")
        
        http_api.add_routes(
            path="/items",
            methods=[aws_apigatewayv2.HttpMethod.GET],
            integration=integration
        )