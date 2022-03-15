# Control Broker Eval Engine

This is a deep dive on one specific component within Vertical Relevance's 
broader [AWS Control Foundation
solution](https://github.com/VerticalRelevance/ControlFoundations-Blueprint).

This repository deploys an Evaluation Pipeline used by a Security Team to
evaluate the IaC proposed by an Application Team’s CDK application.

See the full write-up [here](TODO)

## Prerequisites

Install the [AWS CDK Toolkit
v2](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) CLI tool.

If you encounter issues running the `cdk` commands below, check the version of
`aws-cdk-lib` from [./requirements.txt](./requirements.txt) for the exact
version of the CDK library used in this repo. The latest v2 version of the CDK
Toolkit should be compatible, but try installing the CDK Toolkit version
matching `requirements.txt` before trying other things to resolve your issues.

## Setup

Prior to starting the setup of the CDK environment, ensure that you have cloned
this repo.

Follow the setup steps below to properly configure the environment and first
deployment of the infrastructure.

To manually create a virtualenv on MacOS and Linux:

``` $ python3 -m venv .venv ```

After the init process completes and the virtualenv is created, you can use the
following step to activate your virtualenv.

``` $ source .venv/bin/activate ```

If you are on a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

``` $ pip install -r requirements.txt ```

[Bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-bootstrap) the
cdk app:

``` cdk bootstrap ```

At this point you can
[deploy](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-deploy) the CDK
app for this blueprint:

``` $ cdk deploy ```

After running `cdk deploy`, the pipeline will be set up.

## Walkthrough

### (1)

In the AWS Console, navigate to `CodePipeline` / `Pipelines` and find the
pipeline whose name starts with `ControlBrokerEvalEngineCdkStack`. This is our
Evaluation Pipeline.

The `Initial commit by AWS CodeCommit` commit occurs when CDK initializes the
repository with IaC defined in the  [Application Team Example
App](./supplementary_files/application_team_example_app) directory of the Root
Evaluation Pipeline CDK application. These files serve only to initialize the
CodeCommit repository.

See the screenshot below for the expected state of the Evaluation Pipeline upon
the initial deployment.

![Screenshot of CodePipeline](./supplementary_files/readme/pipeline-screenshots/initial-commit/initial.png)

The initial IaC is compliant, so it should pass the Evaluation Pipeline. Let's
modify the Example App to see what happens if we propose noncompliant IaC. 

Before we can modify the Example App, get ready to make a code change. You can
do this in a couple of ways:

1.  Clone the Example App CodeCommit repository. To clone the Example App
    CodeCommit repository, you have a number of connection options. To clone the
    repo using AWS API credentials you use for the AWS CLI, Boto3, etc., try
    [`git-remote-codecommit`](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-git-remote-codecommit.html).
    For SSH, see the [CodeCommit SSH
    documentation](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html).

2.  If you just want to play along without cloning the example repository
    to your local machine, you can instead edit code files directly using CodeCommit in the
    AWS console interface. To do this, just navigate to the example repository in
    the CodeCommit console, navigate to a file, and use the Edit button to edit
    files:

    ![Screenshot of CodeCommit with Edit button pointed to with a green arrow](./supplementary_files/readme/codecommit-screenshots/codecommit-edit-button.png)

*Note that if you choose not to clone the repository locally and instead use the*
*CodeCommit console approach, you won't be able to run the ensuing*
*`npm install`, `cdk synth`, etc., but you will be able to make the mentioned*
*code changes.*

### (2)

Once you have cloned the repository, run `npm install`. As we edit the resources
in this TypeScript CDK application, we can run `cdk synth` to confirm our
resources compile to CloudFormation successfully. But we will not `cdk deploy`
this Example App directly, because the IaC must first be approved by the
Evaluation Pipeline.

After running `npm install`, run `cdk synth` to confirm the CDK app synthesizes
without errors. You should see some output like the following:

```
[ControlBrokerEvalEngine-ApplicationTeam-ExampleApp] on  main [?]
 🦖❯ cdk synth
Successfully synthesized to ControlBrokerEvalEngine-ApplicationTeam-ExampleApp/cdk.out
Supply a stack id (ControlBrokerEvalEngineExampleAppStackSNS, ControlBrokerEvalEngineExampleAppStackSQS) to display its template.
```

You can inspect the CloudFormation templates in the `cdk.out` directory (they
end with `.template.json`) if you want.
These are what our OPA policies evaluate for compliance.

Next, inside the example app directory, we'll add a noncompliant resource to the
SQS stack. Open the Example App repo and navigate to this path:

```
lib/control_broker_eval_engine-example_app-stack-sqs.ts 
```

Remove or comment out the following bit of code:

```
  const passMeQueue = new sqs.Queue(this, 'passMeQueue', {
    fifo: true,
  });
 
```

Then uncomment the `failMeQueue` in section (2). Save the file, then commit it
to the CodeCommit repository with a command like the following (you can change
the commit message if you want):

```
git add .
git commit -m "add failMe resource to SQS stack"
```

Push your change to the CodeCommit remote:

```
git push
```

Return to the CodePipeline console to track the `failMe` commit through the
Evaluation Pipeline. It should start running shortly after you've pushed your
commit. If it doesn't, make sure you're working in the repo you cloned from
CodeCommit, not this repo.

Since we added a non-compliant resource, it should fail at the EvalEngine stage
as seen in the below screenshot:

![Screenshot of CodePipeline](./supplementary_files/readme/pipeline-screenshots/fail-me/fail.png)

Let's see the result of the evaluation. In the AWS Console, navigate to
`DynamoDB` / `Tables` and find the table whose name starts with
`ControlBrokerEvalEngineCdkStack-EvalResults`. These are results of the
Evaluation Pipeline.

Select `ExploreTableItems`. The evaluation results of the `failMe` commit should
appear here, including the `reason` the IaC was denied along with the metadata
defined in the
[pipeline-ownership-metadata](/ControlBrokerEvalEngine-Blueprint/supplementary_files/pipeline-ownership-metadata/business-unit-a/eval-engine-metadata.json)
file.

The `reason` should match the one specified in the relevant OPA Policy. Check
out the [policy governing
SQS](./supplementary_files/opa-policies/SQS/sqs_queue_fifo.rego) to compare the
configuration of the `failMeQueue` resource we just proposed with the allowed
values defined by the OPA Policy.

Note that this table can be queried programatically. Check the logs of the
Lambda function prefixed `ControlBrokerEvalEngineCd-EvalEngineWrapper` for the
`EvalResultsTablePk` to query the Eval Results table with. This PK corresponds
to a Step Function execution - each execution creates DynamoDB results table
entries.

So far we've seen compliant IaC (1) pass and noncompliant IaC (2) fail using the
provided OPA Policies.

### (3)

In the final portion of the walkthrough, we'll edit the OPA Policy governing the
evaluation. Let's take the noncompliant SQS Queue from (2) and edit the relevant
OPA Policy so that it now compliant, then we'll send it back through the
Evaluation Pipeline and compare the result.

In our Example App repo, comment out the IaC labeled (1) and (2) and uncomment
section (3).

Notice that we've simple renamed the SQS Queue that just failed in
(2) to `fifoFalseQueueMakeMePass` and left the configuration the same.

Commit this change:

```
git add .
git commit -m "fifoFalseQueueMakeMePass"
```

Now let's edit the OPA relevant Policy to make this non-Fifo Queue compliant.

Within the Root CDK Application (not the example app cloned from CodeCommit!),
let's edit the [sqs\_queue\_fifo.rego](./supplementary_files/opa-policies/SQS/sqs_queue_fifo.rego)
file.

In the `obedient_resources` section, change the allowed Fifo parameter value to:

``` properties.FifoQueue == false ```

To recap, while in sections (1) and (2) we used a OPA Policy that required a SQS
Queue to be Fifo, in section (3) we've edited the Policy to require that same
parameter to be `false`.

Save both files and redepoy: `cdk deploy`.

Then, navigate back to the Evaluation Pipeline in the AWS Console.  Remember
that when we first commited `fifoFalseQueueMakeMePass`, the original OPA Policy
was in place. We expect that to be rejected.

Now that we have redeployed and the changes to the OPA Policy have made their
way to S3, let's run it again.  Select the `Release change` button in the top
right of the AWS Console to re-run the pipeline with that same
`fifoFalseQueueMakeMePass` commit. That same non-Fifo queue should now be
compliant, per the changes we made to the policy. We now expect the Evaluation
Pipeline to succeed.

### Conclusion

This concludes our walkthrough. We examined the relationship between the two
inputs to the Evaluation Pipeline - the Example App and the OPA Policies. We
made alternating changes to the IaC and the OPA Policy to get different results.

Both our Example App and OPA Policies were simple and rather arbitrary for
simplicity's sake. As an organization enters the Policy as Code space, they can
apply the lessons learned here to increasingly sophisticated applications and
security policies.