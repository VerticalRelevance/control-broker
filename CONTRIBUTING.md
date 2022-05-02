# control-broker

## license

\#TODO

## testing

\#WIP, see [here](./tests/functional/test_cfn_inputs.py)

## git strategy

per EP, issue with descriptive name -> branch name auto-generated from GUI -> every commit message references that issue:

`Issue #N MY_COMMIT_MESSAGE`

## orientation 5.2.22

clone control-broker at `3-implement-asynchronous-client-layer`

`cdk deploy`

clone [control-broker-codepipeline-example](https://github.com/VerticalRelevance/control-broker-codepipeline-example)

add outputs from original `control-broker` deployment output to `cdk.json` of `control-broker-codepipeline-example`

`cdk deploy`

initial commit to CodeCommit repo should have noncompliant IaC

pipeline should fail

comment out `failMeQueue`, commit it, it should pass

### orientation checklist

- [ ] toggle code input to get different results
- [ ] toggle PaC files, redeploy to get different results
- [ ] check s3 for ResultsReport
- [ ] check ddb for logging
- [ ] see [Issue #4](https://github.com/VerticalRelevance/control-broker/issues/4) for API Contract
- 
### advanced

- [ ] create a EventBridge rule that listens for a type of violation