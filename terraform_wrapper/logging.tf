resource "aws_cloudwatch_log_group" "cloudwatch_log_group" {
  name = var.cloudwatch_logs_group_name
  kms_key_id = aws_kms_key.cdk_deployer_kms_key.arn
  retention_in_days = 30
}

resource "aws_cloudwatch_log_stream" "cloudwatch_log_stream" {
  name = var.cloudwatch_logs_stream_name
  log_group_name = aws_cloudwatch_log_group.cloudwatch_log_group.name
}