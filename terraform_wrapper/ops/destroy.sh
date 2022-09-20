#!/bin/bash

# Set pipeline variables
. ./set-variables.sh "${1:-central}"

# Set pipeline variables
. ./set-variables.sh "${1:-cb_audit}"

cd ../

terraform init
terraform destroy
# terraform deploy

cd ops