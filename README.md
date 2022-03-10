# AWS Controls Foundation - Evaluation Engine Repository

This is a deep dive on one specific component within Vertical Relevance's 
broader (AWS Control Foundation solution)[https://github.com/VerticalRelevance/ControlFoundations-Blueprint].

This repository deploys a pipeline used by Security team
to evaluate the IaC proposed by an Application team’s CDK application
using a serverless Evaluation Engine.


## Prior to starting the setup of the CDK environment, ensure that you have cloned this repo.

## Follow the setup steps below to properly configure the environment and first deployment of the infrastructure.

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

In the AWS Console, navigate to `CodePipeline` / `Pipelines` and find the pipeline whose name starts with `ControlBrokerEvalEngineCdkStack`. This is our Evaluation Pipeline.

The initial commit occurs when CDK initializes the repository with compliant IaC defined in this directory [Application Team Example App](./supplementary_files/application_team_example_app) of the Root Evaluation Pipeline CDK application. These files serve only to initialize the CodeCommit repository.

See the screenshot below for the expected state of the Evaluation Pipeline upon the initial deployment.

![Screenshot of CodePipeline](./supplementary_files/readme/pipeline-screenshots/initial-commit/initial.png)

The compliant IaC, labeled (1) in the stack, should pass the Evaluation Pipeline.

Now let's modify the Example App to see what happens if we propose noncompliant IaC. 

Check the deployment output for links to clone the Example App CodeCommit repository. See [CodeCommit ssh conection setup](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html).

Once you have cloned the repository, uncomment the `failMe` resource labeled (2) in the SQS stack at path:

```
./supplementary_files/application_team_example_app/lib/control_broker_eval_engine-example_app-stack-sqs.ts 
```

Save the file, then commit to the CodeCommit repository with a commit message like:

```
add failMe resource to SQS stack
```

Return to the CodePipeline console to track the `failMe` commit through the Evaluation Pipeline. It should fail at the EvalEngine stage as seen in the below screenshot.

![Screenshot of CodePipeline](./supplementary_files/readme/pipeline-screenshots/fail-me/fail.png)

Let's see the result of the Evaluation. In the AWS Console, navigate to `DynamoDB` / `Tables` and find the table whose name starts with `ControlBrokerEvalEngineCdkStack-EvalResults`. These are results of the Evaluation Pipeline.
Select `ExploreTableItems`. The evaluation results of the `failMe` commit should appear here, including the `reason` the IaC was denied and the metadata defined in the [pipeline-ownership-metadata](/ControlBrokerEvalEngine-Blueprint/supplementary_files/pipeline-ownership-metadata/business-unit-a/eval-engine-metadata.json) file.

The `reason` should match the one specified in the relevant OPA Policy. Check out the [policies governing SQS](./supplementary_files/opa-policies/SQS) to compare the configuration of the `failMe` resource we just proposed with the allowed values defined by the OPA Policy.

So far we've seen the initial commit with compliant IaC (1) pass and noncompliant IaC (2) fail using the provided OPA Policies.

Finally, let's uncomment the IaC labeled (3). Here we've renamed the SQS Queue that just failed in (2) to `fifoQueueMakeMePass`. Let's edit the OPA relevant Policies so that the Evaluation Pipeline passes this resource instead.