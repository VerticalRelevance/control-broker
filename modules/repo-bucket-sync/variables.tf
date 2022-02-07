variable "repo" {
    type = map
}

variable "resource_prefix" {
    type = string
}

variable "destination_bucket" {
    type = string
}

variable "empty_bucket_lambda_function_name" {
    type = string
}