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


# data "aws_iam_policy_document" "lambda_invoked_by_sns" {
#   statement {
#     actions = [
#       "states:StartExecution",
#     ]
#     resources = [
#       aws_sfn_state_machine.process_config_event.arn
#     ]
#   }
# }

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
    SpokeAccountIds = local.spoke_accounts
  }

  #   attach_policy_json = true
  #   policy_json        = data.aws_iam_policy_document.lambda_invoked_by_sns.json
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
