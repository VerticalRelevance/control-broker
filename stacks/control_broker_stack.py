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
)
from constructs import Construct

from components.config_rules import ControlBrokerConfigRule


class ControlBrokerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        application_team_cdk_app: dict,
        config_rule_enabled: bool = False,
        config_rule_scope: aws_config.RuleScope = None,
        **kwargs,
    ) -> None:
        """A full Control Broker installation.

        :param scope:
        :type scope: Construct
        :param construct_id:
        :type construct_id: str
        :param application_team_cdk_app: (_DEPRECATED_)
        :type application_team_cdk_app: dict
        :param config_rule_enabled: Whether to create a custom config rule that sends config events to the control broker to obtain Config compliance status, defaults to False
        :type config_rule_enabled: bool, optional
        :param config_rule_scope: What Config scope to use with the config rule, if enabled., defaults to None
        :type config_rule_scope: aws_config.RuleScope, optional
        :param continously_deployed: Whether to launch the Control Broker via a CDK Pipeline and deploy on code changes, defaults to True
        :type continously_deployed: bool, optional
        :param github_repo_name: Required if continously_deployed is True
        :type github_repo_name: str, optional
        :param github_repo_owner: Required if continously_deployed is True
        :type github_repo_owner: str, optional
        :param github_repo_branch: Required if continously_deployed is True
        :type github_repo_branch: str, optional

        :raises ValueError: When config_rule_enabled is True and config_rule_scope is None
        :raises ValueError: When continously_deployed is True and any of the github variables is not set
        """
        super().__init__(scope, construct_id, **kwargs)

        self.application_team_cdk_app = application_team_cdk_app

        self.pipeline_ownership_metadata = {}
        (
            self.pipeline_ownership_metadata["Directory"],
            self.pipeline_ownership_metadata["Suffix"],
        ) = os.path.split(application_team_cdk_app["PipelineOwnershipMetadata"])

        self.deploy_utils()
        self.s3_deploy_local_assets()
        self.deploy_inner_sfn_lambdas()
        self.deploy_inner_sfn()
        self.deploy_outer_sfn_lambdas()
        self.deploy_outer_sfn()

        self.config_rule = None
        if config_rule_enabled:
            if not config_rule_scope:
                raise ValueError(
                    "Expected config_rule_scope to be set since config rule is enabled"
                )
            self.config_rule = ControlBrokerConfigRule(
                self,
                "ControlBrokerConfigRule",
                rule_scope=config_rule_scope,
                control_broker_statemachine=aws_stepfunctions.StateMachine.from_state_machine_arn(
                    self,
                    "ControlBrokerStateMachine",
                    self.sfn_outer_eval_engine.attr_arn,
                ),
            )

        self.Input_reader_roles: List[aws_iam.Role] = [
            self.lambda_opa_eval_python_subprocess_single_threaded.role,
            self.role_inner_eval_engine_sfn
        ]

        self.outer_eval_engine_state_machine = aws_stepfunctions.StateMachine.from_state_machine_arn(self, "OuterEvalEngineStateMachineObj", self.sfn_outer_eval_engine.attr_arn)
        
        self.eval_results_reports_bucket = aws_s3.Bucket.from_bucket_name(self,
            "EvalResultsReportsBucketObj", self.bucket_eval_results_reports.bucket_name)
        
        CfnOutput(
            self,
            "InputReaderArns",
            value=json.dumps([r.role_arn for r in self.Input_reader_roles]),
        )
        CfnOutput(self, "SfnInvokeArn", value=self.sfn_outer_eval_engine.attr_arn)

    def deploy_utils(self):

        # eval results

        self.table_eval_results = aws_dynamodb.Table(
            self,
            "EvalResults",
            partition_key=aws_dynamodb.Attribute(
                name="pk", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="sk", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # event bridge bus

        self.event_bus_infractions = aws_events.EventBus(self, "Infractions")

        # debug event bridge by logging events

        logs_infraction_events = aws_logs.LogGroup(
            self, "InfractionEvents", removal_policy=RemovalPolicy.DESTROY
        )
        logs_infraction_events.grant_write(
            aws_iam.ServicePrincipal("events.amazonaws.com")
        )

        cfn_rule = aws_events.CfnRule(
            self,
            "ListenAllInfractions",
            state="ENABLED",
            event_bus_name=self.event_bus_infractions.event_bus_name,
            event_pattern=aws_events.EventPattern(account=[self.account]),
            targets=[
                aws_events.CfnRule.TargetProperty(
                    arn=logs_infraction_events.log_group_arn, id="InfractionEvents"
                )
            ],
        )

        # result reports

        self.bucket_eval_results_reports = aws_s3.Bucket(
            self,
            "EvalResultsReports",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

    def s3_deploy_local_assets(self):

        # CfnOutput(self, "ApplicationTeamExampleAppRepositoryCloneSSH",
        #     value = self.repo_app_team_cdk.repository_clone_url_ssh
        # )

        # CfnOutput(self, "ApplicationTeamExampleAppRepositoryCloneHTTP",
        #     value = self.repo_app_team_cdk.repository_clone_url_http
        # )

        # pipeline ownership metadata

        self.bucket_pipeline_ownership_metadata = aws_s3.Bucket(
            self,
            "PipelineOwnershipMetadata",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        aws_s3_deployment.BucketDeployment(
            self,
            "PipelineOwnershipMetadataDir",
            sources=[
                aws_s3_deployment.Source.asset(
                    self.pipeline_ownership_metadata["Directory"]
                )
            ],
            destination_bucket=self.bucket_pipeline_ownership_metadata,
            retain_on_delete=False,
        )

        # opa policies

        self.bucket_opa_policies = aws_s3.Bucket(
            self,
            "OpaPolicies",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        aws_s3_deployment.BucketDeployment(
            self,
            "OpaPoliciesByService",
            sources=[
                aws_s3_deployment.Source.asset("./supplementary_files/opa-policies")
            ],
            destination_bucket=self.bucket_opa_policies,
            retain_on_delete=False,
        )

    def deploy_inner_sfn_lambdas(self):

        # opa eval - python subprocess - single threaded

        self.lambda_opa_eval_python_subprocess_single_threaded = aws_lambda.Function(
            self,
            "OpaEvalPythonSubprocessSingleThreaded",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=10240,  # todo power-tune
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/opa-eval/python-subprocess/single-threaded"
            ),
        )

        self.lambda_opa_eval_python_subprocess_single_threaded.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:HeadObject",
                    "s3:GetObject",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_opa_policies.bucket_arn,
                    f"{self.bucket_opa_policies.bucket_arn}/*",
                ],
            )
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
                    self.bucket_pipeline_ownership_metadata.bucket_arn,
                    f"{self.bucket_pipeline_ownership_metadata.bucket_arn}/*",
                ],
            )
        )
        
        # gather infractions

        self.lambda_gather_infractions = aws_lambda.Function(
            self,
            "GatherInfractions",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset("./supplementary_files/lambdas/gather_infractions"),
        )

        # handle infraction

        self.lambda_handle_infraction = aws_lambda.Function(
            self,
            "HandleInfraction",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset("./supplementary_files/lambdas/handle_infraction"),
            environment = {
                "TableName": self.table_eval_results.table_name,
                "EventBusName": self.event_bus_infractions.event_bus_name
            }
        )
        
        self.lambda_handle_infraction.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                ],
                resources=[
                    self.table_eval_results.table_arn,
                    f"{self.table_eval_results.table_arn}/*",
                ],
            )
        )
        
        self.lambda_handle_infraction.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "events:PutEvents",
                ],
                resources=[
                    self.event_bus_infractions.event_bus_arn,
                    f"{self.event_bus_infractions.event_bus_arn}*",
                ],
            )
        )

    def deploy_inner_sfn(self):

        log_group_inner_eval_engine_sfn = aws_logs.LogGroup(
            self,
            "InnerEvalEngineSfnLogs",
            log_group_name=f"/aws/vendedlogs/states/InnerEvalEngineSfnLogs-{self.stack_name}",
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.role_inner_eval_engine_sfn = aws_iam.Role(
            self,
            "InnerEvalEngineSfn",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
        )

        self.role_inner_eval_engine_sfn.add_to_policy(
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
                    log_group_inner_eval_engine_sfn.log_group_arn,
                    f"{log_group_inner_eval_engine_sfn.log_group_arn}*",
                ],
            )
        )
        self.role_inner_eval_engine_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[
                    self.lambda_opa_eval_python_subprocess_single_threaded.function_arn,
                    self.lambda_s3_select.function_arn,
                    self.lambda_gather_infractions.function_arn,
                    self.lambda_handle_infraction.function_arn,
                ],
            )
        )
        self.role_inner_eval_engine_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                ],
                resources=[
                    self.table_eval_results.table_arn,
                    f"{self.table_eval_results.table_arn}/*",
                ],
            )
        )
        self.role_inner_eval_engine_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "events:PutEvents",
                ],
                resources=[
                    self.event_bus_infractions.event_bus_arn,
                    f"{self.event_bus_infractions.event_bus_arn}*",
                ],
            )
        )

        self.sfn_inner_eval_engine = aws_stepfunctions.CfnStateMachine(
            self,
            "InnerEvalEngine",
            state_machine_type="EXPRESS",
            role_arn=self.role_inner_eval_engine_sfn.role_arn,
            logging_configuration=aws_stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                destinations=[
                    aws_stepfunctions.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=aws_stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn=log_group_inner_eval_engine_sfn.log_group_arn
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
                    "StartAt": "ParseInput",
                    "States": {
                        "ParseInput": {
                            "Type": "Pass",
                            "Next": "GetMetadata",
                            "Parameters": {
                                "JsonInput": {
                                    "Bucket.$": "$.Input.Bucket",
                                    "Key.$": "$.Input.Key",
                                },
                                "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfn.ExecutionId",
                            },
                            "ResultPath": "$",
                        },
                        "GetMetadata": {
                            "Type": "Task",
                            "Next": "OpaEval",
                            "ResultPath": "$.GetMetadata",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_s3_select.function_name,
                                "Payload": {
                                    "Bucket": self.bucket_pipeline_ownership_metadata.bucket_name,
                                    "Key": self.pipeline_ownership_metadata["Suffix"],
                                    "Expression": "SELECT * from S3Object s",
                                },
                            },
                            "ResultSelector": {"Metadata.$": "$.Payload.Selected"},
                        },
                        "OpaEval": {
                            "Type": "Task",
                            "Next": "GatherInfractions",
                            "ResultPath": "$.OpaEval",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_opa_eval_python_subprocess_single_threaded.function_name,
                                "Payload": {
                                    "JsonInput.$": "$.JsonInput",
                                    "OpaPolicies": {
                                        "Bucket": self.bucket_opa_policies.bucket_name
                                    },
                                },
                            },
                            "ResultSelector": {"OpaEvalResults.$": "$.Payload.OpaEvalResults"},
                        },
                        "GatherInfractions": {
                            "Type": "Task",
                            "Next": "ChoiceInfractionsExist",
                            "ResultPath": "$.GatherInfractions",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_gather_infractions.function_name,
                                "Payload.$": "$.OpaEval.OpaEvalResults"
                            },
                            "ResultSelector": {"Infractions.$": "$.Payload.Infractions"},
                        },
                        "ChoiceInfractionsExist": {
                            "Type": "Choice",
                            "Default": "ForEachInfraction",
                            "Choices": [
                                {
                                    "Variable": "$.GatherInfractions.Infractions[0]",
                                    "IsPresent": False,
                                    "Next": "NoInfractions"
                                }
                            ],
                        },
                        "NoInfractions": {
                            "Type": "Succeed",
                        },
                        "ForEachInfraction": {
                            "Type": "Map",
                            "Next": "InfractionsExist",
                            "ResultPath": "$.ForEachInfraction",
                            "ItemsPath": "$.GatherInfractions.Infractions",
                            "Parameters": {
                                "Infraction.$": "$$.Map.Item.Value",
                                "JsonInput.$": "$.JsonInput",
                                "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfnExecutionId",
                                "Metadata.$": "$.GetMetadata.Metadata",
                            },
                            "Iterator": {
                                "StartAt": "HandleInfraction",
                                "States": {
                                    "HandleInfraction": {
                                        "Type": "Task",
                                        "End": True,
                                        "ResultPath": "$.HandleInfraction",
                                        "Resource": "arn:aws:states:::lambda:invoke",
                                        "Parameters": {
                                            "FunctionName": self.lambda_handle_infraction.function_name,
                                            "Payload": {
                                                "Infraction.$": "$.Infraction",
                                                "JsonInput.$": "$.JsonInput",
                                                "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfnExecutionId",
                                                "Metadata.$": "$.Metadata",
                                            }
                                        },
                                        "ResultSelector": {"Payload.$": "$.Payload"},
                                    },
                                }
                            }
                        },
                        "InfractionsExist": {
                            "Type": "Fail",
                        }
                    }
                }
            )
        )

        self.sfn_inner_eval_engine.node.add_dependency(self.role_inner_eval_engine_sfn)

        CfnOutput(self, "InnerSfnArn", value=self.sfn_inner_eval_engine.attr_arn)

    def deploy_outer_sfn_lambdas(self):
        
        # write result reports

        self.lambda_write_result_report = aws_lambda.Function(
            self,
            "WriteResultReport",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/write_result_report"
            ),
            environment = {
                "EvalResultsTable": self.table_eval_results.table_name
            }
        )

        self.lambda_write_result_report.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "dynamodb:Query",
                ],
                resources=[
                    self.table_eval_results.table_arn,
                    f"{self.table_eval_results.table_arn}*",
                ],
            )
        )
        
    def deploy_outer_sfn(self):

        log_group_outer_eval_engine_sfn = aws_logs.LogGroup(
            self,
            "OuterEvalEngineSfnLogs",
            log_group_name=f"/aws/vendedlogs/states/OuterEvalEngineSfnLogs-{self.stack_name}",
            removal_policy=RemovalPolicy.DESTROY,
        )

        role_outer_eval_engine_sfn = aws_iam.Role(
            self,
            "OuterEvalEngineSfn",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
        )

        role_outer_eval_engine_sfn.add_to_policy(
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
                    log_group_outer_eval_engine_sfn.log_group_arn,
                    f"{log_group_outer_eval_engine_sfn.log_group_arn}*",
                ],
            )
        )
        role_outer_eval_engine_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "states:StartExecution",
                    "states:StartSyncExecution",
                ],
                resources=[self.sfn_inner_eval_engine.attr_arn],
            )
        )
        role_outer_eval_engine_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "lambda:InvokeFunction",
                ],
                resources=[self.lambda_write_result_report.function_arn],
            )
        )
        role_outer_eval_engine_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=["states:DescribeExecution", "states:StopExecution"],
                resources=["*"],
            )
        )
        role_outer_eval_engine_sfn.add_to_policy(
            aws_iam.PolicyStatement(
                actions=["events:PutTargets", "events:PutRule", "events:DescribeRule"],
                resources=[
                    f"arn:aws:events:{os.getenv('CDK_DEFAULT_REGION')}:{os.getenv('CDK_DEFAULT_ACCOUNT')}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
                    "*",
                ],
            )
        )

        self.sfn_outer_eval_engine = aws_stepfunctions.CfnStateMachine(
            self,
            "OuterEvalEngine",
            state_machine_type="EXPRESS",
            # state_machine_type="STANDARD",
            role_arn=role_outer_eval_engine_sfn.role_arn,
            logging_configuration=aws_stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                destinations=[
                    aws_stepfunctions.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=aws_stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn=log_group_outer_eval_engine_sfn.log_group_arn
                        )
                    )
                ],
                # include_execution_data=False,
                # level="ERROR",
                include_execution_data=True,
                level="ALL",
            ),
            definition_string=json.dumps(
                {
                    "StartAt": "ForEachInput",
                    "States": {
                        "ForEachInput": {
                            "Type": "Map",
                            "Next": "WriteResultReport",
                            "ResultPath": "$.ForEachInput",
                            "ItemsPath": "$.InvokedByApigw.ControlBrokerConsumerInputs.InputKeys",
                            "Parameters": {
                                "Input": {
                                    "Bucket.$": "$.InvokedByApigw.ControlBrokerConsumerInputs.Bucket",
                                    "Key.$": "$$.Map.Item.Value",
                                },
                                "ConsumerMetadata.$": "$.InvokedByApigw.ControlBrokerConsumerInputs.ConsumerMetadata",
                            },
                            "Iterator": {
                                "StartAt": "InvokeInnerEvalEngineSfn",
                                "States": {
                                    "InvokeInnerEvalEngineSfn": {
                                        "Type": "Task",
                                        "Next": "ChoiceEvalEngineStatus",
                                        "ResultPath": "$.InvokeInnerEvalEngineSfn",
                                        "Resource": "arn:aws:states:::aws-sdk:sfn:startSyncExecution",
                                        "Parameters": {
                                            "StateMachineArn": self.sfn_inner_eval_engine.attr_arn,
                                            "Input": {
                                                "Input.$": "$.Input",
                                                "OuterEvalEngineSfn": {
                                                    "ExecutionId.$": "$$.Execution.Id"
                                                },
                                            },
                                        },
                                    },
                                    "ChoiceEvalEngineStatus": {
                                        "Type": "Choice",
                                        "Default": "InnerSfnFailed",
                                        "Choices": [
                                            {
                                                "Variable": "$.InvokeInnerEvalEngineSfn.Status",
                                                "StringEquals": "SUCCEEDED",
                                                "Next": "InnerSfnSucceeded",
                                            }
                                        ],
                                    },
                                    "InnerSfnFailed": {
                                        "Type": "Pass",
                                        "End": True
                                    },
                                    "InnerSfnSucceeded": {
                                        "Type": "Pass",
                                        "End": True
                                    },
                                },
                            },
                        },
                        "WriteResultReport": {
                            "Type": "Task",
                            "End": True,
                            "ResultPath": "$.WriteResultReport",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_write_result_report.function_name,
                                "Payload": {
                                    "OuterEvalEngineSfnExecutionId.$": "$$.Execution.Id",
                                }
                            },
                            "ResultSelector": {"Payload.$": "$.Payload"},
                        },
                    },
                }
            ),
        )

        self.sfn_outer_eval_engine.node.add_dependency(role_outer_eval_engine_sfn)
