#!/bin/bash


# Set pipeline variables
. ./set-variables.sh "${1:-cb_audit}"

cd ../

terraform init
terraform validate
yes "yes" | terraform apply

cd ops