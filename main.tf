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
  content_based_deduplication = local.toggled_boolean
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
  reserved_concurrent_executions = 1

  source_path = "./resources/lambda/toggle_sqs_cbd"

  environment_variables = {
    QueueUrl = aws_sqs_queue.q.url
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_toggle_sqs_cbd.json
}

resource "aws_cloudwatch_event_rule" "r" {
    name = local.resource_prefix
    schedule_expression = "rate(1 minutes)"
}

resource "aws_cloudwatch_event_target" "t" {
    rule = aws_cloudwatch_event_rule.r.name
    target_id = "check_foo"
    arn = lambda_toggle_sqs_cbd.lambda_function_arn
}

resource "aws_lambda_permission" "p" {
    action = "lambda:InvokeFunction"
    function_name = lambda_toggle_sqs_cbd.lambda_function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.r.arn
}