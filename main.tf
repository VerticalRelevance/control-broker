terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    bucket  = "cschneider-terraform-backend" #RER
    key     = "opa-eval-serverless/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true

    skip_metadata_api_check     = true
    skip_region_validation      = true
    skip_credentials_validation = true
  }
}
provider "aws" {
  region = local.region

  skip_get_ec2_platforms      = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
}

##################################################################
#                       locals
##################################################################

locals {
  region          = "us-east-1"
  resource_prefix = "control-broker-eval-engine"
}

data "aws_caller_identity" "i" {}

data "aws_organizations_organization" "o" {}

##################################################################
#                       Required Existing Resources
##################################################################

locals {
  repos = {
    policies = {
      name   = "opa-eval-serverless-opa-policies"
      branch = "fake-stack"
    }
    cdk = {
      name   = "opa-eval-serverless-cdk-source"
      branch = "master"
    }
  }
}

data "aws_codecommit_repository" "cdk" {
  repository_name = local.repos.cdk.name
}


##################################################################
##################################################################
#######                 root pipeline                       ######
##################################################################
##################################################################


##################################################################
#                        codebuild
##################################################################

data "aws_iam_policy_document" "codebuild_external_buildspec" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "ec2:CreateNetworkInterface",
      "ec2:DescribeDhcpOptions",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeSubnets",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeVpcs",
    ]
    resources = [
      "*",
    ]
  }
  statement {
    actions = [
      "ec2:CreateNetworkInterfacePermission"
    ]
    resources = [
      "arn:aws:ec2:*:${data.aws_caller_identity.i.id}:network-interface/*"
    ]
    condition {
      test     = "StringEquals"
      variable = "ec2:AuthorizedService"
      values = [
        "codebuild.amazonaws.com"
      ]
    }
  }
  statement {
    actions = [
      "s3:List*",
      "s3:Head*",
      "s3:Get*",
      "s3:Put*",
    ]
    resources = [
      module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn,
      "${module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn}/*",
    ]
  }
}

module "policy_codebuild_external_buildspec" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${local.resource_prefix}-codebuild_external_buildspec"
  path = "/"

  policy = data.aws_iam_policy_document.codebuild_external_buildspec.json
}

module "role_codebuild_external_buildspec" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "${local.resource_prefix}-codebuild_external_buildspec"

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "codebuild.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_codebuild_external_buildspec.arn,
  ]

}

resource "aws_codebuild_project" "external_buildspec" {
  name = "${local.resource_prefix}--codebuild_external_buildspec"
  #   build_timeout = "5"
  service_role = module.role_codebuild_external_buildspec.iam_role_arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
  }

  source {
    type = "CODEPIPELINE"
  }

  #   logs_config {
  #     cloudwatch_logs {
  #       group_name  = "log-group"
  #       stream_name = "log-stream"
  #     }
  #   }
}

##################################################################
#                        codepipeline
##################################################################

data "aws_iam_policy_document" "codepipeline_external_buildspec" {
  statement {
    actions = [
      "codecommit:CancelUploadArchive",
      "codecommit:GetBranch",
      "codecommit:GetCommit",
      "codecommit:GetRepository",
      "codecommit:GetUploadArchiveStatus",
      "codecommit:UploadArchive",
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
      "codebuild:BatchGetBuildBatches",
      "codebuild:StartBuildBatch",
    ]
    resources = [
      "*",
    ]
  }
  statement {
    actions = [
      "s3:List*",
      "s3:Head*",
      "s3:Get*",
      "s3:Put*",
    ]
    resources = [
      module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn,
      "${module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "iam:AssumeRole",
    ]
    resources = [
      "*", #FIXME
    ]
  }
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    resources = [
      module.lambda_add_buildspec.lambda_function_arn,
      module.lambda_eval_engine_wrapper.lambda_function_arn,
    ]
  }
  statement {
    actions = [
      "states:DescribeStateMachine",
      "states:StartExecution"
    ]
    resources = [
      aws_sfn_state_machine.eval_engine.arn,
    ]
  }
  statement {
    actions = [
      "states:DescribeExecution",
    ]
    resources = [
      "arn:aws:states:${local.region}:${data.aws_caller_identity.i.id}:execution:${aws_sfn_state_machine.eval_engine.name}:*"
    ]
  }
}

