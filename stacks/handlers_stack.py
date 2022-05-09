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
    aws_s3,
    aws_s3_deployment,
    aws_s3_notifications,
    aws_logs,
    aws_events,
    aws_apigatewayv2,
    # experimental
    aws_apigatewayv2_alpha,
    aws_apigatewayv2_authorizers_alpha,
    aws_apigatewayv2_integrations_alpha,
    aws_lambda_python_alpha,
    aws_s3objectlambda_alpha,
)

from components.control_broker_api import ControlBrokerApi


class HandlersStack(Stack):
    def __init__(
        self,
        *args,
        pac_framework,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)

        self.pac_framework = pac_framework

        self.pac_frameworks()
        self.output_handler()
        self.eval_engine()
        self.api = ControlBrokerApi(
            self,
            "ControlBrokerApi",
            lambda_invoked_by_apigw_eval_engine_endpoint=self.lambda_eval_engine_lambdalith,
            control_broker_results_bucket=None,
        )
        self.endpoint()

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
                block_public_policy=True,
                restrict_public_buckets=True,
            ),
            event_bridge_enabled=True
        )
    
    def output_handler(self):
        
        self.lambda_output_handler = aws_lambda.Function(
            self,
            "OutputHandler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=1024,
            code=aws_lambda.Code.from_asset(
                "./supplementary_files/handlers_stack/lambdas/output_handler"
            ),
            layers=[
                aws_lambda_python_alpha.PythonLayerVersion(self,
                    "requests",
                    entry="./supplementary_files/lambda_layers/requests",
                    compatible_runtimes=[
                        aws_lambda.Runtime.PYTHON_3_9
                    ]
                ),
            ]
            # environment={},
        )
        
        self.lambda_output_handler.role.add_to_policy(
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
        self.lambda_output_handler.role.add_to_policy(
            aws_iam.PolicyStatement(
                actions=[
                    "s3:WriteGetObjectResponse",
                ],
                resources=["*"],
            )
        )
        
        # self.bucket_raw_pac_results.add_event_notification(aws_s3.EventType.OBJECT_CREATED,
        #     aws_s3_notifications.LambdaDestination(self.lambda_output_handler),
        #     # prefix="home/myusername/*"
        # )
        
        self.access_point = aws_s3objectlambda_alpha.AccessPoint(
            self,
            "OuputHandlerCloudFormationOPA",
            bucket=self.bucket_raw_pac_results,
            handler=self.lambda_output_handler,
            access_point_name="ouput-handler-cloudformation-opa",
            # payload={
            #     "prop": "value"
            # }
        )

        CfnOutput(self, "OuputHandlerCloudFormationOPAAccessPointArn", value=self.access_point.access_point_arn)
        
    def endpoint(self):

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

        # integration - cloudformation

        lambda_invoked_by_apigw_cloudformation = aws_lambda.Function(
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
                "OutputHandlers": json.dumps([
                    {
                        "HandlerName":"CloudFormationOPA",
                        "AccessPointArn": self.access_point.access_point_arn
                    }
                ])
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

        self.api.add_api_handler(
            "CloudFormation", lambda_invoked_by_apigw_cloudformation, "/CloudFormation"
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

        CfnOutput(self, "EvalEngineLamdalithRoleArn", value=self.lambda_eval_engine_lambdalith.role.role_arn)
