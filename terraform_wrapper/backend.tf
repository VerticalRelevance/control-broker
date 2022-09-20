provider "aws" {
  region = "us-east-1"
}

terraform {

    backend "local" {}

#   cloud {
#     organization = "verticalrelevance"
#     hostname = "app.terraform.io" # Optional; defaults to app.terraform.io

#     workspaces {
#       name="control-broker-test" # Gets overridden in TF Cloud, based on the actual TF Cloud Workspace you are working in. You can change this locally, if needed, but be sure not to commit, since we want the development workspace to be the default for development.
#     }
#   }
}