module "policy_codepipeline_external_buildspec" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${local.resource_prefix}-codepipeline_external_buildspec"
  path = "/"

  policy = data.aws_iam_policy_document.codepipeline_external_buildspec.json
}

module "role_codepipeline_external_buildspec" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "${local.resource_prefix}-codepipeline_external_buildspec"

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "codepipeline.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_codepipeline_external_buildspec.arn,
  ]

}

module "bucket_pipeline_artifacts_external_buildspec" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "${local.resource_prefix}-codepipeline-external-buildspec"

  # Allow deletion of non-empty bucket
  force_destroy = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_codepipeline" "external_buildspec" {
  role_arn = module.role_codepipeline_external_buildspec.iam_role_arn
  name     = "${local.resource_prefix}"
  artifact_store {
    location = module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_id
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "${local.repos.cdk.name}--${local.repos.cdk.branch}"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeCommit"
      version          = "1"
      output_artifacts = ["Repo"]

      configuration = {
        RepositoryName = local.repos.cdk.name
        BranchName     = local.repos.cdk.branch
      }
    }
  }

  stage {
    name = "AddBuildspec"

    action {
      name     = "AddBuildspec"
      category = "Invoke"
      owner    = "AWS"
      provider = "Lambda"
      version  = "1"

      input_artifacts  = ["Repo"]
      output_artifacts = ["RepoAndBuildSpec"]
      configuration = {
        FunctionName = module.lambda_add_buildspec.lambda_function_name
        UserParameters = jsonencode({
          "Buildspec" : {
            "Bucket" : aws_s3_bucket_object.buildspec.bucket,
            "Key" : aws_s3_bucket_object.buildspec.key
          }
        })
      }
    }
  }

  stage {
    name = "CDKSynth"

    action {
      name             = "CDKSynth"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["RepoAndBuildSpec"]
      output_artifacts = ["Synthed"]

      configuration = {
        ProjectName = aws_codebuild_project.external_buildspec.name
      }
    }
  }

  stage {
    name = "EvalEngine"

    action {
      name     = "EvalEngine"
      category = "Invoke"
      owner    = "AWS"
      provider = "Lambda"
      version  = "1"

      input_artifacts = ["Synthed"]
      configuration = {
        FunctionName = module.lambda_eval_engine_wrapper.lambda_function_name
        UserParameters = jsonencode({
          SynthedTemplatesBucket = module.bucket_synthed_templates.s3_bucket_id
          EvalEngineSfnArn       = aws_sfn_state_machine.eval_engine.arn
        })
      }
    }
  }
}

##################################################################
#                        misc
##################################################################

resource "aws_dynamodb_table" "eval_results" {
  name         = "${local.resource_prefix}-eval-results"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

}

module "bucket_synthed_templates" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "${local.resource_prefix}-synthed-templates"

  # Allow deletion of non-empty bucket
  force_destroy = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

module "bucket_utils" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "${local.resource_prefix}-utils"

  # Allow deletion of non-empty bucket
  force_destroy = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_object" "buildspec" {
  bucket = module.bucket_utils.s3_bucket_id
  key    = "buildspec.yaml"
  source = "./resources/buildspec/buildspec.yaml"
}


##################################################################
##################################################################
#######                     lambdas                         ######
##################################################################
##################################################################


##################################################################
#                      parse active services
##################################################################

data "aws_iam_policy_document" "lambda_parse_active_services" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:HeadObject",
    ]
    resources = [
      module.bucket_synthed_templates.s3_bucket_arn,
      "${module.bucket_synthed_templates.s3_bucket_arn}/*",
    ]
  }
}

module "lambda_parse_active_services" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.resource_prefix}-parse-active-services"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 512

  source_path = "./lambda/functions/parse-active-services"

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_parse_active_services.json
}

##################################################################
#                      opa eval - python subprocess
##################################################################

data "aws_iam_policy_document" "lambda_opa_eval_python_subprocess" {
  statement {
    actions = [
      "s3:HeadObject",
      "s3:List*",
      "s3:Get*",
    ]
    resources = [
      module.bucket_opa_policies.s3_bucket_arn,
      "${module.bucket_opa_policies.s3_bucket_arn}/*",
      module.bucket_synthed_templates.s3_bucket_arn,
      "${module.bucket_synthed_templates.s3_bucket_arn}/*",
      "*"
    ]
  }
}

