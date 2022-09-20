#!/bin/bash


# Set pipeline variables
. ./set-variables.sh "${1:-cb_audit}"

cd ../

terraform init
terraform validate
terraform apply
# terraform deploy

cd ops