resource "aws_codepipeline" "terraform_cdk_wrapper_pipeline_deployer" {
  name     = "tf-test-pipeline"
  role_arn = aws_iam_role.terraform_cdk_wrapper_pipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.bucket
    type     = "S3"
    
    # TODO - Add encryption
    # encryption_key {
    #   id   = data.aws_kms_alias.s3kmskey.arn
    #   type = "KMS"
    # }
  }
  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "S3"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        S3Bucket = aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.id
        S3ObjectKey = "source.zip"
      }
    }
  }
  stage {
    name = "Deploy"
    action {
      name             = "Deploy"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      # output_artifacts = ["build_output"]
      version          = "1"
      configuration = {
        ProjectName = aws_codebuild_project.terraform_cdk_wrapper_cdk_deployer.name
      }
    }
  }
}



# TODO - Parameterize!
resource "aws_iam_role" "terraform_cdk_wrapper_pipeline_role" {
  name = "terraform_cdk_wrapper_pipeline_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}
# TODO - Parameterize!
resource "aws_iam_role_policy" "terraform_cdk_wrapper_pipeline_policy" {
  name = "terraform_cdk_wrapper_pipeline_policy"
  role = aws_iam_role.terraform_cdk_wrapper_pipeline_role.id
  depends_on = [
    aws_s3_object.control_broker_source_files_zip
  ]
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
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
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}