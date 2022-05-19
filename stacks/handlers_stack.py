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
    # experimental
    aws_apigatewayv2_alpha,
    aws_apigatewayv2_authorizers_alpha,
    aws_apigatewayv2_integrations_alpha,
    aws_lambda_python_alpha,
    aws_s3objectlambda_alpha,
)

from constructs import Construct

from components.control_broker_api import ControlBrokerApi

from utils.mixins import SecretConfigStackMixin


class HandlersStack(Stack, SecretConfigStackMixin):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        pac_framework: str,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        self.pac_framework = pac_framework

        self.layers = {
            'requests': aws_lambda_python_alpha.PythonLayerVersion(self,
                    "requests",
                    entry="./supplementary_files/lambda_layers/requests",
                    compatible_runtimes=[
                        aws_lambda.Runtime.PYTHON_3_9
                    ]
                ),
            'aws_requests_auth':aws_lambda_python_alpha.PythonLayerVersion(
                    self,
                    "aws_requests_auth",
                    entry="./supplementary_files/lambda_layers/aws_requests_auth",
                    compatible_runtimes=[
                        aws_lambda.Runtime.PYTHON_3_9
                    ]
                ),
        }
        
        self.pac_frameworks()
        self.output_handler_event_driven()
        
        
        self.input_handler_cloudformation()
        self.input_handler_config_event()
        self.input_handler_cross_cloud_custom_auth()
        self.input_handler_terraform()
        
        self.eval_engine()
        
        self.api = ControlBrokerApi(
            self,
            "ControlBrokerApi",
            lambda_invoked_by_apigw_eval_engine_endpoint=self.lambda_eval_engine_lambdalith,
            control_broker_results_bucket=None,
        )
        
        self.add_apis()
        
    def pac_frameworks(self):
        
        # EvaluationContext - owned by Security Team
        
        self.bucket_evaluation_context = aws_s3.Bucket(
            self,
            "EvaluationContext",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )
        """
        NB: EvaluationContext will be passed back to Consumers in payload.
        """
        aws_s3_deployment.BucketDeployment(
            self,
            "EvaluationContextDeployment",
            sources=[
                aws_s3_deployment.Source.asset("./supplementary_files/handlers_stack/evaluation_context")
            ],
            destination_bucket=self.bucket_evaluation_context,
            retain_on_delete=False,
        )
        
        self.evaluation_context = {
            "Bucket": self.bucket_evaluation_context.bucket_name,
            "Key":"evaluation-context.json"
        }
        
        # opa
        
        self.bucket_pac_policies = aws_s3.Bucket(
            self,
            "PaCPolicies",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )


        aws_s3_deployment.BucketDeployment(
            self,
            "PaCPoliciesDeployment",
            sources=[
                aws_s3_deployment.Source.asset("./supplementary_files/handlers_stack/pac_frameworks")
            ],
            destination_bucket=self.bucket_pac_policies,
            retain_on_delete=False,
        )
        
        # raw results
        
        self.bucket_raw_pac_results = aws_s3.Bucket(
            self,
            "RawPaCResults",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                # block_public_policy=True,
                # restrict_public_buckets=True,
                block_public_policy=False,
                restrict_public_buckets=False,
            ),
            event_bridge_enabled=True
        )
        
        self.bucket_raw_pac_results.add_to_resource_policy(
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
                    "s3:Get*",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_raw_pac_results.bucket_arn,
                    self.bucket_raw_pac_results.arn_for_objects("*"),
                ],
            )
        )   
    
    def output_handler_event_driven(self):
        
        self.bucket_output_handler = aws_s3.Bucket(
            self,
            "OutputHandlerProcessedResults",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
            event_bridge_enabled=True
        )
        self.bucket_output_handler.add_to_resource_policy(
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
                    "s3:Get*",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_output_handler.bucket_arn,
                    self.bucket_output_handler.arn_for_objects("*"),
                ],
            )
        )   
        
        
        self.event_bus_infractions = aws_events.EventBus(
            self,
            "Infractions"
        )
        
        # debug logs
        
        self.log_group_infractions = aws_logs.LogGroup(
            self,
            "InfractionsEvents",
            retention=aws_logs.RetentionDays.ONE_DAY
        )
        
        self.rule_control_broker = aws_events.Rule(
            self,
            "ControlBroker",
            event_bus = self.event_bus_infractions,
            event_pattern=aws_events.EventPattern(
                source=["ControlBroker"]
            )
        )
        
        self.rule_control_broker.add_target(
            aws_events_targets.CloudWatchLogGroup(
                self.log_group_infractions
            )
        )
        
        # output handler - event-driven
        
        self.lambda_output_handler_opa = aws_lambda.Function(
            self,
            "OutputHandlerOPA",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/output_handlers/OPA"
            ),
            environment={
                "InfractionsEventBusName":self.event_bus_infractions.event_bus_name,
                "OutputHandlerProcessedResultsBucket":self.bucket_output_handler.bucket_name
            },
        )
        
        self.lambda_output_handler_opa.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:GetBucket",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_raw_pac_results.bucket_arn,
                    self.bucket_raw_pac_results.arn_for_objects("*"),
                ],
            )
        )
        self.lambda_output_handler_opa.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetBucket",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_output_handler.bucket_arn,
                    self.bucket_output_handler.arn_for_objects("*"),
                ],
            )
        )
        
        self.lambda_output_handler_opa.role.add_to_policy(
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
        
        self.bucket_raw_pac_results.add_event_notification(aws_s3.EventType.OBJECT_CREATED,
            aws_s3_notifications.LambdaDestination(self.lambda_output_handler_opa),
            # prefix="home/myusername/*"
        )

    def authorizer_lambda(self):

        # auth - lambda

        lambda_authorizer = aws_lambda.Function(
            self,
            "CBEndpointAuthorizer",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/apigw_authorizer"
            ),
        )

        authorizer_lambda = aws_apigatewayv2_authorizers_alpha.HttpLambdaAuthorizer(
            "CBEndpointAuthorizer",
            lambda_authorizer,
            response_types=[
                aws_apigatewayv2_authorizers_alpha.HttpLambdaResponseType.SIMPLE
            ],
            results_cache_ttl=Duration.seconds(0),
            identity_source=[
                "$request.header.Authorization",  # Authorization must be present in headers or 401, e.g. r = requests.post(url,auth = auth, ...)
            ],
        )
        
    def input_handler_cloudformation(self):

        self.bucket_cloudformation_raw_inputs = aws_s3.Bucket(
            self,
            "CloudFormationRawInputs",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )
        
        self.lambda_invoked_by_apigw_cloudformation = aws_lambda.Function(
            self,
            "InvokedByApigwCloudFormation",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/invoked_by_apigw_cloudformation"
            ),
            environment={
                "RawPaCResultsBucket": self.bucket_raw_pac_results.bucket_name,
                "OutputHandlers": json.dumps(
                    {
                        "OPA": {
                            "Bucket": self.bucket_output_handler.bucket_name
                        }
                    }
                ),
                "CloudFormationRawInputsBucket": self.bucket_cloudformation_raw_inputs.bucket_name,
            },
            layers=[
                self.layers['requests'],
                self.layers['aws_requests_auth']
            ]
        )
        
        self.lambda_invoked_by_apigw_cloudformation.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:GetObject", # required to generate presigned url for get_object ClientMethod
                ],
                resources=[
                    self.bucket_raw_pac_results.bucket_arn,
                    self.bucket_raw_pac_results.arn_for_objects("*"),
                    self.bucket_output_handler.bucket_arn,
                    self.bucket_output_handler.arn_for_objects("*"),
                ],
            )
        )
        
        self.lambda_invoked_by_apigw_cloudformation.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                ],
                resources=[
                    self.bucket_cloudformation_raw_inputs.bucket_arn,
                    self.bucket_cloudformation_raw_inputs.arn_for_objects("*"),
                ],
            )
        )
        
    def input_handler_config_event(self):
        
        self.bucket_config_events_converted_inputs = aws_s3.Bucket(
            self,
            "ConfigEventsConvertedInput",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )
        
        self.bucket_config_events_raw_inputs = aws_s3.Bucket(
            self,
            "ConfigEventsRawInput",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )
        
        self.lambda_invoked_by_apigw_config_event = aws_lambda.Function(
            self,
            "InvokedByApigwConfigEvent",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/invoked_by_apigw_config_event"
            ),
            environment={
                "RawPaCResultsBucket": self.bucket_raw_pac_results.bucket_name,
                "OutputHandlers": json.dumps(
                    {
                        "OPA": {
                            "Bucket": self.bucket_output_handler.bucket_name
                        }
                    }
                ),
                "ConfigEventsConvertedInputsBucket":self.bucket_config_events_converted_inputs.bucket_name
            },
            layers=[
                self.layers['requests'],
                self.layers['aws_requests_auth']
            ]
        )
        
        self.lambda_invoked_by_apigw_config_event.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "cloudformation:ValidateTemplate",
                    "cloudformation:DescribeType",
                ],
                resources=["*"],
            )
        )
        
        self.lambda_invoked_by_apigw_config_event.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "cloudcontrol:GetResource",
                ],
                resources=["*"],
            )
        )
        
        self.lambda_invoked_by_apigw_config_event.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:GetObject", # required to generate presigned url for get_object ClientMethod
                ],
                resources=[
                    self.bucket_raw_pac_results.bucket_arn,
                    self.bucket_raw_pac_results.arn_for_objects("*"),
                    self.bucket_output_handler.bucket_arn,
                    self.bucket_output_handler.arn_for_objects("*"),
                ],
            )
        )
        
        self.lambda_invoked_by_apigw_config_event.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                ],
                resources=[
                    self.bucket_config_events_converted_inputs.bucket_arn,
                    self.bucket_config_events_converted_inputs.arn_for_objects("*"),
                ],
            )
        )
        
        self.lambda_invoked_by_apigw_config_event.role.add_to_policy(
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
        
    def input_handler_cfn_hooks(self):
        
        self.lambda_invoked_by_apigw_cfn_hooks = aws_lambda.Function(
            self,
            "InvokedByApigwCfnHooks",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/invoked_by_apigw_cfn_hooks"
            ),
            layers=[
                self.layers['requests'],
                self.layers['aws_requests_auth']
            ]
        )
        
        self.api.add_api_handler(
            "CfnHooks", self.lambda_invoked_by_apigw_cfn_hooks, "/CfnHooks"
        )
        
    def input_handler_cross_cloud_custom_auth(self):
        
        self.bucket_cross_cloud_inputs = aws_s3.Bucket(
            self,
            "CrossCloudInputs",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )
        
        # auth
        
        lambda_authorizer_cross_cloud = aws_lambda.Function(
            self,
            "CrossCloudCustomAuthorizerLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/apigw_authorizer"
            ),
        )

        self.authorizer_lambda_cross_cloud = aws_apigatewayv2_authorizers_alpha.HttpLambdaAuthorizer(
            "CrossCloudCustomAuthorizer",
            lambda_authorizer_cross_cloud,
            response_types=[
                aws_apigatewayv2_authorizers_alpha.HttpLambdaResponseType.SIMPLE
            ],
            results_cache_ttl=Duration.seconds(0),
            identity_source=[
                "$request.header.Authorization",  # Authorization must be present in headers or 401, e.g. r = requests.post(url,auth = auth, ...)
            ],
        )
        
        # invoked by cross cloud
        
        self.lambda_invoked_by_apigw_cross_cloud = aws_lambda.Function(
            self,
            "InvokedByApigwCrossCloud",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/invoked_by_apigw_cross_cloud"
            ),
            environment={
                "RawPaCResultsBucket": self.bucket_raw_pac_results.bucket_name,
                "OutputHandlers": json.dumps(
                    {
                        "OPA": {
                            "Bucket": self.bucket_output_handler.bucket_name
                        }
                    }
                ),
                "CrossCloudInputsBucket": self.bucket_cross_cloud_inputs.bucket_name
            },
            layers=[
                self.layers['requests'],
                self.layers['aws_requests_auth']
            ]
        )
    
        self.lambda_invoked_by_apigw_cross_cloud.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                ],
                resources=[
                    self.bucket_cross_cloud_inputs.bucket_arn,
                    self.bucket_cross_cloud_inputs.arn_for_objects("*"),
                ],
            )
        )
        
        self.lambda_invoked_by_apigw_cross_cloud.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:GetObject", # required to generate presigned url for get_object ClientMethod
                ],
                resources=[
                    self.bucket_raw_pac_results.bucket_arn,
                    self.bucket_raw_pac_results.arn_for_objects("*"),
                    self.bucket_output_handler.bucket_arn,
                    self.bucket_output_handler.arn_for_objects("*"),
                ],
            )
        )
    
    def input_handler_terraform(self):
        
        self.bucket_terraform_inputs = aws_s3.Bucket(
            self,
            "TerraformInputs",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=aws_s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
        )
        
        # invoked by terraform
        
        self.lambda_invoked_by_apigw_terraform = aws_lambda.Function(
            self,
            "InvokedByApigwTerraform",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/invoked_by_apigw_terraform"
            ),
            environment={
                "RawPaCResultsBucket": self.bucket_raw_pac_results.bucket_name,
                "OutputHandlers": json.dumps(
                    {
                        "OPA": {
                            "Bucket": self.bucket_output_handler.bucket_name
                        }
                    }
                ),
                "TerraformInputsBucket": self.bucket_terraform_inputs.bucket_name
            },
            layers=[
                self.layers['requests'],
                self.layers['aws_requests_auth']
            ]
        )
    
        self.lambda_invoked_by_apigw_terraform.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                ],
                resources=[
                    self.bucket_terraform_inputs.bucket_arn,
                    self.bucket_terraform_inputs.arn_for_objects("*"),
                ],
            )
        )
        
        self.lambda_invoked_by_apigw_terraform.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:GetObject", # required to generate presigned url for get_object ClientMethod
                ],
                resources=[
                    self.bucket_raw_pac_results.bucket_arn,
                    self.bucket_raw_pac_results.arn_for_objects("*"),
                    self.bucket_output_handler.bucket_arn,
                    self.bucket_output_handler.arn_for_objects("*"),
                ],
            )
        )
        
    def eval_engine(self):

        self.lambda_eval_engine_lambdalith = aws_lambda.Function(
            self,
            "EvalEngineLambdalith",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=10240, # TODO power-tune
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/eval_engine_lambdalith"
            ),
            environment={
                "PaCFramework": self.pac_framework,
                "PaCPoliciesBucket": self.bucket_pac_policies.bucket_name,
                "EvaluationContext": json.dumps(self.evaluation_context) ,
                "RawPaCResultsBucket": self.bucket_raw_pac_results.bucket_name
            },
        )
        
        self.lambda_eval_engine_lambdalith.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:GetBucket",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_pac_policies.bucket_arn,
                    self.bucket_pac_policies.arn_for_objects("*"),
                    self.bucket_evaluation_context.bucket_arn,
                    self.bucket_evaluation_context.arn_for_objects("*"),
                    self.bucket_config_events_converted_inputs.bucket_arn,
                    self.bucket_config_events_converted_inputs.arn_for_objects("*"),
                    self.bucket_cloudformation_raw_inputs.bucket_arn,
                    self.bucket_cloudformation_raw_inputs.arn_for_objects("*"),
                    self.bucket_cross_cloud_inputs.bucket_arn,
                    self.bucket_cross_cloud_inputs.arn_for_objects("*"),
                    self.bucket_terraform_inputs.bucket_arn,
                    self.bucket_terraform_inputs.arn_for_objects("*"),
                ],
            )
        )
        
        self.lambda_eval_engine_lambdalith.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetBucket",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_raw_pac_results.bucket_arn,
                    self.bucket_raw_pac_results.arn_for_objects("*"),
                ],
            )
        )
    
    def add_apis(self):
        
        handler_url_config_event = self.api.add_api_handler(
            "ConfigEvent", self.lambda_invoked_by_apigw_config_event, "/ConfigEvent"
        )
        
        handler_url_cloudformation = self.api.add_api_handler(
            "CloudFormation", self.lambda_invoked_by_apigw_cloudformation, "/CloudFormation"
        )
        
        handler_url_cloudformation = self.api.add_api_handler(
            "CrossCloudCustomAuth",
            self.lambda_invoked_by_apigw_cross_cloud,
            "/CrossCloudCustomAuth",
            authorizer = self.authorizer_lambda_cross_cloud
        )
        
        handler_url_cloudformation = self.api.add_api_handler(
            "Terraform", self.lambda_invoked_by_apigw_terraform, "/Terraform"
        )
        