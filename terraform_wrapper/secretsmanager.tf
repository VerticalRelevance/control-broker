

resource "aws_secretsmanager_secret" "wrapper_access_key_id" {
  name = "terraform-wrapper/access-key-id1"
}

resource "aws_secretsmanager_secret_version" "wrapper_access_key_id" {
  secret_id     = aws_secretsmanager_secret.wrapper_access_key_id.id
  secret_string = var.AWS_ACCESS_KEY_ID
}

resource "aws_secretsmanager_secret" "wrapper_secret_access_key" {
  name = "terraform-wrapper/secret-access-key1"
}

resource "aws_secretsmanager_secret_version" "wrapper_secret_access_key" {
  secret_id     = aws_secretsmanager_secret.wrapper_secret_access_key.id
  secret_string = var.AWS_SECRET_ACCESS_KEY
}

resource "aws_secretsmanager_secret" "wrapper_session_token" {
  name = "terraform-wrapper/session-token1"
}

resource "aws_secretsmanager_secret_version" "wrapper_session_token" {
  secret_id     = aws_secretsmanager_secret.wrapper_session_token.id
  secret_string = var.AWS_SESSION_TOKEN
}