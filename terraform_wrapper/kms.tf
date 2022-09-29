
variable "aws-partition" {
  description = "The specific AWS partition to be deployed into. Vast majority of use cases will only need the regular 'aws' partition."
  default = "aws"

  validation {
    condition = can(regex("aws|aws-us-gov|aws-cn", var.aws-partition))
    error_message = "Please use a valid AWS partition, or comment out this validation check if the provided list is out of date."
  }
}

data "aws_caller_identity" "current-account" {
  # To retrieve the account ID -- needed for KMS key policy
}

data "aws_region" "current-region" {
  # To retrieve the current AWS region
}

resource "aws_kms_key" "cdk_deployer_kms_key" {
  description             = "CDK deployer key"
  policy      = <<EOF
{
    "Version": "2012-10-17",
    "Id": "key-consolepolicy",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:${var.aws-partition}:iam::${data.aws_caller_identity.current-account.account_id}:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the Key for CodeBuild and CodePipeline",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "${aws_iam_role.terraform_cdk_wrapper_cdk_deployer_role.arn}",
                    "${aws_iam_role.terraform_cdk_wrapper_pipeline_role.arn}"
                ]
            },
            "Action": [
                "kms:Encrypt*",
                "kms:Decrypt*",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:Describe*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the Key for CloudWatch logging",
            "Effect": "Allow",
            "Principal": {
                "Service": "logs.${data.aws_region.current-region.name}.amazonaws.com"
            },
            "Action": [
                "kms:Encrypt*",
                "kms:Decrypt*",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:Describe*"
            ],
            "Resource": "*",
            "Condition": {
                "ArnEquals": {
                    "kms:EncryptionContext:${var.aws-partition}:logs:arn": "arn:${var.aws-partition}:logs:${data.aws_region.current-region.name}:${data.aws_caller_identity.current-account.account_id}:*:*"
                }
            }
        }
    ]
}
EOF
}