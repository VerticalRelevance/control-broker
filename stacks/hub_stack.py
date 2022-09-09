import os
import json
from typing import List, Sequence
from os import path

from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_lambda,
    aws_iam,
    aws_config,
    aws_sqs,
    aws_s3,
    aws_s3_deployment,
    aws_s3_notifications,
    aws_logs,
    aws_events,
    aws_events_targets,
    aws_apigatewayv2,
    aws_s3objectlambda,
    aws_lambda_event_sources,
    # experimental
    aws_apigatewayv2_alpha,
    aws_apigatewayv2_authorizers_alpha,
    aws_apigatewayv2_integrations_alpha,
    aws_lambda_python_alpha,
    aws_s3objectlambda_alpha,
)

from constructs import Construct


class HubStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        pac_framework: str,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        self.pac_framework = pac_framework
        
        self.lambda_invoked_by_sqs = aws_lambda.Function(
            self,
            "InvokedByApigwConfigEvent",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/invoked_by_sqs"
            ),
        )
        
        # self.lambda_invoked_by_sqs.role.add_to_policy(
        #     aws_iam.PolicyStatement(
        #         actions=[
        #             ":",
        #         ],
        #         resources=["*"],
        #     )
        # )
        
        queue_subscribed_to_agg_sns=aws_sqs.Queue(self,"SubscribedToAggSns")
        
        event_source_sqs = aws_lambda_event_sources.SqsEventSource(queue)
        self.lambda_invoked_by_sqs.add_event_source(event_source_sqs)