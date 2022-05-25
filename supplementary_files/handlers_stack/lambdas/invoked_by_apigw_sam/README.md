# SAM to CloudFormation

## After deployment

`cloudformation get-template` returns the compiled to raw CFN version after deployment

## Before Deployment

[sam-translate.py](https://github.com/aws/serverless-application-model/blob/6188d82230e2fba243cf61e8f60457a028159fdb/bin/sam-translate.py#L5)

`Known limitations: cannot transform CodeUri pointing at local directory.`

## Control Broker support for conversion

As of research 5.23.22, no native, reliable way to translate SAM.template.yaml to CFN.template.json before deployment

Potentially, some isolated env where you deploy the SAM app just to be able to access the transformed raw CFN, but this a breach of the whole PaC principle: deploying something  something just to see what it is,