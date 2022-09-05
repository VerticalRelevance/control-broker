terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket  = "audit-test-terraform-backend" #RER
    key     = "control-broker/terraform.tfstate"
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
  resource_prefix = "control-broker"
  azs             = formatlist("${local.region}%s", ["a", "b", "c"])
}

data "aws_caller_identity" "i" {}

data "aws_organizations_organization" "o" {}

##################################################################
#                       config agg 
##################################################################

locals {
  config_agg_sns_topic_arn = "arn:aws:sns:us-east-1:615251248113:aws-controltower-AllConfigNotifications"
}

locals {
  spoke_accounts_path = "${path.module}/ignored/spoke_accounts.json"
  spoke_accounts      = file(local.spoke_accounts_path)
}

output "spoke_accounts" {
  value = local.spoke_accounts
}

##################################################################
#                      invoked by sns
##################################################################

resource "aws_sns_topic_subscription" "lambda_invoked_by_sns" {
  topic_arn = local.config_agg_sns_topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_invoked_by_sns.lambda_function_arn
}


resource "aws_lambda_permission" "lambda_invoked_by_sns" {
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_invoked_by_sns.lambda_function_arn
  principal     = "sns.amazonaws.com"
  source_arn    = local.config_agg_sns_topic_arn
}


data "aws_iam_policy_document" "lambda_invoked_by_sns" {
  statement {
    actions = [
      "states:StartExecution",
    ]
    resources = [
      aws_sfn_state_machine.process_config_event.arn
    ]
  }
}

module "lambda_invoked_by_sns" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${local.resource_prefix}-invoked_by_sns"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 512
  #   reserved_concurrent_executions = 1

  source_path = "./resources/lambda/invoked_by_sns"

  environment_variables = {
    SpokeAccountIds  = local.spoke_accounts
    ProcessingSfnArn = aws_sfn_state_machine.process_config_event.arn
  }

     attach_policy_json = true
     policy_json        = data.aws_iam_policy_document.lambda_invoked_by_sns.json
}


##################################################################
#                       PaC 
##################################################################

locals {
  cfn_guard_config_events_policies_dir = "${path.module}/resources/policy_as_code/cfn_guard/expected_schema_config_event_invoking_event"
}

resource "aws_s3_bucket" "pac" {
  bucket_prefix = "${local.resource_prefix}-pac"
}

resource "aws_s3_bucket_public_access_block" "pac" {
  bucket = aws_s3_bucket.pac.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_object" "cfn_guard_policies" {
  for_each = fileset(local.cfn_guard_config_events_policies_dir, "*")

  bucket = aws_s3_bucket.pac.id
  key    = "cfn_guard/expected_schema_config_event_invoking_event/${each.value}"
  source = "${local.cfn_guard_config_events_policies_dir}/${each.value}"
  etag   = filemd5("${local.cfn_guard_config_events_policies_dir}/${each.value}")
}


##################################################################
#                       eval engine 
##################################################################

resource "aws_s3_bucket" "input_to_be_analyzed" {
  bucket_prefix = "${local.resource_prefix}-input-to-be-analyzed"
}

resource "aws_s3_bucket_public_access_block" "input_to_be_analyzed" {
  bucket = aws_s3_bucket.input_to_be_analyzed.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "cfn_guard_install_cli_command" {
  value = "\ncurl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/aws-cloudformation/cloudformation-guard/main/install-guard.sh | sh && cp -r ~/.guard ~/environment/control-broker/resources/lambda/eval_engine_cfn_guard/.guard"
}

data "aws_iam_policy_document" "lambda_eval_engine_cfn_guard" {
  statement {
    actions = [
      "s3:Get*",
      "s3:List*",
    ]
    resources = [
      "*",
      aws_s3_bucket.input_to_be_analyzed.arn,
      "${aws_s3_bucket.input_to_be_analyzed.arn}*",
      aws_s3_bucket.pac.arn,
      "${aws_s3_bucket.pac.arn}*",
    ]
  }
}

module "lambda_eval_engine_cfn_guard" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                  = "${local.resource_prefix}-eval_engine_cfn_guard"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
#   reserved_concurrent_executions = 4

  source_path = "./resources/lambda/eval_engine_cfn_guard"

  environment_variables = {
    # ProcessingSfnArn = aws_sfn_state_machine.process_config_event.arn
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_eval_engine_cfn_guard.json

  tags = {
    IsCompliant = true
  }
}

##################################################################
#                       output handler 
##################################################################

data "aws_iam_policy_document" "lambda_output_handler" {
  statement {
    actions = [
      "config:PutEvaluationResults",
      "config:*",
    ]
    resources = [
      "*",
    ]
  }
}

module "lambda_output_handler" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                  = "${local.resource_prefix}-output_handler"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
#   reserved_concurrent_executions = 4

  source_path = "./resources/lambda/output_handler"

  environment_variables = {
    # ProcessingSfnArn = aws_sfn_state_machine.process_config_event.arn
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_output_handler.json

  tags = {
    IsCompliant = true
  }
}

##################################################################
#                       put object 
##################################################################

data "aws_iam_policy_document" "lambda_s3_put_object" {
  statement {
    actions = [
      "s3:List*",
      "s3:PutObject*",
    ]
    resources = [
      "*",
      aws_s3_bucket.input_to_be_analyzed.arn,
      "${aws_s3_bucket.input_to_be_analyzed.arn}*",
    ]
  }
}

module "lambda_s3_put_object" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                  = "${local.resource_prefix}-s3_put_object"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
#   reserved_concurrent_executions = 4

  source_path = "./resources/lambda/s3_put_object"

  environment_variables = {
    # ProcessingSfnArn = aws_sfn_state_machine.process_config_event.arn
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_s3_put_object.json

  tags = {
    IsCompliant = true
  }
}

##################################################################
#                       asff 
##################################################################

data "aws_iam_policy_document" "lambda_put_asff" {
  statement {
    actions = [
      "securityhub:BatchImportFindings",
      "securityhub:*",
    ]
    resources = [
      "*",
    ]
  }
}

module "lambda_put_asff" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                  = "${local.resource_prefix}-put_asff"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
#   reserved_concurrent_executions = 4

  source_path = "./resources/lambda/put_asff"

  environment_variables = {
    # ProcessingSfnArn = aws_sfn_state_machine.process_config_event.arn
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_put_asff.json

  tags = {
    IsCompliant = true
  }
}


##################################################################
#                       process config event 
##################################################################

# cwl - sfn

resource "aws_cloudwatch_log_group" "sfn_process_config_event" {
  name = "/aws/vendedlogs/states/${local.resource_prefix}-sfn_process_config_event"
}

# iam - sfn

data "aws_iam_policy_document" "sfn_process_config_event" {
  statement {
    actions = [
      "logs:*",
    ]
    resources = [
      "*", #FIXME
      aws_cloudwatch_log_group.sfn_process_config_event.arn,
      "${aws_cloudwatch_log_group.sfn_process_config_event.arn}:*"
    ]
  }
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    resources = [
      module.lambda_eval_engine_cfn_guard.lambda_function_arn,
      module.lambda_output_handler.lambda_function_arn,
      module.lambda_s3_put_object.lambda_function_arn,
    ]
  }
  statement {
    actions = [
      "config:*",
    ]
    resources = [
      "*"
    ]
  }
}

