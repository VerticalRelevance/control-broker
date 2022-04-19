import boto3
from aws_cdk import (
    ArnFormat,
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codestarconnections as codestarconnections,
    aws_iam as iam,
    pipelines as pipelines,
)


class GitHubCDKPipelineStack(Stack):
    """
    If you want to use an existing CodeStar connection for the source stage, specify its arn with
    codestar_connection_arn

    additional_synth_iam_statements are added to the synth stage role"""

    def __init__(
        self,
        scope,
        id,
        github_repo_name,
        github_repo_owner,
        github_repo_branch,
        codestar_connection_arn_secret_id=None,
        additional_synth_iam_statements=None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # Create codestar connection to connect pipeline to git.
        # The connector name is sliced here because the max length
        # of the connection_name attribute is 32.
        connection_name = github_repo_name[:31]
        if codestar_connection_arn_secret_id:
            secrets_client = boto3.client("secretsmanager")
            codestar_connection_arn = secrets_client.get_secret_value(
                SecretId=codestar_connection_arn_secret_id
            )["SecretString"]
        else:
            codestar_connection = codestarconnections.CfnConnection(
                self,
                connection_name,
                connection_name=connection_name,
                provider_type="GitHub",
            )
            codestar_connection_arn = codestar_connection.get_att(
                "ConnectionArn"
            ).to_string()

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
        )

        self.pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipeline_synth_action,
        )