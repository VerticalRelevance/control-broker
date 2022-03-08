#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ControlBrokerEvalEngineExampleAppStackSNS } from '../lib/control_broker_eval_engine-example_app-stack-sns';
import { ControlBrokerEvalEngineExampleAppStackSQS } from '../lib/control_broker_eval_engine-example_app-stack-sqs';

const app = new cdk.App();

new ControlBrokerEvalEngineExampleAppStackSNS(app, 'ControlBrokerEvalEngineExampleAppStackSNS', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});

new ControlBrokerEvalEngineExampleAppStackSQS(app, 'ControlBrokerEvalEngineExampleAppStackSQS', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});