from typing import List
import boto3
from aws_cdk import (
    ArnFormat,
    Stack,
    CfnOutput,
    aws_codestarconnections as codestarconnections,
    aws_iam as iam,
    pipelines as pipelines,
)
from constructs import Construct

from utils.mixins import SecretConfigStackMixin

class GitHubCDKPipelineStack(Stack, SecretConfigStackMixin):
    """Create a CDK Pipelines CodePipeline using a GitHub repo via a CodeStar Connection.

    Optionally allows using a pre-existing CodeStar Connection via a SecretsManager Secret containing
    the ARN of the CodeStar Connection.
    """

    def __init__(
        self,
        scope: Construct,
        name: str,
        github_repo_name: str,
        github_repo_owner: str,
        github_repo_branch: str,
        codestar_connection_arn_secret_id: str = None,
        additional_synth_iam_statements: List[iam.PolicyStatement] = None,
        **kwargs,
    ):
        """Initialize a CDK Pipeline stack that uses a GitHub repo for its source.

        :param scope: Scope of this stack.
        :type scope: Construct
        :param id: Unique identifier.
        :type id: str
        :param github_repo_name: Name of the repo to use for the pipeline's source stage.
        :type github_repo_name: str
        :param github_repo_owner: Owner of the repo for the pipeline's source stage.
        :type github_repo_owner: str
        :param github_repo_branch: Branch of the github repo, defaults to None
        :type github_repo_branch: str, optional
        :param codestar_connection_arn_secret_id: ID of a SecretsManager Secret
                                                  that contains the ARN to a CodeStar Connection to use to access the
                                                  GitHub repo. Useful if you already have a Connection you want to reuse.
        :type codestar_connection_arn_secret_id: str, optional
        :param additional_synth_iam_statements:   Statements to add to the CDK deployment role to allow CDK to get the
                                                  secret at codestar_connection_arn_secret_id, if specified. Defaults to None
        :type additional_synth_iam_statements: List[iam.PolicyStatement], optional
        """
        super().__init__(scope, name, **kwargs)

        # Create codestar connection to connect pipeline to git.
        # The connector name is sliced here because the max length
        # of the connection_name attribute is 32.
        # connection_name = github_repo_name[:31]
        
        
        if codestar_connection_arn_secret_id:
            secrets_client = boto3.client("secretsmanager")
            codestar_connection_arn = secrets_client.get_secret_value(
                SecretId=codestar_connection_arn_secret_id
            )["SecretString"]
        else:
            codestar_connection_arn = self.secrets.codestar_connection_arn
            # codestar_connection = codestarconnections.CfnConnection(
            #     self,
            #     connection_name,
            #     connection_name=connection_name,
            #     provider_type="GitHub",
            # )
            # codestar_connection_arn = codestar_connection.get_att(
            #     "ConnectionArn"
            # ).to_string()

        if codestar_connection_arn_secret_id:
            ssm_statement = iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=["*"],
                conditions={
                    "StringLike": {
                        "secretsmanager:SecretId": self.format_arn(
                            resource="secret",
                            service="secretsmanager",
                            resource_name=f"*{codestar_connection_arn_secret_id}*",
                            arn_format=ArnFormat.COLON_RESOURCE_NAME,
                        )
                    }
                },
            )
            if additional_synth_iam_statements is None:
                additional_synth_iam_statements = [ssm_statement]
            elif isinstance(additional_synth_iam_statements, list):
                additional_synth_iam_statements.append(ssm_statement)

        pipeline_synth_action = pipelines.ShellStep(
            "Synth",
            input=pipelines.CodePipelineSource.connection(
                f"{github_repo_owner}/{github_repo_name}",
                github_repo_branch,
                connection_arn=codestar_connection_arn,
            ),
            commands=[
                "npm install -g aws-cdk",  # Installs the cdk cli on Codebuild
                "pip install --upgrade pip",
                "pip install -r requirements.txt",  # Instructs Codebuild to install required packages
                "npx cdk synth",
            ],
            env={"PIPELINE_SYNTH": "true"}
        )

        self.pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipeline_synth_action,
            publish_assets_in_parallel=False,
            docker_enabled_for_synth=True,
        )