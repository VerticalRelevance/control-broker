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
    aws_sqs,
    aws_s3_deployment,
    aws_lambda,
    aws_stepfunctions,
    aws_iam,
    aws_logs,
    aws_events,
    aws_apigatewayv2,
    aws_apigatewayv2_alpha, # experimental as of 4.25.22
    aws_apigatewayv2_integrations_alpha, # experimental as of 4.25.22
    aws_apigatewayv2_authorizers_alpha, # experimental as of 4.25.22
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
    
        self.apigw()
        self.consumer_client()
    
    def apigw(self):
        
        # Objective 1.0: enumerate credentials/awsID of requestor that client is aware of of
        
        
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
            response_types=[aws_apigatewayv2_authorizers_alpha.HttpLambdaResponseType.SIMPLE],
            results_cache_ttl = Duration.seconds(0),
            identity_source = [
                "$request.header.Authorization", # request must match or 401: requests.get(invoke_url,headers={'Authorization':'foo'})
                # "$context.identity.principalOrgId",
            ]
        )
        
        
        # auth - iam
        
        authorizer_iam = aws_apigatewayv2_authorizers_alpha.HttpIamAuthorizer()

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
        )

        integration = aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            "ControlBrokerClient",
            lambda_invoked_by_apigw
        )
    
        # api
    
        http_api = aws_apigatewayv2_alpha.HttpApi(
            self,
            "ControlBrokerClient",
            # default_authorizer = authorizer
        )
        
        path = "/items"
        
        routes = http_api.add_routes(
            path=path,
            methods=[
                aws_apigatewayv2_alpha.HttpMethod.GET
            ],
            integration=integration,
            authorizer=authorizer_lambda
            # authorizer=authorizer_iam
        )
        
        # routes[0].grant_invoke(principal)
        
        
        # test Invoker
        
        # lambda_apigw_invoker = aws_lambda.Function(
        #     self,
        #     "ApigwInvoker",
        #     runtime=aws_lambda.Runtime.PYTHON_3_9,
        #     handler="lambda_function.lambda_handler",
        #     timeout=Duration.seconds(60),
        #     memory_size=1024,
        #     code=aws_lambda.Code.from_asset(
        #         "./supplementary_files/lambdas/invoked_by_apigw"
        #     ),
        # )

        # lambda_invoked_by_apigw.role.add_to_policy(
        #     aws_iam.PolicyStatement(
        #         actions=[
        #             "s3:List*",
        #         ],
        #         resources=[
        #         ],
        #     )
        # )
        
        """
        Eval Engine Client Layer
        update 4.25.22
        
        
        objective:
        
        manage access control to
        
        
        input:
        
        1+ synthedTemplates
        BucketOwnedBy: Requestor
        AccessGrantedTo: EvalEngine
        AccessType: Read
        
        output:
        
        1 evaluationReport
        BucketOwnedBy: EvalEngine
        AccessGrantedTo: Requestor
        AccessType: Read
        
        
        desired method:
        
        
        ReportRequestor awsID is received by EvalEngine.
        EvalEngine writes the evaluationReport to S3 with key:
        my-requestor-id.report.json
        
        ReportRequestor make the getObject request as signed by that same awsID 
        
        The dynamic bucket policy uses IAM Conditions to compare requestor's awsID to the key,
        ensuring that they can only request their own report.
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-principalarn
        
        
        progress so far:
        
        
        this `aws-requests-auth` package (https://github.com/DavidMuller/aws-requests-auth)
        uses boto3 creds to sign Python `requests` request
        
        when this is done, both the customAuth Lambda and InvokedByApigw have access to a string in
        the identity source and authorization header with the following format per these docs
        
        'AWS4-HMAC-SHA256 Credential=MY_ACCESS_KEY/20220425/us-east-1/execute-api/aws4_request, SignedHeaders=host;x-amz-date, Signature=MY_SIG',
        
        https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-auth-using-authorization-header.html
        """
    
    def consumer_client(self):
        
        # sqs
        
        queue_consumer_client_task_tokens = aws_sqs.Queue(
            self,
            "ConsumerClientTaskTokens",
            fifo=False
        )
        
        
        # sfn
        
        log_group_consumer_client_sfn = aws_logs.LogGroup(
            self,
            "ConsumerClientLogs",
            log_group_name=f"/aws/vendedlogs/states/ConsumerClientLogs-{self.stack_name}",
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.role_consumer_client_sfn = aws_iam.Role(
            self,
            "ConsumerClientSfn",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
        )

        self.role_consumer_client_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    # "logs:*",
                    "logs:CreateLogDelivery",
                    "logs:GetLogDelivery",
                    "logs:UpdateLogDelivery",
                    "logs:DeleteLogDelivery",
                    "logs:ListLogDeliveries",
                    "logs:PutResourcePolicy",
                    "logs:DescribeResourcePolicies",
                    "logs:DescribeLogGroups",
                ],
                resources=[
                    "*",
                    log_group_consumer_client_sfn.log_group_arn,
                    f"{log_group_consumer_client_sfn.log_group_arn}*",
                ],
            )
        )
        self.role_consumer_client_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "sqs:SendMessage",
                ],
                resources=[
                    "*",
                    queue_consumer_client_task_tokens.queue_arn,
                    f"{queue_consumer_client_task_tokens.queue_arn}*",
                ],
            )
        )

        self.sfn_consumer_client = aws_stepfunctions.CfnStateMachine(
            self,
            "ConsumerClient",
            # state_machine_type="EXPRESS",
            state_machine_type="STANDARD",
            role_arn=self.role_consumer_client_sfn.role_arn,
            logging_configuration=aws_stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                destinations=[
                    aws_stepfunctions.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=aws_stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn=log_group_consumer_client_sfn.log_group_arn
                        )
                    )
                ],
                # include_execution_data=False,
                # level="ALL"
                include_execution_data=True,
                level="ERROR",
            ),
            definition_string=json.dumps(
                {
                    "StartAt": "ParseInput",
                    "States": {
                        "ParseInput": {
                            "Type": "Pass",
                            "End": True,
                        }
                    }
                }
            )
        )
        
        self.sfn_consumer_client.node.add_dependency(self.role_consumer_client_sfn)

        