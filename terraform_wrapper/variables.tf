

variable "resource_bucket_name" {
  type = string
  description = "The name of the S3 bucket for supporting Control Broker deployment"
}

variable "cdk_destroy" {
  type = bool
  default = false
  description = "Determines whether CDK will deploy, or if set to true, will destroy CDK provisioned resources"
}
variable "cdk_source_directory" {
  type = string
  description = "The relative path to the CDK source directory, relative to the Terraform wrapper resources"
}
variable "cdk_source_file_name" {
  type = string
  description = "The name of the CDK source file"
}
variable "cdk_source_file_key" {
  type = string
  description = "The CDK source file S3 bucket key"
}

# Logs
variable "cloudwatch_logs_group_name" {
  type = string
  description = "The name of the CloudWatch logs group to use for the CDK deployer"
}
variable "cloudwatch_logs_stream_name" {
  type = string
  description = "The name of the CloudWatch logs group stream to use for the CDK deployer"
}

# CodePipeline
variable "codepipeline_pipeline_name" {
  type = string 
  description = "The name of the CodePipeline definition executed to perform deployments"
}
variable "codepipeline_pipeline_role_name" {
  type = string
  description = "The name of the role CodePipeline uses to perform CDK operations"
}
variable "codepipeline_pipeline_role_policy_name" {
  type = string
  description = "The name of the policy the CodePipeline role uses to define permissions"
}

# CodeBuild
variable "codebuild_project_name" {
  type = string
  description = "The name of the CodeBuild project definiton that performs CDK operations"
}
variable "codebuild_role_name" {
  type = string
  description = "The name of the role CodeBuild uses to perform CDK operations"
}
variable "codebuild_project_image" {
  type = string
  description = "The image value of the CodeBuild project definition"
  default = "aws/codebuild/amazonlinux2-x86_64-standard:4.0" # Currently only value tested
}
variable "codebuild_role_policy_name" {
  type = string
  description = "The name of the policy the CodeBuild role uses to define permissions"
}
variable "codebuild_buildspec_file_name" {
  type = string
  description = "The name of the CodeBuild buildspec local file name to include with the CodeBuild deployment definition"
}
variable "codebuild_cdk_target_account" {
  type = string
  description = "The target account for CDK to be deployed into. Currently only supports deploying to same account"
}
variable "codebuild_cdk_target_region" {
  type = string
  description = "The target region for the CDK app to be deployed into"
}

# Credentials
variable "AWS_ACCESS_KEY_ID" {
  type = string
  sensitive = true
}
variable "AWS_SECRET_ACCESS_KEY" {
  type = string
  sensitive = true
}
variable "AWS_SESSION_TOKEN" {
  type = string
  sensitive = true
}