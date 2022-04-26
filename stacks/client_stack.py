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
        control_broker_eval_results_bucket: aws_s3.Bucket,
        **kwargs,
    ):
        """Create a ClientStack.

        :param control_broker_outer_state_machine: The outer state machine to call when invoking the control broker during tests.
        :type control_broker_outer_state_machine: aws_stepfunctions.StateMachine
        :param control_broker_principals: The principals to which we need to give S3 access for our input bucket.
        :type control_broker_principals: List[aws_iam.IPrincipal]
        """
        super().__init__(*args, **kwargs)
    
        self.control_broker_outer_state_machine = control_broker_outer_state_machine
        self.control_broker_eval_results_bucket = control_broker_eval_results_bucket
    
        self.apigw()
        # self.consumer_client_task_token() # outer consumer sfn would have to be standard, can't be express endpoint and support waitForTaskToken
        self.consumer_client_retry()
        
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
        
        self.apigw_full_invoke_url = f'{self.http_api.url}{self.path}'
        
        
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
    
    def consumer_client_task_token(self):
        
        # sqs
        
        queue_consumer_client_task_tokens = aws_sqs.Queue(
            self,
            "ConsumerClientTaskTokens",
        )
        
        # s3
        
        self.bucket_consumer_inputs = aws_s3.Bucket(
            self,
            "ConsumerInputs",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
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
                    "StartAt": "SendMessageTaskToken",
                    "States": {
                        "SendMessageTaskToken": {
                            "Type": "Task",
                            "Next": "GetResultsReport",
                            "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
                            "HeartbeatSeconds": 10, #FIXME
                            "Parameters": {
                                "QueueUrl": queue_consumer_client_task_tokens.queue_url,
                                "MessageBody": {
                                    "Message": {
                                        "ControlBrokerConsumerInputs":{
                                            "Bucket": self.bucket_consumer_inputs.bucket_name,
                                            "ConsumerMetadata": "my-consumer-metadata-key",
                                            "InputKeys":[
                                                "input-01-key",
                                                "input-02-key"
                                            ]
                                        }
                                    },
                                    "TaskToken.$": "$$.Task.Token"
                                }
                            },
                        },
                        "GetResultsReport": {
                            "Type":"Succeed"
                        }
                    }
                }
            )
        )
        
        self.sfn_consumer_client.node.add_dependency(self.role_consumer_client_sfn)
    
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
                    # "*",
                    "arn:aws:s3:::cschneider-terraform-backend/*" # test
                ],
            )
        )
        
        # sign apigw request

        layer_requests = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            "Requests",
            "arn:aws:lambda:us-east-1:899456967600:layer:requests:1" # built via CodeCommit/cschneider-utils/lambda/utils/layer-builder.sh
        )
        
        layer_aws_requests_auth = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            "AwsRequestsAuth",
            "arn:aws:lambda:us-east-1:899456967600:layer:aws-requests-auth:1" # built via CodeCommit/cschneider-utils/lambda/utils/layer-builder.sh
        )
        
        self.lambda_sign_apigw_request = aws_lambda.Function(
            self,
            "SignApigwRequest",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/sign_apigw_request"
            ),
            layers = [
                layer_requests,
                layer_aws_requests_auth
            ],
            environment = {
                "ApigwInvokeUrl" : self.apigw_full_invoke_url
            }
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
                    self.lambda_object_exists.function_arn
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
                            "Next": "ResultsReportExists",
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
                                    "MaxAttempts": 3,
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
                        "ResultsReportExists": {
                            "Type":"Succeed"
                        }
                    }
                }
            )
        )
        
        self.sfn_consumer_client.node.add_dependency(self.role_consumer_client_sfn)
        
        