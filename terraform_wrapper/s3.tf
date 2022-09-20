
# Creates Zip of source files
data "archive_file" "cdk_source_files" {
  type = "zip"
  output_path = "${path.module}/source.zip"
  source_dir = "${path.module}/../src"
}

# Uploads source files to S3 bucket for CodeBuild
resource "aws_s3_object" "control_broker_source_files_zip" {
  bucket = aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.id
  key    = "source.zip"
  source = "${path.module}/source.zip"
  etag = data.archive_file.cdk_source_files.output_md5
}

# TODO - Parameterize!
resource "aws_s3_bucket" "terraform_cdk_wrapper_pipeline_bucket" {
  bucket = var.resource_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_acl" "terraform_cdk_wrapper_pipeline_bucket_acl" {
  bucket = aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "terraform_cdk_wrapper_pipeline_bucket_versioning" {
  bucket = aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}