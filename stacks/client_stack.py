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
    aws_apigatewayv2
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
    
        
        # enumerate credentials/awsID of requestor that client is aware of of
        
        pass