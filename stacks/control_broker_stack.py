import os
import json
from typing import List, Sequence

from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    SecretValue,
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

from utils.mixins import SecretConfigStackMixin


class ControlBrokerStack(Stack, SecretConfigStackMixin):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        """A full Control Broker installation.

        :param scope:
        :type scope: Construct
        :param construct_id:
        :type construct_id: str
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

        self.deploy_utils()
        self.s3_deploy_local_assets()
        self.deploy_inner_sfn_lambdas()
        self.deploy_inner_sfn()
        self.deploy_outer_sfn_lambdas()
        self.deploy_outer_sfn()

        self.Input_reader_roles: List[aws_iam.Role] = [
            self.lambda_evaluate_cloudformation_by_opa.role,
            self.lambda_pac_evaluation_router.role,
        ]

        self.outer_eval_engine_state_machine = (
            aws_stepfunctions.StateMachine.from_state_machine_arn(
                self,
                "OuterEvalEngineStateMachineObj",
                self.sfn_outer_eval_engine.attr_arn,
            )
        )

        self.eval_results_reports_bucket = aws_s3.Bucket.from_bucket_name(
            self,
            "EvalResultsReportsBucketObj",
            self.bucket_eval_results_reports.bucket_name,
        )

        CfnOutput(
            self,
            "InputReaderArns",
            value=json.dumps([r.role_arn for r in self.Input_reader_roles]),
        )

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

        # converted inputs

        self.bucket_converted_inputs = aws_s3.Bucket(
            self,
            "ConvertedInputs",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )

        # results reports

        self.bucket_eval_results_reports = aws_s3.Bucket(
            self,
            "EvalResultsReports",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )

        self.bucket_eval_results_reports.add_to_resource_policy(
            aws_iam.PolicyStatement(
                principals=[
                    aws_iam.AnyPrincipal().with_conditions(
                        {
                            "ForAnyValue:StringLike": {
                                "aws:PrincipalOrgPaths": [self.secrets.allowed_org_path]
                            }
                        }
                    )
                ],
                actions=[
                    "s3:GetObject",
                ],
                resources=[
                    self.bucket_eval_results_reports.bucket_arn,
                    self.bucket_eval_results_reports.arn_for_objects("*"),
                ],
            )
        )

    def s3_deploy_local_assets(self):

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

        # pac evaluation router

        self.lambda_pac_evaluation_router = aws_lambda.Function(
            self,
            "PaCEvaluationRouter",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=10240,  # todo power-tune
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/pac_evaluation_router"
            ),
            environment={
                "PaCBucketRouting": json.dumps(
                    {"OPA": self.bucket_opa_policies.bucket_name}
                ),
                "ConvertedInputsBucket": self.bucket_converted_inputs.bucket_name,
            },
        )

        self.lambda_pac_evaluation_router.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "cloudformation:ValidateTemplate",
                    "cloudformation:DescribeType",
                    "cloudformation:Get*",  # FIXME
                    "cloudformation:Describe*",  # FIXME
                ],
                resources=["*"],
            )
        )
        self.lambda_pac_evaluation_router.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "cloudcontrol:GetResource",
                    "cloudcontrol:*",  # FIXME
                ],
                resources=["*"],
            )
        )
        self.lambda_pac_evaluation_router.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                ],
                resources=[
                    self.bucket_converted_inputs.arn_for_objects("*"),
                ],
            )
        )
        self.lambda_pac_evaluation_router.role.add_to_policy(
            aws_iam.PolicyStatement(
                # Get*, List* for all services with a cloudcontrol provisionable resource
                # required fro cloudcontrol.get_resource()
                actions=[
                    "acmpca:Get*",
                    "acmpca:List*",
                    "aps:Get*",
                    "aps:List*",
                    "accessanalyzer:Get*",
                    "accessanalyzer:List*",
                    "amplify:Get*",
                    "amplify:List*",
                    "amplifyuibuilder:Get*",
                    "amplifyuibuilder:List*",
                    "apigateway:Get*",
                    "apigateway:List*",
                    "appflow:Get*",
                    "appflow:List*",
                    "appintegrations:Get*",
                    "appintegrations:List*",
                    "apprunner:Get*",
                    "apprunner:List*",
                    "appstream:Get*",
                    "appstream:List*",
                    "appsync:Get*",
                    "appsync:List*",
                    "applicationinsights:Get*",
                    "applicationinsights:List*",
                    "athena:Get*",
                    "athena:List*",
                    "auditmanager:Get*",
                    "auditmanager:List*",
                    "autoscaling:Get*",
                    "autoscaling:List*",
                    "backup:Get*",
                    "backup:List*",
                    "batch:Get*",
                    "batch:List*",
                    "budgets:Get*",
                    "budgets:List*",
                    "ce:Get*",
                    "ce:List*",
                    "cur:Get*",
                    "cur:List*",
                    "cassandra:Get*",
                    "cassandra:List*",
                    "certificatemanager:Get*",
                    "certificatemanager:List*",
                    "chatbot:Get*",
                    "chatbot:List*",
                    "cloudformation:Get*",
                    "cloudformation:List*",
                    "cloudfront:Get*",
                    "cloudfront:List*",
                    "cloudtrail:Get*",
                    "cloudtrail:List*",
                    "cloudwatch:Get*",
                    "cloudwatch:List*",
                    "codeartifact:Get*",
                    "codeartifact:List*",
                    "codeguruprofiler:Get*",
                    "codeguruprofiler:List*",
                    "codegurureviewer:Get*",
                    "codegurureviewer:List*",
                    "codestarconnections:Get*",
                    "codestarconnections:List*",
                    "codestarnotifications:Get*",
                    "codestarnotifications:List*",
                    "config:Get*",
                    "config:List*",
                    "connect:Get*",
                    "connect:List*",
                    "customerprofiles:Get*",
                    "customerprofiles:List*",
                    "databrew:Get*",
                    "databrew:List*",
                    "datasync:Get*",
                    "datasync:List*",
                    "detective:Get*",
                    "detective:List*",
                    "devopsguru:Get*",
                    "devopsguru:List*",
                    "devicefarm:Get*",
                    "devicefarm:List*",
                    "dynamodb:Get*",
                    "dynamodb:List*",
                    "ec2:Get*",
                    "ec2:List*",
                    "ecr:Get*",
                    "ecr:List*",
                    "ecs:Get*",
                    "ecs:List*",
                    "efs:Get*",
                    "efs:List*",
                    "eks:Get*",
                    "eks:List*",
                    "emr:Get*",
                    "emr:List*",
                    "emrcontainers:Get*",
                    "emrcontainers:List*",
                    "elasticache:Get*",
                    "elasticache:List*",
                    "elasticloadbalancingv2:Get*",
                    "elasticloadbalancingv2:List*",
                    "eventschemas:Get*",
                    "eventschemas:List*",
                    "events:Get*",
                    "events:List*",
                    "evidently:Get*",
                    "evidently:List*",
                    "fis:Get*",
                    "fis:List*",
                    "fms:Get*",
                    "fms:List*",
                    "finspace:Get*",
                    "finspace:List*",
                    "forecast:Get*",
                    "forecast:List*",
                    "frauddetector:Get*",
                    "frauddetector:List*",
                    "gamelift:Get*",
                    "gamelift:List*",
                    "globalaccelerator:Get*",
                    "globalaccelerator:List*",
                    "glue:Get*",
                    "glue:List*",
                    "greengrassv2:Get*",
                    "greengrassv2:List*",
                    "groundstation:Get*",
                    "groundstation:List*",
                    "healthlake:Get*",
                    "healthlake:List*",
                    "iam:Get*",
                    "iam:List*",
                    "ivs:Get*",
                    "ivs:List*",
                    "imagebuilder:Get*",
                    "imagebuilder:List*",
                    "inspector:Get*",
                    "inspector:List*",
                    "inspectorv2:Get*",
                    "inspectorv2:List*",
                    "iot:Get*",
                    "iot:List*",
                    "iotanalytics:Get*",
                    "iotanalytics:List*",
                    "iotcoredeviceadvisor:Get*",
                    "iotcoredeviceadvisor:List*",
                    "iotevents:Get*",
                    "iotevents:List*",
                    "iotfleethub:Get*",
                    "iotfleethub:List*",
                    "iotsitewise:Get*",
                    "iotsitewise:List*",
                    "iotwireless:Get*",
                    "iotwireless:List*",
                    "kms:Get*",
                    "kms:List*",
                    "kafkaconnect:Get*",
                    "kafkaconnect:List*",
                    "kendra:Get*",
                    "kendra:List*",
                    "kinesis:Get*",
                    "kinesis:List*",
                    "kinesisfirehose:Get*",
                    "kinesisfirehose:List*",
                    "kinesisvideo:Get*",
                    "kinesisvideo:List*",
                    "lambda:Get*",
                    "lambda:List*",
                    "lex:Get*",
                    "lex:List*",
                    "licensemanager:Get*",
                    "licensemanager:List*",
                    "lightsail:Get*",
                    "lightsail:List*",
                    "location:Get*",
                    "location:List*",
                    "logs:Get*",
                    "logs:List*",
                    "lookoutequipment:Get*",
                    "lookoutequipment:List*",
                    "lookoutmetrics:Get*",
                    "lookoutmetrics:List*",
                    "lookoutvision:Get*",
                    "lookoutvision:List*",
                    "msk:Get*",
                    "msk:List*",
                    "mwaa:Get*",
                    "mwaa:List*",
                    "macie:Get*",
                    "macie:List*",
                    "mediaconnect:Get*",
                    "mediaconnect:List*",
                    "mediapackage:Get*",
                    "mediapackage:List*",
                    "memorydb:Get*",
                    "memorydb:List*",
                    "networkfirewall:Get*",
                    "networkfirewall:List*",
                    "networkmanager:Get*",
                    "networkmanager:List*",
                    "nimblestudio:Get*",
                    "nimblestudio:List*",
                    "opensearchservice:Get*",
                    "opensearchservice:List*",
                    "opsworkscm:Get*",
                    "opsworkscm:List*",
                    "panorama:Get*",
                    "panorama:List*",
                    "personalize:Get*",
                    "personalize:List*",
                    "pinpoint:Get*",
                    "pinpoint:List*",
                    "qldb:Get*",
                    "qldb:List*",
                    "quicksight:Get*",
                    "quicksight:List*",
                    "rds:Get*",
                    "rds:List*",
                    "rum:Get*",
                    "rum:List*",
                    "redshift:Get*",
                    "redshift:List*",
                    "refactorspaces:Get*",
                    "refactorspaces:List*",
                    "rekognition:Get*",
                    "rekognition:List*",
                    "resiliencehub:Get*",
                    "resiliencehub:List*",
                    "resourcegroups:Get*",
                    "resourcegroups:List*",
                    "robomaker:Get*",
                    "robomaker:List*",
                    "route53:Get*",
                    "route53:List*",
                    "route53recoverycontrol:Get*",
                    "route53recoverycontrol:List*",
                    "route53recoveryreadiness:Get*",
                    "route53recoveryreadiness:List*",
                    "route53resolver:Get*",
                    "route53resolver:List*",
                    "s3:Get*",
                    "s3:List*",
                    "s3objectlambda:Get*",
                    "s3objectlambda:List*",
                    "s3outposts:Get*",
                    "s3outposts:List*",
                    "ses:Get*",
                    "ses:List*",
                    "sqs:Get*",
                    "sqs:List*",
                    "ssm:Get*",
                    "ssm:List*",
                    "ssmcontacts:Get*",
                    "ssmcontacts:List*",
                    "ssmincidents:Get*",
                    "ssmincidents:List*",
                    "sso:Get*",
                    "sso:List*",
                    "sagemaker:Get*",
                    "sagemaker:List*",
                    "servicecatalog:Get*",
                    "servicecatalog:List*",
                    "servicecatalogappregistry:Get*",
                    "servicecatalogappregistry:List*",
                    "signer:Get*",
                    "signer:List*",
                    "stepfunctions:Get*",
                    "stepfunctions:List*",
                    "synthetics:Get*",
                    "synthetics:List*",
                    "timestream:Get*",
                    "timestream:List*",
                    "transfer:Get*",
                    "transfer:List*",
                    "wafv2:Get*",
                    "wafv2:List*",
                    "wisdom:Get*",
                    "wisdom:List*",
                    "workspaces:Get*",
                    "workspaces:List*",
                    "xray:Get*",
                    "xray:List*",
                ],
                resources=["*"],
            )
        )

        # InputType CloudFormation - PaCFramework OPA - PythonSubprocess

        self.lambda_evaluate_cloudformation_by_opa = aws_lambda.Function(
            self,
            "EvaluateCloudFormationTemplateByOPAPythonSubprocess",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=10240,  # todo power-tune
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/pac_evaluation/input_type_cloudformation/pac_framework_opa/python_subprocess"
            ),
        )

        self.lambda_evaluate_cloudformation_by_opa.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:HeadObject",
                    "s3:GetObject",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_opa_policies.bucket_arn,
                    self.bucket_opa_policies.arn_for_objects("*"),
                    self.bucket_converted_inputs.bucket_arn,
                    self.bucket_converted_inputs.arn_for_objects("*"),
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
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/gather_infractions"
            ),
        )

        # handle infraction

        self.lambda_handle_infraction = aws_lambda.Function(
            self,
            "HandleInfraction",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/handle_infraction"
            ),
            environment={
                "TableName": self.table_eval_results.table_name,
                "EventBusName": self.event_bus_infractions.event_bus_name,
            },
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
                    self.lambda_pac_evaluation_router.function_arn,
                    self.lambda_evaluate_cloudformation_by_opa.function_arn,
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
                level="ALL",
            ),
            definition_string=json.dumps(
                {
                    "StartAt": "PaCEvaluationRouter",
                    "States": {
                        "PaCEvaluationRouter": {
                            "Type": "Task",
                            "Next": "ChoicePaCEvaluationRouting",
                            "ResultPath": "$.PaCEvaluationRouter",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_pac_evaluation_router.function_name,
                                "Payload.$": "$",
                            },
                            "ResultSelector": {"Routing.$": "$.Payload.Routing"},
                        },
                        "ChoicePaCEvaluationRouting": {
                            "Type": "Choice",
                            "Default": "NoValidRoute",
                            "Choices": [
                                {
                                    "Variable": "$.PaCEvaluationRouter.Routing.InvokingSfnNextState",
                                    "StringEquals": "EvaluateCloudFormationTemplateByOPA",
                                    "Next": "EvaluateCloudFormationTemplateByOPA",
                                }
                            ],
                        },
                        "NoValidRoute": {
                            "Type": "Fail",
                        },
                        "EvaluateCloudFormationTemplateByOPA": {
                            "Type": "Task",
                            "Next": "GatherInfractions",
                            "ResultPath": "$.EvaluateCloudFormationTemplateByOPA",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_evaluate_cloudformation_by_opa.function_name,
                                "Payload": {
                                    "JsonInput": {
                                        "Bucket.$": "$.PaCEvaluationRouter.Routing.ModifiedInput.Bucket",
                                        "Key.$": "$.PaCEvaluationRouter.Routing.ModifiedInput.Key",
                                    },
                                    "PaC": {
                                        "Bucket.$": "$.PaCEvaluationRouter.Routing.PaC.Bucket"
                                    },
                                },
                            },
                            "ResultSelector": {
                                "Results.$": "$.Payload.EvaluateCloudFormationTemplateByOPAResults"
                            },
                        },
                        "GatherInfractions": {
                            "Type": "Task",
                            "Next": "ChoiceInfractionsExist",
                            "ResultPath": "$.GatherInfractions",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_gather_infractions.function_name,
                                "Payload.$": "$.EvaluateCloudFormationTemplateByOPA.Results",
                            },
                            "ResultSelector": {
                                "Infractions.$": "$.Payload.Infractions"
                            },
                        },
                        "ChoiceInfractionsExist": {
                            "Type": "Choice",
                            "Default": "ForEachInfraction",
                            "Choices": [
                                {
                                    "Variable": "$.GatherInfractions.Infractions[0]",
                                    "IsPresent": False,
                                    "Next": "NoInfractions",
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
                                "JsonInput": {
                                    "Bucket.$": "$.PaCEvaluationRouter.Routing.ModifiedInput.Bucket",
                                    "Key.$": "$.PaCEvaluationRouter.Routing.ModifiedInput.Key",
                                },
                                "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfnExecutionId",
                                "ConsumerMetadata.$": "$.InvokedByApigw.ControlBrokerConsumerInputs.ConsumerMetadata",
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
                                                "JsonInput.$":"$.JsonInput",
                                                "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfnExecutionId",
                                                "ConsumerMetadata.$": "$.ConsumerMetadata",
                                            },
                                        },
                                        "ResultSelector": {"Payload.$": "$.Payload"},
                                    },
                                },
                            },
                        },
                        "InfractionsExist": {
                            "Type": "Fail",
                        },
                    },
                }
            ),
        )

        self.sfn_inner_eval_engine.node.add_dependency(self.role_inner_eval_engine_sfn)

        # CfnOutput(self, "InnerSfnArn", value=self.sfn_inner_eval_engine.attr_arn)

    def deploy_outer_sfn_lambdas(self):

        # write results report

        self.lambda_write_results_report = aws_lambda.Function(
            self,
            "WriteResultsReport",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/write_results_report"
            ),
            environment={"EvalResultsTable": self.table_eval_results.table_name},
        )

        self.lambda_write_results_report.role.add_to_policy(
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
        self.lambda_write_results_report.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:List*",
                ],
                resources=[self.bucket_eval_results_reports.bucket_arn],
            )
        )
        self.lambda_write_results_report.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                ],
                resources=[
                    self.bucket_eval_results_reports.arn_for_objects("*"),
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
                resources=[self.lambda_write_results_report.function_arn],
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
                            "Next": "WriteResultsReport",
                            "ResultPath": "$.ForEachInput",
                            "ItemsPath": "$.InvokedByApigw.ControlBrokerConsumerInputs.InputKeys",
                            "Parameters": {
                                "InvokedByApigw.$": "$.InvokedByApigw",
                                "ControlBrokerConsumerInputKey.$": "$$.Map.Item.Value",
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
                                                "ControlBrokerConsumerInputKey.$": "$.ControlBrokerConsumerInputKey",
                                                "ControlBrokerConsumerInputs.$": "$.InvokedByApigw.ControlBrokerConsumerInputs",
                                                "OuterEvalEngineSfnExecutionId.$": "$$.Execution.Id",
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
                                    "InnerSfnFailed": {"Type": "Pass", "End": True},
                                    "InnerSfnSucceeded": {"Type": "Pass", "End": True},
                                },
                            },
                        },
                        "WriteResultsReport": {
                            "Type": "Task",
                            "End": True,
                            "ResultPath": "$.WriteResultReport",
                            "Resource": "arn:aws:states:::lambda:invoke",
                            "Parameters": {
                                "FunctionName": self.lambda_write_results_report.function_name,
                                "Payload": {
                                    "OuterEvalEngineSfnExecutionId.$": "$$.Execution.Id",
                                    "ResultsReportS3Uri.$": "$.ResultsReportS3Uri",
                                    "ForEachInput.$": "$.ForEachInput",
                                },
                            },
                            "ResultSelector": {"Payload.$": "$.Payload"},
                        },
                    },
                }
            ),
        )

        self.sfn_outer_eval_engine.node.add_dependency(role_outer_eval_engine_sfn)
