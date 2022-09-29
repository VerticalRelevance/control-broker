
# Creates Zip of source files
data "archive_file" "cdk_source_files" {
  type = "zip"
  output_path = "${path.module}/${var.cdk_source_file_name}"
  source_dir = "${path.module}/${var.cdk_source_directory}"
}

# Uploads source files to S3 bucket for CodeBuild
resource "aws_s3_object" "control_broker_source_files_zip" {
  bucket = aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.id
  key    = var.cdk_source_file_key
  source = "${path.module}/${var.cdk_source_file_name}"
  etag = data.archive_file.cdk_source_files.output_md5
}

resource "aws_s3_bucket" "terraform_cdk_wrapper_pipeline_bucket" {
  bucket = var.resource_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.terraform_cdk_wrapper_pipeline_bucket.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.cdk_deployer_kms_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
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