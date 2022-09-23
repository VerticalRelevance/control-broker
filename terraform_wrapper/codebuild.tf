
resource "aws_codebuild_project" "terraform_cdk_wrapper_cdk_deployer" {
  name          = "test-project"
  description   = "test_codebuild_project"
  build_timeout = "5"
  service_role  = aws_iam_role.terraform_cdk_wrapper_cdk_deployer_role.arn
  artifacts {
    type = "NO_ARTIFACTS"
  }
  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    # image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    image = "aws/codebuild/standard:6.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    environment_variable {
      name  = "AWS_ACCESS_KEY_ID"
      value = aws_secretsmanager_secret.wrapper_access_key_id.name
      type = "SECRETS_MANAGER"
    }
    environment_variable {
      name  = "AWS_SECRET_ACCESS_KEY"
      value = aws_secretsmanager_secret.wrapper_secret_access_key.name
      type = "SECRETS_MANAGER"
    }
    environment_variable {
      name  = "AWS_SESSION_TOKEN"
      value = aws_secretsmanager_secret.wrapper_session_token.name
      type = "SECRETS_MANAGER"
    }
    # environment_variable {
    #   name  = "SOME_KEY2"
    #   value = "SOME_VALUE2"
    #   type  = "PARAMETER_STORE"
    # }
  }
  source {
    type      = "S3"
    location = "${aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.id}/${aws_s3_object.control_broker_source_files_zip.key}"
    buildspec = file("buildspec.yml")
  }
  # TODO - Configure CloudWatch Logging
  # logs_config {
  #   cloudwatch_logs {
  #     group_name  = "log-group"
  #     stream_name = "log-stream"
  #   }
  # }
}


resource "aws_iam_role" "terraform_cdk_wrapper_cdk_deployer_role" {
  name = "terraform_cdk_wrapper_cdk_deployer_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "terraform_cdk_wrapper_deployer_policy" {
  name = "terraform_cdk_wrapper_deployer_policy"
  role = aws_iam_role.terraform_cdk_wrapper_cdk_deployer_role.name
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": [
        "*"
      ],
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
    },
    {
      "Effect": "Allow",
      "Resource": [
        "*"
      ],
      "Action": [
        "cloudformation:*"
      ]
    },
    {
      "Effect": "Allow",
      "Resource": [
        "${aws_secretsmanager_secret_version.wrapper_access_key_id.arn}",
        "${aws_secretsmanager_secret_version.wrapper_secret_access_key.arn}",
        "${aws_secretsmanager_secret_version.wrapper_session_token.arn}"
      ],
      "Action": [
        "secretsmanager:GetSecretValue"
      ]
    },
    {
      "Effect":"Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:PutObjectAcl",
        "s3:PutObject"
      ],
      "Resource": [
        "${aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.arn}",
        "${aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.arn}/*"
      ]
    }
  ]
}
POLICY
}