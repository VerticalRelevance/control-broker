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
  azs                = formatlist("${var.region}%s", ["a", "b", "c"])
}

data "aws_caller_identity" "i" {}

data "aws_organizations_organization" "o" {}

##################################################################
#               sagemaker RK demo resources
##################################################################

locals {
  console_sm_role = "arn:aws:iam::446960196218:role/service-role/AmazonSageMaker-ExecutionRole-20220827T090729"
}



module "vpc" {

  source = "terraform-aws-modules/vpc/aws"

  name = var.resource_prefix

  cidr = "10.0.0.0/16"

  azs = local.azs

  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  create_egress_only_igw = true
  create_igw             = true

  enable_ipv6 = false

  enable_nat_gateway     = false
  single_nat_gateway     = false
  one_nat_gateway_per_az = false

  create_vpc = true
}

# sg

resource "aws_security_group" "g" {
  name   = "${local.resource_prefix}"
  vpc_id = module.vpc.vpc_id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_sagemaker_notebook_instance" "i" {
  name          = local.resource_prefix
  role_arn      = local.console_sm_role
  instance_type = "ml.t2.medium"
  direct_internet_access="disabled"
  security_groups=[
    aws_security_group.g.id
  ]
  subnet_id=module.vpc.private_subnets[0]
}