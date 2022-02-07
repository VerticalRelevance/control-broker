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
  azs             = formatlist("${local.region}%s", ["a", "b", "c"])
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
      branch = "master"
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

data "aws_iam_policy_document" "eb_can_log" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:PutLogEventsBatch",
    ]

    resources = ["arn:aws:logs:*"]

    principals {
      identifiers = ["events.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_cloudwatch_log_resource_policy" "eb_can_log" { # not attached to any resources
  policy_document = data.aws_iam_policy_document.eb_can_log.json
  policy_name     = "eb_can_log"
}

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

##################################################################
#                         ExampleCICDPipeline
##################################################################

# ssm
locals {
  ssm_parameter_name_for_cfn_template_name = "/${local.resource_prefix}/${local.repos.cdk.name}/CfnTemplateName"
}

# s3

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

resource "aws_s3_bucket_notification" "eval" {
  bucket      = module.bucket_synthed_templates.s3_bucket_id
  eventbridge = true
}

module "bucket_pipeline_artifacts_eval" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "${local.resource_prefix}-codepipeline-artifacts-eval"

  # Allow deletion of non-empty bucket
  force_destroy = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# codebuild

data "aws_iam_policy_document" "codebuild" {
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
      module.bucket_pipeline_artifacts_eval.s3_bucket_arn,
      "${module.bucket_pipeline_artifacts_eval.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "s3:List*",
      "s3:Head*",
      "s3:PutObject",
    ]
    resources = [
      module.bucket_synthed_templates.s3_bucket_arn,
      "${module.bucket_synthed_templates.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "ssm:PutParameter",
    ]
    resources = [
      "arn:aws:ssm:${local.region}:${data.aws_caller_identity.i.id}:parameter${local.ssm_parameter_name_for_cfn_template_name}"
    ]
  }
}

module "policy_codebuild" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${local.resource_prefix}-codebuild"
  path = "/"

  policy = data.aws_iam_policy_document.codebuild.json
}

module "role_codebuild" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "${local.resource_prefix}-codebuild"

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "codebuild.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_codebuild.arn,
  ]

}

resource "aws_codebuild_project" "eval" {
  name = "${local.resource_prefix}--eval"
  #   build_timeout = "5"
  service_role = module.role_codebuild.iam_role_arn

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

# codepipeline

data "aws_iam_policy_document" "codepipeline_eval" {
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
      module.bucket_pipeline_artifacts_eval.s3_bucket_arn,
      "${module.bucket_pipeline_artifacts_eval.s3_bucket_arn}/*",
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

module "policy_codepipeline_eval" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${local.resource_prefix}-codepipeline-eval"
  path = "/"

  policy = data.aws_iam_policy_document.codepipeline_eval.json
}

module "role_codepipeline_eval" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "${local.resource_prefix}-codepipeline_eval"

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "codepipeline.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_codepipeline_eval.arn,
  ]

}

locals {
  eval_pipeline_name = "${local.resource_prefix}--eval" # avoid cycle
}

resource "aws_codepipeline" "eval" {
  role_arn = module.role_codepipeline_eval.iam_role_arn
  name     = local.eval_pipeline_name
  artifact_store {
    location = module.bucket_pipeline_artifacts_eval.s3_bucket_id
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
      output_artifacts = ["CDKSourceArtifact"]

      configuration = {
        RepositoryName = local.repos.cdk.name
        BranchName     = local.repos.cdk.branch
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
      input_artifacts  = ["CDKSourceArtifact"]
      output_artifacts = ["CDKSynthArtifact"]

      configuration = {
        ProjectName = aws_codebuild_project.eval.name
        EnvironmentVariables = jsonencode([
          {
            name  = "SYNTHED_TEMPLATES_BUCKET"
            value = module.bucket_synthed_templates.s3_bucket_id
            type  = "PLAINTEXT"
          },
          {
            name  = "SSM_PARAMETER_NAME_FOR_CFN_TEMPLATE_NAME"
            value = local.ssm_parameter_name_for_cfn_template_name
            type  = "PLAINTEXT"
          }
        ])
      }
    }
  }
  stage {
    name = "EvalEngine"

    action {
      name     = "EvalEngine"
      category = "Invoke"
      owner    = "AWS"
      provider = "StepFunctions"
      version  = "1"

      configuration = {
        StateMachineArn = aws_sfn_state_machine.eval_engine.arn
        Input = jsonencode({
          "SYNTHED_TEMPLATES_BUCKET" : module.bucket_synthed_templates.s3_bucket_id
        })
      }
    }
  }
}

##################################################################
#                      eval results
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
  memory_size   = 1024 # TODO: power-tune

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
#                      eval engine
##################################################################

data "aws_iam_policy_document" "sfn_eval_engine" {
  statement {
    actions = [
      "logs:*",
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
  statement {
    actions = [
      "ssm:GetParameter",
    ]
    resources = [
      "arn:aws:ssm:${local.region}:${data.aws_caller_identity.i.id}:parameter${local.ssm_parameter_name_for_cfn_template_name}"
    ]
  }
}

module "policy_sfn_eval_engine" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "sfn_eval_engine"
  path = "/"

  policy = data.aws_iam_policy_document.sfn_eval_engine.json
}

module "role_sfn_eval_engine" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "sfn_eval_engine"

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

resource "aws_sfn_state_machine" "eval_engine" {
  name     = "${local.resource_prefix}-eval-engine"
  role_arn = module.role_sfn_eval_engine.iam_role_arn
  type     = "STANDARD"

  definition = jsonencode({
    "StartAt" : "GetCfnTemplateName",
    "States" : {
      "GetCfnTemplateName" : {
        "Type" : "Task",
        "Next" : "CFN",
        "ResultPath" : "$.GetCfnTemplateName",
        "Resource" : "arn:aws:states:::aws-sdk:ssm:getParameter",
        "Parameters" : {
          "Name" : local.ssm_parameter_name_for_cfn_template_name
        },
        "ResultSelector" : {
          "CfnTemplateName.$" : "$.Parameter.Value"
        }
      },
      "CFN" : {
        "Type" : "Pass",
        "Next" : "ParseActiveServices",
        "Parameters" : {
          "CFN" : {
            "Bucket.$" = "$.SYNTHED_TEMPLATES_BUCKET",
            "Key.$"    = "$.GetCfnTemplateName.CfnTemplateName",
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