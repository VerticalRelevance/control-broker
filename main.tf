terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket  = "cschneider-terraform-backend-02" #RER
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
  profile="047395971161_AWSOrganizationsFullAccess"

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


##################################################################
#                       locals
##################################################################

locals {
  toggled_boolean_path = "${path.module}/dev/toggled_boolean.json"
  toggled_boolean      = file(local.toggled_boolean_path)
}

resource "local_file" "toggled" {
  content  = !local.toggled_boolean
  filename = local.toggled_boolean_path
}

resource "aws_sqs_queue" "terraform_queue" {
  name                        = "terraform-example-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = local.toggled_boolean_path
}