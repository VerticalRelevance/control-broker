from typing import List
from aws_cdk import (
    ArnFormat,
    RemovalPolicy,
    Stack,
    aws_synthetics,
    aws_iam,
    aws_s3,
    aws_s3_assets,
    aws_stepfunctions,
)
from utils import paths


class TestStack(Stack):
    """Canaries and any other post-deployment tests."""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        """Create a TestStack.

        :param control_broker_outer_state_machine: The outer state machine to call when invoking the control broker during tests.
        :type control_broker_outer_state_machine: aws_stepfunctions.StateMachine
        :param control_broker_principals: The principals to which we need to give S3 access for our input bucket.
        :type control_broker_principals: List[aws_iam.IPrincipal]
        """
        super().__init__(*args, **kwargs)
        CANARY_TEST_TEMPLATE_DEST = "test-templates"
        canary_bucket = aws_s3.Bucket(
            self,
            "ControlBrokerCanaryBucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        canary_execution_role = aws_iam.Role(
            self,
            "ControlBrokerConsumerRole",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[control_broker_consumer_policy],
            inline_policies={
                "CanaryLogsAndStorage": aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            sid="AllowCanaryBucketUse",
                            actions=[
                                "s3:PutObject",
                                "s3:GetBucketLocation",
                            ],
                            resources=[
                                canary_bucket.bucket_arn,
                                canary_bucket.arn_for_objects("*"),
                            ],
                        ),
                        aws_iam.PolicyStatement(
                            sid="AllowBucketListing",
                            actions=["s3:ListAllMyBuckets"],
                            resources=["*"],
                        ),
                        aws_iam.PolicyStatement(
                            sid="AllowCanaryLogging",
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=[
                                self.format_arn(
                                    resource="log-group",
                                    service="logs",
                                    resource_name="/aws/lambda/cwsyn-*",
                                    arn_format=ArnFormat.COLON_RESOURCE_NAME,
                                )
                            ],
                        ),
                        aws_iam.PolicyStatement(
                            sid="AllowCanaryMetrics",
                            actions=[
                                "cloudwatch:PutMetricData",
                            ],
                            resources=["*"],
                        ),
                    ]
                )
            },
        )
        valid_cfn_canary_code = aws_s3_assets.Asset(
            self,
            "ValidCfnCanaryCode",
            path=str(paths.LAMBDA_FUNCTIONS / "valid_cfn_canary"),
        )
        valid_cfn_canary = aws_synthetics.CfnCanary(
            self,
            "ValidCfnTemplateTest",
            code=aws_synthetics.CfnCanary.CodeProperty(
                handler="lambda_function.lambda_handler",
                s3_bucket=valid_cfn_canary_code.s3_bucket_name,
                s3_key=valid_cfn_canary_code.s3_object_key,
            ),
            start_canary_after_creation=True,
            artifact_s3_location=canary_bucket.s3_url_for_object("canary_artifacts/"),
            execution_role_arn=canary_execution_role.role_arn,
            name="validcfntemplatetest",
            schedule=aws_synthetics.CfnCanary.ScheduleProperty(
                expression="rate(1 minute)", duration_in_seconds="600"
            ),
            runtime_version="syn-python-selenium-1.2",
            run_config=aws_synthetics.CfnCanary.RunConfigProperty(
                environment_variables={
                    "CONTROL_BROKER_READABLE_INPUT_BUCKET": canary_bucket.bucket_name,
                    "CONTROL_BROKER_INPUT_PREFIX": CANARY_TEST_TEMPLATE_DEST,
                }
            ),
        )

        """
        TODO.1
        
        test that "out-of-the-box" conversion from Config Event -> cloud_control.get_resource() is working
        
        for an example ResourceType:
        
        compare the Describe__ API response of two resources of that ResourceType:
        - existingDescribedByConfig
        - newlyProvisionedPerGetResourceConvertedCloudFormation
        
        assert that for each non-read-only property, the API response is the same
        
        
        TODO.2
        
        test that "custom" conversion of resource that cloudformation.describe_type() lists as NON_PROVISIONABLE is working
        
        for an example ResourceType:
        
        compare the Describe__ API response of two resources of that ResourceType:
        - existingDescribedByConfig
        - newlyProvisionedPerDescribeTypeConvertedCloudFormation
        
        assert that for each non-read-only property, the API response is the same
        
        
        """
