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

output "auth_ecr" {
  value = "\naws ecr get-login-password --region ${local.region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.i.id}.dkr.ecr.${local.region}.amazonaws.com\n"
}

##################################################################
#               sagemaker RK demo resources
##################################################################

locals {
  console_sagemaker_role_notebook = "arn:aws:iam::446960196218:role/service-role/AmazonSageMaker-ExecutionRole-20220827T090729"
  console_sagemaker_role_model    = "arn:aws:iam::446960196218:role/service-role/AmazonSageMaker-ExecutionRole-20220827T090729"
  console_kms_key_arn             = "arn:aws:kms:us-east-1:446960196218:key/2fe5b328-ecb5-4bac-8821-091c7bcc4b15"
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
  direct_internet_access = "Disabled"
  security_groups = [
    aws_security_group.g.id
  ]
  subnet_id = module.vpc.private_subnets[0]
}

resource "aws_ecr_repository" "r" {
  name = local.resource_prefix

  image_scanning_configuration {
    scan_on_push = true
  }
}

locals {
  docker_image_name = "m1" # i.e., not ec2ib
  docker_tag_name   = "latest"
  docker_build      = "docker build -t ${local.docker_image_name}:${local.docker_tag_name} ."
  model_to_ecr      = "\n${local.docker_build} && docker tag  ${local.docker_image_name}:${local.docker_tag_name} ${aws_ecr_repository.r.repository_url}:${local.docker_image_name} && docker push ${aws_ecr_repository.r.repository_url}:${local.docker_image_name}"
  model_image_name  = "${aws_ecr_repository.r.repository_url}:${local.docker_image_name}"
}

output "model_to_ecr" {
  value = local.model_to_ecr
}

resource "aws_sagemaker_model" "m" {
  name               = local.resource_prefix
  execution_role_arn = local.console_sagemaker_role_model

  primary_container {
    image = local.model_image_name
  }
}

locals {
  toggled_boolean_path = "${path.module}/dev/toggled_boolean.json"
  toggled_boolean      = file(local.toggled_boolean_path)
}

resource "local_file" "toggled" {
  content  = !local.toggled_boolean
  filename = local.toggled_boolean_path
}

resource "aws_sagemaker_endpoint_configuration" "c" {
  name = local.resource_prefix

  production_variants {
    variant_name = "variant-1"
    model_name   = aws_sagemaker_model.m.name
    serverless_config {
      max_concurrency   = 1
      memory_size_in_mb = 1024
    }
  }

  kms_key_arn = local.toggled_boolean ? local.console_kms_key_arn : null
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


##################################################################
#                       PaC 
##################################################################

locals {
  cfn_guard_config_events_policies_dir = "${path.module}/resources/policy_as_code/cfn_guard/expected_schema_config_event_invoking_event"
}

resource "aws_s3_bucket" "pac" {
  bucket_prefix = "${local.resource_prefix}-pac"
}

resource "aws_s3_bucket_public_access_block" "example" {
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

output "cfn_guard_install_cli_command" {
  value = "\ncurl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/aws-cloudformation/cloudformation-guard/main/install-guard.sh | sh && cp -r ~/.guard ${path.module}/control-broker/resources/lambda/eval_engine_cfn_guard/.guard"
}

data "aws_iam_policy_document" "lambda_eval_engine_cfn_guard" {
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

module "lambda_eval_engine_cfn_guard" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                  = "${local.resource_prefix}-eval_engine_cfn_guard"
  handler                        = "lambda_function.lambda_handler"
  runtime                        = "python3.9"
  timeout                        = 60
  memory_size                    = 512
  reserved_concurrent_executions = 1

  source_path = "./resources/lambda/eval_engine_cfn_guard"

  environment_variables = {
    # ProcessingSfnArn = aws_sfn_state_machine.convert_then_lint.arn
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.lambda_eval_engine_cfn_guard.json
  
  tags={
    IsCompliant	=true
  }
}