module "lambda_opa_eval_python_subprocess" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.resource_prefix}-opa-eval-python-subprocess"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  # memory_size   = 1024 # TODO: power-tune
  memory_size = 10240 # TODO: power-tune

  source_path = "./lambda/functions/opa-eval/python-subprocess"

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_opa_eval_python_subprocess.json

  environment_variables = {
    OPAPolicyS3Bucket = module.bucket_opa_policies.s3_bucket_id
  }

}

##################################################################
#                     infractions feedback git - codecommit
##################################################################

data "aws_iam_policy_document" "lambda_infractions_feedback_git_codecommit" {
  statement {
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      module.bucket_synthed_templates.s3_bucket_arn,
    ]
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:HeadObject",
    ]
    resources = [
      "${module.bucket_synthed_templates.s3_bucket_arn}/*",
    ]
  }
  statement {
    not_actions = [
      "codecommit:Delete*", #FIXME
    ]
    resources = [
      data.aws_codecommit_repository.cdk.arn,
      "${data.aws_codecommit_repository.cdk.arn}/*",
      "*", #FIXME
    ]
  }
  statement {
    actions = [
      "dynamodb:Query",
    ]
    resources = [
      aws_dynamodb_table.eval_results.arn,
      "${aws_dynamodb_table.eval_results.arn}/*"
    ]
  }
}

module "lambda_infractions_feedback_git_codecommit" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.resource_prefix}-infractions-feedback-git-codecommit"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 512

  source_path = "./lambda/functions/infractions-feedback/git/codecommit"

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_infractions_feedback_git_codecommit.json

  environment_variables = {
    CdkTsSourceRepo       = local.repos.cdk.name,
    CdkTsSourceRepoBranch = local.repos.cdk.branch
  }
}

##################################################################
#                        add buildspec
##################################################################

data "aws_iam_policy_document" "lambda_add_buildspec" {
  statement {
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      module.bucket_utils.s3_bucket_arn,
      module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn,
    ]
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:HeadObject",
    ]
    resources = [
      "${module.bucket_utils.s3_bucket_arn}/*",
      "${module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "s3:PutObject",
    ]
    resources = [
      "${module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "codepipeline:PutJobSuccessResult",
      "codepipeline:PutJobFailureResult",
    ]
    resources = [
      "*"
    ]
  }
}

module "lambda_add_buildspec" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.resource_prefix}-add-buildspec"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 512

  source_path = "./lambda/functions/add-buildspec"

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_add_buildspec.json

}

##################################################################
#                      eval-engine-wrapper
##################################################################

data "aws_iam_policy_document" "lambda_eval_engine_wrapper" {
  statement {
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn,
      module.bucket_synthed_templates.s3_bucket_arn,
    ]
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:HeadObject",
    ]
    resources = [
      "${module.bucket_pipeline_artifacts_external_buildspec.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "s3:PutObject",
    ]
    resources = [
      "${module.bucket_synthed_templates.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "states:StartExecution",
      "states:StartSyncExecution",
    ]
    resources = [
      aws_sfn_state_machine.eval_engine.arn,
      "${aws_sfn_state_machine.eval_engine.arn}/*",
    ]
  }
  statement {
    actions = [
      "codepipeline:PutJobSuccessResult",
      "codepipeline:PutJobFailureResult",
    ]
    resources = [
      "*"
    ]
  }
}

module "lambda_eval_engine_wrapper" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.resource_prefix}-eval-engine-wrapper"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 512

  source_path = "./lambda/functions/eval-engine-wrapper"

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_eval_engine_wrapper.json

}


##################################################################
##################################################################
#######                       sfn                           ######
##################################################################
##################################################################


##################################################################
#                      eval engine
##################################################################

