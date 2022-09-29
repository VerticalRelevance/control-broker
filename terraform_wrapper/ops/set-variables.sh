#!/bin/bash
# Sets variables common to all the CI/CD scripts.

# Deployment environment variables
export Env="$1"
export AWS_PROFILE="$1"
export DeploymentRootName="control-broker"
export Region=$(aws configure get region)
export CompId="hub"

echo "Env: $Env, Region: $Region"

# CDK Ops
export TF_VAR_cdk_destroy=false
export TF_VAR_cdk_source_directory="../src"
export TF_VAR_cdk_source_file_name="source.zip"
export TF_VAR_cdk_source_file_key="source/${TF_VAR_cdk_source_file_name}"

# S3 variables
export TF_VAR_resource_bucket_name="${DeploymentRootName}-${CompId}-resources"

export TF_VAR_codepipeline_pipeline_name="${DeploymentRootName}-${CompId}-pipeline-${Region}"
export TF_VAR_codepipeline_pipeline_role_name="${DeploymentRootName}-${CompId}-pipeline-role-${Region}"
export TF_VAR_codepipeline_pipeline_role_policy_name="${DeploymentRootName}-${CompId}-pipeline-role-policy-${Region}"

# CodeBuild
export TF_VAR_codebuild_project_name="${DeploymentRootName}-${CompId}-ops-${Region}"
export TF_VAR_codebuild_project_image="aws/codebuild/amazonlinux2-x86_64-standard:4.0"
export TF_VAR_codebuild_role_name="${DeploymentRootName}-${CompId}-ops-role-${Region}"
export TF_VAR_codebuild_role_policy_name="${DeploymentRootName}-${CompId}-ops-role-policy-${Region}"
export TF_VAR_codebuild_buildspec_file_name="buildspec.yml"
export TF_VAR_codebuild_cdk_target_account="615251248113"
export TF_VAR_codebuild_cdk_target_region="us-east-1"

# CloudWatch
export TF_VAR_cloudwatch_logs_group_name="${DeploymentRootName}-${CompId}-log-group-${Region}"
export TF_VAR_cloudwatch_logs_stream_name="${DeploymentRootName}-${CompId}-log-stream-${Region}"

# AWS SecretsManager Credentials
export TF_VAR_AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export TF_VAR_AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export TF_VAR_AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
