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



##################################################################
#                      invoked by sns
##################################################################

# resource "aws_lambda_permission" "invoked_by_sns" {
#   action        = "lambda:InvokeFunction"
#   function_name = module.lambda_invoked_by_sns.lambda_function_name
#   principal     = "sns.amazonaws.com"
#   statement_id  = "ConfigCanInvoke"
# }

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

  function_name                  = "${local.resource_prefix}-invoked_by_sns"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
  reserved_concurrent_executions = 1

  source_path = "./resources/lambda/invoked_by_sns"

  environment_variables = {
    ProcessingSfnArn = aws_sfn_state_machine.process_config_event.arn
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_invoked_by_sns.json
}
