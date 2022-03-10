# AWS Controls Foundation - Evaluation Engine Repository - Example App

Serves as an example CDK application whose IaC is evaluated by the [Evaluation Engine](https://github.com/VerticalRelevance/ControlBrokerEvalEngine-Blueprint).

Contains two simple stacks, one for SNS and one for SQS, 
each with resources labeled either `Pass` or `Fail`,
according to the expected outcome of the evaluation performed by the Evaluation Engine
per the [example OPA Policies provided in that repo](https://github.com/VerticalRelevance/ControlBrokerEvalEngine-Blueprint/tree/00de002a20f23291b0ecced6f5fec6f3365791bc/supplementary_files/opa-policies).


## Useful commands

The `cdk.json` file tells the CDK Toolkit how to execute your app.

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template
