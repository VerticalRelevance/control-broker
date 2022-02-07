# repo-bucket-sync

data "aws_caller_identity" "i" {}

data "aws_codecommit_repository" "source" {
    repository_name = var.repo.name
}

# s3

module "bucket_pipeline_artifacts" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = substr("${var.repo.name}-repo-bucket-sync-codepipeline-artifacts", 0, 62)

  # Allow deletion of non-empty bucket
  force_destroy = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
  
  tags = {
    Project = var.resource_prefix
  }
}

# iam

data "aws_iam_policy_document" "codepipeline" {
  statement {
    actions = [
      "codecommit:CancelUploadArchive",
      "codecommit:GetBranch",
      "codecommit:GetCommit",
      "codecommit:GetRepository",
      "codecommit:GetUploadArchiveStatus",
      "codecommit:UploadArchive",
      "codedeploy:CreateDeployment",
      "codedeploy:GetApplication",
      "codedeploy:GetApplicationRevision",
      "codedeploy:GetDeployment",
      "codedeploy:GetDeploymentConfig",
      "codedeploy:RegisterApplicationRevision",
    ]
    resources = [
      "*",
    ]
  }
  statement {
    actions = [
      "s3:Head*",
      "s3:List*",
      "s3:Get*",
      "s3:Put*",
    ]
    resources = [
      module.bucket_pipeline_artifacts.s3_bucket_arn,
      "${module.bucket_pipeline_artifacts.s3_bucket_arn}/*",
    ]
  }
  statement {
    actions = [
      "s3:Head*",
      "s3:List*",
      "s3:Put*",
    ]
    resources = [
      "arn:aws:s3:::${var.destination_bucket}",
      "arn:aws:s3:::${var.destination_bucket}/*",
    ]
  }
  statement {
    actions = [
      "iam:AssumeRole",
    ]
    resources = [
      "*", #FIXME
    ]
  }
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    resources = [
      "arn:aws:lambda:*:${data.aws_caller_identity.i.id}:function:${var.empty_bucket_lambda_function_name}"
    ]
  }
}

module "policy_codepipeline" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name = "${var.repo.name}-repo-bucket-sync-codepipeline"
  path = "/"

  policy = data.aws_iam_policy_document.codepipeline.json

  tags = {
    Project = var.resource_prefix
  }
}

module "role_codepipeline" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "4.7.0"

  create_role       = true
  role_requires_mfa = false

  role_name = substr("${var.repo.name}-repo-bucket-sync-codepipeline", 0, 64)

  trusted_role_arns = [
    data.aws_caller_identity.i.arn
  ]

  trusted_role_services = [
    "codepipeline.amazonaws.com"
  ]

  custom_role_policy_arns = [
    module.policy_codepipeline.arn,
  ]

  tags = {
    Project = var.resource_prefix
  }
}

# codepipeline

resource "aws_codepipeline" "repo_bucket_sync" {
  name = "${var.repo.name}-repo-bucket-sync"
  role_arn = module.role_codepipeline.iam_role_arn

  artifact_store {
    location = module.bucket_pipeline_artifacts.s3_bucket_id
    type     = "S3"
  }

  tags = {
    Project = var.resource_prefix
  }
  
  stage {
    name = "Source"

    action {
      name             = "${var.repo.name}--${var.repo.branch}"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeCommit"
      version          = "1"
      output_artifacts = ["SourceArtifact"]

      configuration = {
        RepositoryName = var.repo.name
        BranchName     = var.repo.branch
      }
    }
  }

  stage {
    name = "EmptyBucket-${var.destination_bucket}"

    action {
        name = "EmptyBucket-${var.destination_bucket}"
      category = "Invoke"
      owner    = "AWS"
      provider = "Lambda"
      version  = "1"

      configuration = {
        FunctionName = var.empty_bucket_lambda_function_name
        UserParameters = jsonencode({
          "BucketToEmpty" : var.destination_bucket
        })
      }

    }
  }

  stage {
    name = "Deploy"

    action {
        name = "Deploy"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "S3"
      version         = "1"
      input_artifacts = ["SourceArtifact"]

      configuration = {
        BucketName = var.destination_bucket
        Extract    = true
      }
    }
  }
}
