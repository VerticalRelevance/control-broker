

variable "resource_bucket_name" {
  type = string
  description = "The name of the S3 bucket for supporting Control Broker deployment."
}


variable "AWS_ACCESS_KEY_ID" {
  type = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
  sensitive = true
}

variable "AWS_SESSION_TOKEN" {
  type = string
  sensitive = true
}