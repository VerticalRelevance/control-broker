#!/bin/bash
# Sets variables common to all the CI/CD scripts.

# Deployment environment variables
export Env="$1"
export AWS_PROFILE="$1"
export DeploymentRootName="control-broker"
export Region=$(aws configure get region)
export CompId="hub"

echo "Env: $Env, Region: $Region"

# S3 variables
export TF_VAR_resource_bucket_name="${DeploymentRootName}-${CompId}-resources-${Region}"

# AWS Credentials
export TF_VAR_AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export TF_VAR_AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export TF_VAR_AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
