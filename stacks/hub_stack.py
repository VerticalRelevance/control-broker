import os, json
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
    aws_sns,
    aws_ec2,
    aws_s3,
    aws_s3_deployment,
    aws_s3_notifications,
    aws_logs,
    aws_events,
    aws_events_targets,
    aws_apigateway,
    aws_s3objectlambda,
    aws_lambda_event_sources,
    aws_sns_subscriptions,
    # experimental
    aws_apigatewayv2_alpha,
    aws_apigatewayv2_authorizers_alpha,
    aws_apigatewayv2_integrations_alpha,
    aws_lambda_python_alpha,
    aws_s3objectlambda_alpha,
)

from constructs import Construct

from utils.mixins import re_search

class HubStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        pac_framework: str,
        config_sns_topic:str,
        is_dev:bool,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        self.pac_framework = pac_framework
        self.is_dev=is_dev
        
        
        self.dev_config={
            True:{
                'SQS':{
                    'BatchSize':1
                }
            },
            False:{
                'SQS':{
                    'BatchSize':10
                }
            },
        }
        
        pac_path='./supplementary_files/pac_frameworks/cfn-guard/AWS/ConfigEvent'
        self.resource_types_subject_to_pac=[]
        for root, dirs, files in os.walk(pac_path):
            for filename in files:
                self.resource_types_subject_to_pac.append(re_search('(AWS::\w+::\w+)\.?.+\.guard',filename))
        
        print(self.resource_types_subject_to_pac)
        
        self.topic_config=aws_sns.Topic.from_topic_arn(self,"Config",
            f'arn:aws:sns:{os.getenv("CDK_DEFAULT_REGION")}:{os.getenv("CDK_DEFAULT_ACCOUNT")}:{config_sns_topic}'
        )
        
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
        
        self.queue_subscribed_to_config_topic=aws_sqs.Queue(self,"SubscribedToConfigTopic")
        
        self.topic_config.add_subscription(aws_sns_subscriptions.SqsSubscription(self.queue_subscribed_to_config_topic))
        
        self.event_source_sqs = aws_lambda_event_sources.SqsEventSource(self.queue_subscribed_to_config_topic,
            batch_size=self.dev_config[self.is_dev]['SQS']['BatchSize'], 
            # max_batching_window=Duration.minutes(5),
        )
        
        self.pac_frameworks()
        self.main()
    
    def pac_frameworks(self):
        
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
                aws_s3_deployment.Source.asset("./supplementary_files/pac_frameworks/cfn-guard")
            ],
            destination_bucket=self.bucket_pac_policies,
            retain_on_delete=False,
        )
        
    def main(self):
        
        self.vpc = aws_ec2.Vpc(self, "VpcHub",
            cidr="10.0.0.0/16"
        )
        
        self.sg=aws_ec2.SecurityGroup(self, "SgHub",
            vpc=self.vpc
        )
        
        self.sg.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.all_traffic()
        )
        
        self.endpoint=aws_ec2.InterfaceVpcEndpoint(self, "EndpointHub",
            vpc=self.vpc,
            service=aws_ec2.InterfaceVpcEndpointService(f'com.amazonaws.{os.getenv("CDK_DEFAULT_REGION")}.execute-api', 443),
            security_groups=[
                self.sg
            ],
            private_dns_enabled=True
        )
        
        self.log_group_api = aws_logs.LogGroup(
            self,
            "ApiControlBroker",
            retention=aws_logs.RetentionDays.ONE_DAY
        )
        
        self.api_cb = aws_apigateway.RestApi(self, "ApiCb",
            rest_api_name="ControlBroker",
            endpoint_configuration=aws_apigateway.EndpointConfiguration(
                types=[aws_apigateway.EndpointType.PRIVATE],
                vpc_endpoints=[
                    self.endpoint
                ]
            ),
            deploy_options=aws_apigateway.StageOptions(
                access_log_destination=aws_apigateway.LogGroupLogDestination(self.log_group_api),
                logging_level=aws_apigateway.MethodLoggingLevel.INFO
            ),
            policy=aws_iam.PolicyDocument(
                statements=[
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        actions=["execute-api:Invoke"],
                        principals=[aws_iam.AnyPrincipal()],
                        resources=["execute-api:/*"]
                    ),
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.DENY,
                        actions=["execute-api:Invoke"],
                        principals=[aws_iam.AnyPrincipal()],
                        resources=["execute-api:/*"],
                        conditions={
                            "StringNotEquals": {
                               "aws:SourceVpc": self.vpc.vpc_id
                            }
                        }
                    ),
                ]
            )
        )
        
        #
        
        self.lambda_put_asff = aws_lambda.Function(
            self,
            "PutAsff",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(20),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/put_asff"
            ),
            environment={
            },
        )
        
        self.lambda_put_asff.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "securityhub:BatchImportFindings",
                ],
                resources=[
                    "*",
                ],
            )
        )
        
        #
        
        self.lambda_output_handler = aws_lambda.Function(
            self,
            "OutputHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(20),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/output_handlers/cfn-guard"
            ),
            environment={
                'PutAssfLambda':self.lambda_put_asff.function_name
            },
        )
        
        self.lambda_output_handler.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "lambda:InvokeFunction",
                ],
                resources=[
                    self.lambda_put_asff.function_arn,
                    "*",
                ],
            )
        )
        
        #
        
        self.lambda_eval_engine = aws_lambda.Function(
            self,
            "EvalEngine",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(20),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/eval_engine"
            ),
            environment={
                "RulesS3":json.dumps({
                    "Bucket":self.bucket_pac_policies.bucket_name,
                    "Prefix":"AWS/ConfigEvent"
                }),
                'OutputHandlerLambda':self.lambda_output_handler.function_name
            },
        )
        
        self.lambda_eval_engine.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:Get*",
                    "s3:List*",
                ],
                resources=[
                    self.bucket_pac_policies.bucket_arn,
                    self.bucket_pac_policies.arn_for_objects("*"),
                    "*",
                ],
            )
        )
        self.lambda_eval_engine.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "lambda:InvokeFunction",
                ],
                resources=[
                    self.lambda_output_handler.function_arn,
                    "*",
                ],
            )
        )
        
        #
        
        self.lambda_invoked_by_apigw = aws_lambda.Function(
            self,
            "InvokedByApigw",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(20),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/invoked_by_apigw"
            ),
            environment={
                'EvalEngineLambda':self.lambda_eval_engine.function_name
            },
        )
        
        self.lambda_invoked_by_apigw.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "lambda:InvokeFunction",
                ],
                resources=[
                    self.lambda_eval_engine.function_arn,
                    "*",
                ],
            )
        )
        
        self.api_cb.root.add_method("POST", aws_apigateway.LambdaIntegration(self.lambda_invoked_by_apigw))
        
        #
        
        self.lambda_invoked_by_sqs = aws_lambda.Function(
            self,
            "InvokedBySqs",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(20),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/lambdas/invoked_by_sqs"
            ),
            environment={
                "ResourceTypesSubjectToPac": json.dumps(self.resource_types_subject_to_pac),
                "QueueUrl": self.queue_subscribed_to_config_topic.queue_url,
                "ControlBrokerApigwEndpointUrl": self.api_cb.url,
                # "VPCEndpointDNSNames":json.dumps(self.endpoint.vpc_endpoint_dns_entries)
            },
            vpc=self.vpc,
            security_groups=[
                self.sg
            ],
            vpc_subnets=self.vpc.private_subnets[0],
            layers=[
                self.layers['requests'],
                self.layers['aws_requests_auth']
            ]
        )
        
        self.lambda_invoked_by_sqs.role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))

        self.lambda_invoked_by_sqs.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "sqs:*",
                ],
                resources=[
                    "*",
                    self.queue_subscribed_to_config_topic.queue_arn,
                ],
            )
        )
        
        self.lambda_invoked_by_sqs.add_event_source(self.event_source_sqs)