module "policy_process_config_event" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${local.resource_prefix}-process_config_event"
  path = "/"

  policy = data.aws_iam_policy_document.sfn_process_config_event.json
}

module "role_process_config_event" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = "${local.resource_prefix}-process_config_event"

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "states.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_process_config_event.arn,
  ]

}

# sfn

resource "aws_sfn_state_machine" "process_config_event" {
  name     = "${local.resource_prefix}-process_config_event"
  role_arn = module.role_process_config_event.iam_role_arn
  type     = "STANDARD"
  # type = "EXPRESS"
  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.sfn_process_config_event.arn}:*"
    include_execution_data = true
    # level                  = "ERROR"
    level = "ALL"
  }

  definition = jsonencode({
    "StartAt" : "ParseInput0",
    "States" : {
      "ParseInput0" : {
        "Type" : "Pass",
        "Next" : "ParseInput1",
        "ResultPath" : "$",
        "Parameters" : {
          "SnsMessage.$" : "$"
        }
      },
      "ParseInput1" : {
        "Type" : "Pass",
        "Next" : "PutInputToBeAnalyzed",
        "ResultPath" : "$.InputToBeAnalyzed",
        "Parameters" : {
          "Bucket" : aws_s3_bucket.input_to_be_analyzed.id,
          "Key.$" : "States.Format('{}#{}',$.SnsMessage.configurationItem.resourceType,$.SnsMessage.configurationItem.resourceId)"
        }
      },
      "PutInputToBeAnalyzed" : {
        "Type" : "Task",
        "Next" : "EvalEngine",
        "ResultPath" : "$.PutInputToBeAnalyzed",
        "Resource" : "arn:aws:states:::lambda:invoke",
        "Parameters" : {
          "FunctionName" : module.lambda_s3_put_object.lambda_function_name,
          "Payload" : {
            "Bucket.$" : "$.InputToBeAnalyzed.Bucket",
            "Key.$" : "$.InputToBeAnalyzed.Key"
            "Object.$" : "$.SnsMessage"
          }
        },
        "ResultSelector" : {
          "InputManifest.$" : "$.Payload"
        }
      },
      "EvalEngine" : {
        "Type" : "Task",
        "Next" : "OutputHandler",
        "ResultPath" : "$.EvalEngine",
        "Resource" : "arn:aws:states:::lambda:invoke",
        "Parameters" : {
          "FunctionName" : module.lambda_eval_engine_cfn_guard.lambda_function_arn,
          "Payload" : {
            "Rules" : {
              "Bucket" : aws_s3_bucket.pac.id,
              "Prefix" : "cfn_guard/expected_schema_config_event_invoking_event"
            },
            "InputToBeAnalyzed" : {
              "Bucket.$" : "$.InputToBeAnalyzed.Bucket",
              "Key.$" : "$.InputToBeAnalyzed.Key"
            },
          }
        },
        "ResultSelector" : {
          "Payload.$" : "$.Payload"
        },
      },
      "OutputHandler" : {
        "Type" : "Task",
        "Next" : "PutASFF",
        "ResultPath" : "$.OutputHandler",
        "Resource" : "arn:aws:states:::lambda:invoke",
        "Parameters" : {
          "FunctionName" : module.lambda_output_handler.lambda_function_arn,
          "Payload.$" : "$.EvalEngine.Payload"
        },
        "ResultSelector" : {
          "Payload.$" : "$.Payload"
        },
      },
      "PutASFF" : {
        "Type" : "Task",
        "End" : true,
        "ResultPath" : "$.PutASFF",
        "Resource" : "arn:aws:states:::lambda:invoke",
        "Parameters" : {
          "FunctionName" : module.lambda_put_asff.lambda_function_arn,
          "Payload.$" : "$.EvalEngine.Payload"
        },
        "ResultSelector" : {
          "Payload.$" : "$.Payload"
        },
      },
      
    }
  })
}