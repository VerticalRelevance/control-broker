terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket  = "verticalrelevance-test-org-terraform-backend" #RER
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
  config_agg_sns_topic_arn="arn:aws:sns:us-east-1:305726504525:config-topic"
}


resource "aws_sqs_queue" "sub_to_config_agg_sns" {
  name                        = "${local.resource_prefix}-sub-to-config-agg-sns"
}

resource "aws_sns_topic_subscription" "sub_to_config_agg_sns" {
  topic_arn = local.config_agg_sns_topic_arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.sub_to_config_agg_sns.arn
}