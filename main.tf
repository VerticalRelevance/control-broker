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
  azs             = formatlist("${local.region}%s", ["a", "b", "c"])
}

data "aws_caller_identity" "i" {}

data "aws_organizations_organization" "o" {}

##################################################################
#               sagemaker RK demo resources
##################################################################

locals {
  console_sagemaker_role_notebook = "arn:aws:iam::446960196218:role/service-role/AmazonSageMaker-ExecutionRole-20220827T090729",
  console_sagemaker_role_model = "arn:aws:iam::446960196218:role/service-role/AmazonSageMaker-ExecutionRole-20220827T090729",
  console_kms_key_id="arn:aws:kms:us-east-1:446960196218:key/2fe5b328-ecb5-4bac-8821-091c7bcc4b15"
}


module "vpc" {

  source = "terraform-aws-modules/vpc/aws"

  name = local.resource_prefix

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

resource "aws_security_group" "g" {
  name   = local.resource_prefix
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
  name                   = local.resource_prefix
  role_arn               = local.console_sagemaker_role_notebook
  instance_type          = "ml.t2.medium"
  # direct_internet_access = "Disabled"
  # security_groups = [
  #   aws_security_group.g.id
  # ]
  # subnet_id = module.vpc.private_subnets[0]
}

resource "aws_ecr_repository" "r" {
  name = "${local.resource_prefix}"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# resource "aws_sagemaker_model" "m" {
#   name                   = local.resource_prefix
#   execution_role_arn = local.console_sagemaker_role_model

#   primary_container {
#     image = data.aws_sagemaker_prebuilt_ecr_image.test.registry_path
#   }
# }


# resource "aws_sagemaker_endpoint_configuration" "c" {
#   name   = local.resource_prefix

#   production_variants {
#     variant_name           = "variant-1"
#     model_name             = aws_sagemaker_model.m.name
#     initial_instance_count = 1
#     instance_type          = "ml.t2.medium"
#   }
# }


##################################################################
#                       config 
##################################################################

resource "aws_lambda_permission" "custom_config" {
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_custom_config.lambda_function_name
  principal     = "config.amazonaws.com"
  statement_id  = "ConfigCanInvoke"
}

resource "aws_config_config_rule" "sagemaker" {

  name = "${local.resource_prefix}-sagemaker"

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
      "AWS::SageMaker::NotebookInstance",
      "AWS::SageMaker::EndpointConfig",
    ]
  }

  # input_parameters = jsonencode({
  #   "something" : "useful"
  # })

}

data "aws_iam_policy_document" "lambda_custom_config" {
  statement {
    actions = [
      "states:StartSyncExecution",
      "states:StartExecution",
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
  reserved_concurrent_executions = 1

  source_path = "./resources/lambda/invoked_by_config"

  environment_variables = {
    # ProcessingSfnArn = aws_sfn_state_machine.convert_then_lint.arn
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_custom_config.json
}