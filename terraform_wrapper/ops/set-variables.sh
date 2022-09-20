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
