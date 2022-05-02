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
    aws_lambda_python_alpha, # experimental as of 4.25.22
)
from constructs import Construct


class ClientStack(Stack):
    """Client Layer"""

    def __init__(
        self,
        *args,
        control_broker_outer_state_machine: aws_stepfunctions.StateMachine,
        control_broker_roles: List[aws_iam.Role],
        control_broker_eval_results_bucket: aws_s3.Bucket,
        **kwargs,
    ):
        """Create a ClientStack.

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
    
        self.apigw()
        # self.consumer_client_retry()
        
    def apigw(self):
        
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
                "$request.header.Authorization", # Authorization must be present in headers or 401, e.g. r = requests.post(url,auth = auth, ...)
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
            environment = {
                "ControlBrokerOuterSfnArn" : self.control_broker_outer_state_machine.state_machine_arn,
                "ControlBrokerEvalResultsReportsBucket": self.control_broker_eval_results_bucket.bucket_name
            }
        )
        
        lambda_invoked_by_apigw.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "states:StartExecution",
                ],
                resources=[
                    self.control_broker_outer_state_machine.state_machine_arn
                ],
            )
        )

        integration = aws_apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            "ControlBrokerClient",
            lambda_invoked_by_apigw
        )
    
        # api
    
        self.http_api = aws_apigatewayv2_alpha.HttpApi(
            self,
            "ControlBrokerClient",
            # default_authorizer = authorizer
        )
        
        self.path = "/"
        
        routes = self.http_api.add_routes(
            path=self.path,
            methods=[
                aws_apigatewayv2_alpha.HttpMethod.POST
            ],
            integration=integration,
            authorizer=authorizer_lambda
            # authorizer=authorizer_iam
        )
        
        self.apigw_full_invoke_url = f'{self.http_api.url[:-1]}{self.path}' # remove duplicate slash
        
        CfnOutput(self, "ApigwInvokeUrl", value=self.apigw_full_invoke_url)

    def consumer_client_retry(self):
        
        # object exists
        
        self.lambda_object_exists = aws_lambda.Function(
            self,
            "ObjectExists",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,  # todo power-tune
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/s3_head_object"
            ),
        )

        self.lambda_object_exists.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:HeadObject",
                    "s3:GetObject",
                    "s3:List*",
                ],
                resources=[
                    self.control_broker_eval_results_bucket.bucket_arn,
                    f"{self.control_broker_eval_results_bucket.bucket_arn}*"
                ],
            )
        )
        
        # sign apigw request

        self.lambda_sign_apigw_request = aws_lambda_python_alpha.PythonFunction(
            self,
            "SignApigwRequest",
            entry="./supplementary_files/lambdas/sign_apigw_request",
            runtime= aws_lambda.Runtime.PYTHON_3_9,
            index="lambda_function.py",
            handler="lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            environment = {
                "ApigwInvokeUrl" : self.apigw_full_invoke_url
            },
            layers=[
                aws_lambda_python_alpha.PythonLayerVersion(
                    self,
                    "aws_requests_auth",
                    entry="./supplementary_files/lambda_layers/aws_requests_auth",
                    compatible_runtimes=[
                        aws_lambda.Runtime.PYTHON_3_9
                    ]
                ),
                aws_lambda_python_alpha.PythonLayerVersion(self,
                    "requests",
                    entry="./supplementary_files/lambda_layers/requests",
                    compatible_runtimes=[
                        aws_lambda.Runtime.PYTHON_3_9
                    ]
                ),
            ]
        )
        
        # s3 select
        
        self.lambda_s3_select = aws_lambda.Function(
            self,
            "S3Select",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset("./supplementary_files/lambdas/s3_select"),
        )

        self.lambda_s3_select.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:HeadObject",
                    "s3:GetObject",
                    "s3:List*",
                    "s3:SelectObjectContent",
                ],
                resources=[
                    self.control_broker_eval_results_bucket.bucket_arn,
                    f"{self.control_broker_eval_results_bucket.bucket_arn}/*",
                ],
            )
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
                    "lambda:InvokeFunction",
                ],
                resources=[
                    self.lambda_sign_apigw_request.function_arn,
                    self.lambda_object_exists.function_arn,
                    self.lambda_s3_select.function_arn
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
                # level="ERROR",
                include_execution_data=True,
                level="ALL"
            ),
            definition_string=json.dumps(
                {
                    "StartAt": "SignApigwRequest",
                    "States": {
                        "SignApigwRequest": {
                            "Type": "Task",
                            "Next": "CheckResultsReportExists",
                            "ResultPath": "$.SignApigwRequest",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_sign_apigw_request.function_name,
                                "Payload.$": "$"
                            },
                            "ResultSelector": {
                                "Payload.$": "$.Payload"
                            },
                        },
                        "CheckResultsReportExists": {
                            "Type": "Task",
                            "Next": "GetResultsReportIsCompliantBoolean",
                            "ResultPath": "$.CheckResultsReportExists",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_object_exists.function_name,
                                "Payload": {
                                    "S3Uri.$":"$.SignApigwRequest.Payload.ControlBrokerRequestStatus.ResultsReportS3Uri"
                                }
                            },
                            "ResultSelector": {
                                "Payload.$": "$.Payload"
                            },
                            "Retry": [
                                {
                                    "ErrorEquals": [
                                        "ObjectDoesNotExistException"
                                    ],
                                    "IntervalSeconds": 1,
                                    "MaxAttempts": 6,
                                    "BackoffRate": 2.0
                                }
                            ],
                            "Catch": [
                                {
                                    "ErrorEquals":[
                                        "States.ALL"
                                    ],
                                    "Next": "ResultsReportDoesNotYetExist"
                                }
                            ]
                        },
                        "ResultsReportDoesNotYetExist": {
                            "Type":"Fail"
                        },
                        "GetResultsReportIsCompliantBoolean": {
                            "Type": "Task",
                            "Next": "ChoiceIsComplaint",
                            "ResultPath": "$.GetResultsReportIsCompliantBoolean",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_s3_select.function_name,
                                "Payload": {
                                    "S3Uri.$":"$.SignApigwRequest.Payload.ControlBrokerRequestStatus.ResultsReportS3Uri",
                                    "Expression": "SELECT * from S3Object s",
                                },
                            },
                            "ResultSelector": {"S3SelectResult.$": "$.Payload.Selected"},
                        },
                        "ChoiceIsComplaint": {
                            "Type":"Choice",
                            "Default":"CompliantFalse",
                            "Choices":[
                                {
                                    "Variable":"$.GetResultsReportIsCompliantBoolean.S3SelectResult.ControlBrokerResultsReport.Evaluation.IsCompliant",
                                    "BooleanEquals":True,
                                    "Next":"CompliantTrue"
                                }
                            ]
                        },
                        "CompliantTrue": {
                            "Type":"Succeed"
                        },
                        "CompliantFalse": {
                            "Type":"Fail"
                        }
                    }
                }
            )
        )
        
        self.sfn_consumer_client.node.add_dependency(self.role_consumer_client_sfn)
        
        