data "aws_iam_policy_document" "sfn_eval_engine" {
  statement {
    actions = [
      "logs:*",
    ]
    resources = [
      "*", #FIXME
      aws_cloudwatch_log_group.sfn_eval_engine.arn,
      "${aws_cloudwatch_log_group.sfn_eval_engine.arn}:"
    ]
  }
  statement {
    actions = [
      "states:StartExecution",
      "states:StartSyncExecution",
    ]
    resources = [
      aws_sfn_state_machine.for_each_template.arn,
    ]
  }
  statement {
    actions = [
      "states:DescribeExecution",
      "states:StopExecution"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    actions = [
      "events:PutTargets",
      "events:PutRule",
      "events:DescribeRule"
    ]
    resources = [
      "arn:aws:events:${local.region}:${data.aws_caller_identity.i.id}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
      "*"
    ]
  }
}

module "policy_sfn_eval_engine" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${local.resource_prefix}-sfn_eval_engine"
  path = "/"

  policy = data.aws_iam_policy_document.sfn_eval_engine.json
}

module "role_sfn_eval_engine" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "${local.resource_prefix}-sfn_eval_engine"

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "states.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_sfn_eval_engine.arn,
  ]

}

resource "aws_cloudwatch_log_group" "sfn_eval_engine" {
  name = "${local.resource_prefix}-sfn_eval_engine"
}

resource "aws_sfn_state_machine" "eval_engine" {
  name     = "${local.resource_prefix}-eval-engine"
  role_arn = module.role_sfn_eval_engine.iam_role_arn
  # type = "STANDARD"

  type = "EXPRESS"
  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.sfn_eval_engine.arn}:*"
    include_execution_data = true
    # level                  = "ERROR"
    level = "ALL"
  }


  definition = jsonencode({
    "StartAt" : "ForEachTemplate",
    "States" : {
      "ForEachTemplate" : {
        "Type" : "Map",
        "End" : true
        "ResultPath" : "$.ForEachTemplate",
        "ItemsPath" : "$.CFN.Keys",
        "Parameters" : {
          "Template" : {
            "Bucket.$" : "$.CFN.Bucket"
            "Key.$" : "$$.Map.Item.Value",
          }
        },
        "Iterator" : {
          "StartAt" : "TemplateToNestedSFN",
          "States" : {
            "TemplateToNestedSFN" : {
              "Type" : "Task",
              "End" : true
              "ResultPath" : "$.TemplateToNestedSFN",
              # "Resource" : "arn:aws:states:::states:startExecution.sync:2",
              "Resource" : "arn:aws:states:::aws-sdk:sfn:startSyncExecution",
              "Parameters" : {
                "StateMachineArn" : aws_sfn_state_machine.for_each_template.arn,
                # "Name":"ExecutionName"
                "Input" : {
                  "Template.$" : "$.Template"
                },
              },
            }
          }
        }

      }
    }
  })
}

##################################################################
#                      for each template
##################################################################

data "aws_iam_policy_document" "sfn_for_each_template" {
  statement {
    actions = [
      "logs:*",
    ]
    resources = [
      "*", #FIXME
      aws_cloudwatch_log_group.sfn_for_each_template.arn,
      "${aws_cloudwatch_log_group.sfn_for_each_template.arn}:*"
    ]
  }
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    resources = [
      module.lambda_parse_active_services.lambda_function_arn,
      module.lambda_opa_eval_python_subprocess.lambda_function_arn,
      module.lambda_infractions_feedback_git_codecommit.lambda_function_arn,
    ]
  }
  statement {
    actions = [
      "s3:ListObjectsV2",
      "s3:HeadObject",
      "s3:ListBuckets",
      "s3:ListBucket",
      "s3:List*",
      "s3:Get*",
    ]
    resources = [
      module.bucket_opa_policies.s3_bucket_arn,
      "${module.bucket_opa_policies.s3_bucket_arn}/*"
    ]
  }
  statement {
    actions = [
      "dynamodb:UpdateItem",
    ]
    resources = [
      aws_dynamodb_table.eval_results.arn,
      "${aws_dynamodb_table.eval_results.arn}/*"
    ]
  }
}

module "policy_sfn_for_each_template" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${local.resource_prefix}-sfn_for_each_template"
  path = "/"

  policy = data.aws_iam_policy_document.sfn_for_each_template.json
}

module "role_sfn_for_each_template" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "${local.resource_prefix}-sfn_for_each_template"

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "states.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_sfn_for_each_template.arn,
  ]

}

resource "aws_cloudwatch_log_group" "sfn_for_each_template" {
  name = "${local.resource_prefix}-sfn_for_each_template"
}

