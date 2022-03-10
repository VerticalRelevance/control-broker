# AWS Controls Foundation - Evaluation Engine Repository

This is a deep dive on one specific component within Vertical Relevance's 
broader (AWS Control Foundation solution)[https://github.com/VerticalRelevance/ControlFoundations-Blueprint].

This repository deploys a pipeline used by Security team
to evaluate the IaC proposed by an Application team’s CDK application
using a serverless Evaluation Engine.

See the full write-up [here](TODO)


## Setup

Prior to starting the setup of the CDK environment, ensure that you have cloned this repo.

Follow the setup steps below to properly configure the environment and first deployment of the infrastructure.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are on a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Bootstrap the cdk app.

```
cdk bootstrap
```

At this point you can deploy the CDK app for this blueprint.

```
$ cdk deploy
```

After running `cdk deploy`, the pipeline will be set up.

## Walkthrough

### (1)

In the AWS Console, navigate to `CodePipeline` / `Pipelines` and find the pipeline whose name starts with `ControlBrokerEvalEngineCdkStack`. This is our Evaluation Pipeline.

The 'Initial commit by AWS CodeCommit' commit occurs when CDK initializes the repository with IaC defined in this directory [Application Team Example App](./supplementary_files/application_team_example_app) of the Root Evaluation Pipeline CDK application. These files serve only to initialize the CodeCommit repository.

See the screenshot below for the expected state of the Evaluation Pipeline upon the initial deployment.

![Screenshot of CodePipeline](./supplementary_files/readme/pipeline-screenshots/initial-commit/initial.png)

This `passMe` IaC, labeled (1) in the stack is compliant, so it should pass the Evaluation Pipeline.

Now let's modify the Example App to see what happens if we propose noncompliant IaC. 

Check the deployment output for links to clone the Example App CodeCommit repository. See [CodeCommit ssh conection setup](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html).

### (2)

Once you have cloned the repository, run `npm install`. As we edit the resources in this TypeScript CDK application, we can run `cdk synth` to confirm our resources compile to CloudFormatio successfully. But we will not `cdk deploy` this Example App directly, because the IaC must first be approved by the Evaluation Pipeline.

Next, uncomment the `failMe` resource labeled (2) in the SQS stack at path:

```
./supplementary_files/application_team_example_app/lib/control_broker_eval_engine-example_app-stack-sqs.ts 
```

Save the file, then commit to the CodeCommit repository with a commit message like:

```
add failMe resource to SQS stack
```

Return to the CodePipeline console to track the `failMe` commit through the Evaluation Pipeline. It should fail at the EvalEngine stage as seen in the below screenshot.

![Screenshot of CodePipeline](./supplementary_files/readme/pipeline-screenshots/fail-me/fail.png)

Let's see the result of the evaluation. In the AWS Console, navigate to `DynamoDB` / `Tables` and find the table whose name starts with `ControlBrokerEvalEngineCdkStack-EvalResults`. These are results of the Evaluation Pipeline.
Select `ExploreTableItems`. The evaluation results of the `failMe` commit should appear here, including the `reason` the IaC was denied along with the metadata defined in the [pipeline-ownership-metadata](/ControlBrokerEvalEngine-Blueprint/supplementary_files/pipeline-ownership-metadata/business-unit-a/eval-engine-metadata.json) file.

The `reason` should match the one specified in the relevant OPA Policy. Check out the [policies governing SQS](./supplementary_files/opa-policies/SQS) to compare the configuration of the `failMe` resource we just proposed with the allowed values defined by the OPA Policy.

This table can be queried programatically.

So far we've seen the initial commit with compliant IaC (1) pass and noncompliant IaC (2) fail using the provided OPA Policies.

### (3)

In the final portion of the walkthrough, we'll edit the OPA Policy governing the evaluation. Let's take the noncompliant SQS Queue from (2) and edit the relevant OPA Policy so that it now compliant, then we'll send it back through the Evaluation Pipeline and compare the result.

In our Example App repo, let's comment out the IaC labeled (1) and (2) and uncomment section (3).Notice that we've simple renamed the SQS Queue that just failed in (2) to `fifoFalseQueueMakeMePass` and left the configuration the same. Commit this with a commit message such as:

```
fifoFalseQueueMakeMePass
```

Now let's edit the OPA relevant Policies to make this non-Fifo Queue compliant.

Within the Root CDK Application, in let's edit the [sqs\_queue\_fifo.rego](./supplementary_files/opa-policies/SQS/sqs_queue_fifo.rego) file. In the `obedient_resources` section, edit allowed Fifo parameter value to:

```
properties.FifoQueue == false
```


To recap, while in sections (1) and (2) we used OPA Policies that required a SQS Queue to be Fifo and used ContentBasedDeduplication, in section (3) we've edited the Policies to require those same parameters to be `false`.

Save both files and redepoy: `cdk deploy`.

Then, navigate back to the Evaluation Pipeline in the AWS Console.
Remember that when we first commited `fifoFalseQueueMakeMePass`, the original OPA Policies were in place. We expect that to be rejected.
Now that we have redeployed and the changes to the OPA Policies have made their way to S3, let's run it again. Select the `Release change` button to re-run the pipeline with that same `fifoFalseQueueMakeMePass` commit. That same non-Fifo queue should now be compliant, per the changes we made to the policy. We expect the Evaluation Pipeline to succeed.

### Conclusion.

