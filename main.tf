terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket  = "verticalrelevance-test-org-spoke-1-terraform-backend" #RER
    key     = "control-broker/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true

    skip_metadata_api_check     = true
    skip_region_validation      = true
    skip_credentials_validation = true
  }
}
provider "aws" {
  region  = local.region
  profile = "047395971161_AWSAdministratorAccess"

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
}

data "aws_caller_identity" "i" {}

data "aws_organizations_organization" "o" {}

locals {
  toggled_boolean_path = "${path.module}/dev/toggled_boolean.json"
  toggled_boolean      = file(local.toggled_boolean_path)
}

resource "local_file" "toggled" {
  content  = !local.toggled_boolean
  filename = local.toggled_boolean_path
}

##################################################################
#                       generate events
##################################################################

resource "aws_sqs_queue" "q" {
  name                        = "${local.resource_prefix}-event-generator-via-toggle-cbd.fifo"
  fifo_queue                  = true
  # content_based_deduplication = local.toggled_boolean
  content_based_deduplication=true
}

data "aws_iam_policy_document" "lambda_toggle_sqs_cbd" {
  statement {
    actions = [
      "sqs:*",
    ]
    resources = [
      aws_sqs_queue.q.arn
    ]
  }
}

module "lambda_toggle_sqs_cbd" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                  = "${local.resource_prefix}-toggle_sqs_cbd"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
  # reserved_concurrent_executions = 10

  source_path = "./resources/lambda/toggle_sqs_cbd"

  environment_variables = {
    QueueUrl = aws_sqs_queue.q.url
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_toggle_sqs_cbd.json
}

resource "aws_cloudwatch_event_rule" "r" {
  name                = local.resource_prefix
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "t" {
  rule      = aws_cloudwatch_event_rule.r.name
  arn       = module.lambda_toggle_sqs_cbd.lambda_function_arn
}

resource "aws_lambda_permission" "p" {
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_toggle_sqs_cbd.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.r.arn
}

##################################################################
#                       config 
##################################################################

resource "aws_lambda_permission" "custom_config" {
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_custom_config.lambda_function_name
  principal     = "config.amazonaws.com"
  statement_id  = "ConfigCanInvoke"
}

resource "aws_config_config_rule" "r" {

  name = "${local.resource_prefix}"

  source {
    owner             = "CUSTOM_LAMBDA"
    source_identifier = module.lambda_custom_config.lambda_function_arn
    source_detail {
      message_type = "ConfigurationItemChangeNotification"
    }
  }

  depends_on = [
    aws_lambda_permission.custom_config,
  ]

  scope {
    compliance_resource_types = [
      "AWS::SQS::Queue",
    ]
  }

}

data "aws_iam_policy_document" "lambda_custom_config" {
  statement {
    actions = [
      "config:*",
    ]
    resources = [
      "*"
    ]
  }
}

module "lambda_custom_config" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                  = "${local.resource_prefix}-invoked_by_config"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
#   reserved_concurrent_executions = 1

  source_path = "./resources/lambda/invoked_by_config"

#   environment_variables = {
#     ProcessingSfnArn = aws_sfn_state_machine.process_config_event.arn
#   }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_custom_config.json
}