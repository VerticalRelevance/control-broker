# opa-eval-serverless

Runs `opa eval` as a subprocess in a Python Lambda function.
Parallel execution of each ActiveService against its policy.

## dependencies

-note how `opa eval` lambda finds the name of the service rego package_suffix from the s3 key for the policy