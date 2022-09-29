#!/bin/bash


# Set pipeline variables
. ./set-variables.sh "${1:-cb_audit}"

cd ../

export TF_VAR_cdk_destroy=true

terraform init
terraform validate
yes "yes" | terraform apply

# Wait for new pipeline to be invoked before checking state
read -p "Waiting for Pipeline to trigger..." -t 60

cdk_state=$(aws codepipeline get-pipeline-state --name "$TF_VAR_codepipeline_pipeline_name" --output "text" --query "stageStates[1].latestExecution.status")
echo "State of CDK teardown is: ${cdk_state}"
while [ "$cdk_state" != "Succeeded" ]
do
    read -p "Still waiting for teardown Pipeline to complete..." -t 10
    cdk_state=$(aws codepipeline get-pipeline-state --name "$TF_VAR_codepipeline_pipeline_name" --output "text" --query "stageStates[1].latestExecution.status")
    echo "State of CDK teardown is: ${cdk_state}"
done
echo "CDK teardown complete. Tearing down Terraform wrapper resources.."
terraform destroy
echo "Terraform CDK deployment wrapper teardown complete."
cd ops

# if [$cdk_destroy -eq "false"]
# then
#     cdk deploy \
#     --profile default \
#     --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess \
#     --require-approval never --force true
# else
#     cdk destroy \
#     --profile default \
#     --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess \
#     --require-approval never --force true
# fi