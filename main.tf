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
#               sagemaker RK demo resources
##################################################################

locals{
  console_sm_role="arn:aws:iam::446960196218:role/service-role/AmazonSageMaker-ExecutionRole-20220827T090729"
}

resource "aws_sagemaker_notebook_instance" "i" {
  name          = "${local.resource_prefix}"
  role_arn      = local.console_sm_role
  instance_type = "ml.t2.medium"

}