resource "aws_sfn_state_machine" "for_each_template" {
  name     = "${local.resource_prefix}-for-each-template"
  role_arn = module.role_sfn_for_each_template.iam_role_arn
  # type = "STANDARD"

  type = "EXPRESS"
  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.sfn_for_each_template.arn}:*"
    include_execution_data = true
    level                  = "ERROR"
  }


  definition = jsonencode({
    "StartAt" : "CFN",
    "States" : {
      "CFN" : {
        "Type" : "Pass",
        "Next" : "ParseActiveServices",
        "Parameters" : {
          "CFN" : {
            "Bucket.$" = "$.Template.Bucket",
            "Key.$"    = "$.Template.Key",
          }
        },
        "ResultPath" : "$"
      },
      "ParseActiveServices" : {
        "Type" : "Task",
        "Next" : "ForEachActiveSerive",
        "ResultPath" : "$.ParseActiveServices",
        "Resource" : "arn:aws:states:::lambda:invoke",
        "Parameters" : {
          "FunctionName" : module.lambda_parse_active_services.lambda_function_name,
          "Payload.$" : "$.CFN"
        },
        "ResultSelector" : {
          "Payload.$" : "$.Payload"
        }
      },
      "ForEachActiveSerive" : {
        "Type" : "Map",
        "Next" : "InfractionsFeedback",
        "ResultPath" : "$.ForEachActiveSerive",
        "ItemsPath" : "$.ParseActiveServices.Payload.ActiveServices",
        "Parameters" : {
          "ActiveService.$" : "$$.Map.Item.Value",
          "CFN.$" : "$.CFN"
        },
        "Iterator" : {
          "StartAt" : "ListPoliciesByService",
          "States" : {
            "ListPoliciesByService" : {
              "Type" : "Task",
              "Next" : "ChoicePoliciesExist",
              "ResultPath" : "$.ListPoliciesByService"
              "Resource" : "arn:aws:states:::aws-sdk:s3:listObjectsV2",
              "Parameters" : {
                "Bucket" : module.bucket_opa_policies.s3_bucket_id,
                "Prefix.$" : "$.ActiveService"
              },
            },
            "ChoicePoliciesExist" : {
              "Type" : "Choice",
              "Default" : "NoPolicies",
              "Choices" : [
                {
                  "Variable" : "$.ListPoliciesByService.Contents",
                  "IsPresent" : true,
                  "Next" : "ForEachPolicy"
                }
              ]
            },
            "NoPolicies" : {
              "Type" : "Pass",
              "End" : true
            },
            "ForEachPolicy" : {
              "Type" : "Map",
              "End" : true,
              "ResultPath" : "$.ForEachPolicy",
              "ItemsPath" : "$.ListPoliciesByService.Contents",
              "Parameters" : {
                "Policies" : {
                  "Bucket" : module.bucket_opa_policies.s3_bucket_id,
                  "Key.$" : "$$.Map.Item.Value.Key",
                },
                "CFN.$" : "$.CFN"
              },
              "Iterator" : {
                "StartAt" : "OPAEvalPythonSubprocess",
                "States" : {
                  "OPAEvalPythonSubprocess" : {
                    "Type" : "Task",
                    "Next" : "ChoiceOPAEvalIsAllowed",
                    "ResultPath" : "$.OPAEvalPythonSubprocess",
                    "Resource" : "arn:aws:states:::lambda:invoke",
                    "Parameters" : {
                      "FunctionName" : module.lambda_opa_eval_python_subprocess.lambda_function_name,
                      "Payload" : {
                        "Policies.$" : "$.Policies",
                        "CFN.$" : "$.CFN",
                      }
                    },
                    "ResultSelector" : {
                      "Payload.$" : "$.Payload"
                    }
                  },
                  "ChoiceOPAEvalIsAllowed" : {
                    "Type" : "Choice",
                    "Default" : "Deny",
                    "Choices" : [
                      {
                        "Variable" : "$.OPAEvalPythonSubprocess.Payload.OPAEvalDenyResult",
                        "StringEquals" : "False",
                        "Next" : "Allow"
                      }
                    ]
                  }
                  "Allow" : {
                    "Type" : "Pass",
                    "End" : true
                  },
                  "Deny" : {
                    "Type" : "Pass",
                    "Next" : "ForEachInfraction"
                  },
                  "ForEachInfraction" : {
                    "Type" : "Map",
                    "End" : true,
                    "ResultPath" : "$.ForEachInfraction",
                    "ItemsPath" : "$.OPAEvalPythonSubprocess.Payload.Infractions",
                    "Parameters" : {
                      "Infraction.$" : "$$.Map.Item.Value",
                      "Policies.$" : "$.Policies",
                      "CFN.$" : "$.CFN"
                    },
                    "Iterator" : {
                      "StartAt" : "WriteInfractionToDDB",
                      "States" : {
                        "WriteInfractionToDDB" : {
                          "Type" : "Task",
                          "End" : true,
                          "ResultPath" : "$.WriteEvalResultToDDB"
                          "Resource" : "arn:aws:states:::dynamodb:updateItem",
                          "ResultSelector" : {
                            "HttpStatusCode.$" : "$.SdkHttpMetadata.HttpStatusCode"
                          },
                          "Parameters" : {
                            "TableName" : aws_dynamodb_table.eval_results.name,
                            "Key" : {
                              "pk" : {
                                "S.$" : "$$.Execution.Id"
                              },
                              "sk" : {
                                "S.$" : "States.Format('{}#{}', $.CFN.Key, $.Policies.Key)"
                              }
                            },
                            "ExpressionAttributeNames" : {
                              "#allowed" : "AllowedStringBoolean",
                              "#infractions" : "Infractions"
                            },
                            "ExpressionAttributeValues" : {
                              ":allowed" : {
                                "S" : "False"
                              },
                              ":infractions" : {
                                "S.$" : "States.JsonToString($.Infraction)"
                              },
                            },
                            "UpdateExpression" : "SET #allowed=:allowed, #infractions=:infractions"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      "InfractionsFeedback" : {
        "Type" : "Task",
        "Next" : "ChoicePipelineIsHalted",
        "ResultPath" : "$.InfractionsFeedback",
        "Resource" : "arn:aws:states:::lambda:invoke",
        "Parameters" : {
          "FunctionName" : module.lambda_infractions_feedback_git_codecommit.lambda_function_name,
          "Payload" : {
            "CFN.$" : "$.CFN",
            "DynamoDB" : {
              "Table" : aws_dynamodb_table.eval_results.name,
              "Pk.$" : "$$.Execution.Id"
            }
          }
        },
        "ResultSelector" : {
          "Payload.$" : "$.Payload"
        }
      }
      "ChoicePipelineIsHalted" : {
        "Type" : "Choice"
        "Default" : "PipelineIsHalted"
        "Choices" : [
          {
            "Variable" : "$.InfractionsFeedback.Payload.InfractionsExist",
            "BooleanEquals" : false,
            "Next" : "PipelineProceeds"
          }
        ]
      }
      "PipelineProceeds" : {
        "Type" : "Succeed",
      },
      "PipelineIsHalted" : {
        "Type" : "Fail",
        "Cause" : "InfractionsExist"
      },
    }
  })
}





##################################################################
##################################################################
#######                 optional                       ######
##################################################################
##################################################################

# used to sync a repo of opa policies to s3 for testing
# but Control-Broker-Eval-Engine solution might assume they're already in S3

##################################################################
#                       repo-bucket-sync
##################################################################

# empty bucket

data "aws_iam_policy_document" "lambda_empty_bucket" {
  statement {
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      module.bucket_opa_policies.s3_bucket_arn,
    ]
  }
  statement {
    actions = [
      "s3:ListObjectsV2",
      "s3:DeleteObject",
    ]
    resources = [
      "${module.bucket_opa_policies.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "codepipeline:PutJobFailureResult",
      "codepipeline:PutJobSuccessResult",
    ]
    resources = [
      "*", # Must be *
    ]
  }
}

module "lambda_empty_bucket" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.resource_prefix}-empty-bucket"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 512

  source_path = "./lambda/functions/empty-bucket"

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_empty_bucket.json
}

# opa policies

module "bucket_opa_policies" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "${local.resource_prefix}-opa-policies"

  # Allow deletion of non-empty bucket
  force_destroy = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

module "repo_bucket_sync_opa_policies" {
  source = "./modules/repo-bucket-sync"

  repo               = local.repos.policies
  destination_bucket = module.bucket_opa_policies.s3_bucket_id

  resource_prefix                   = local.resource_prefix
  empty_bucket_lambda_function_name = module.lambda_empty_bucket.lambda_function_name
}
