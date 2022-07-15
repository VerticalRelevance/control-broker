#!/usr/bin/env node

import * as cdk from 'aws-cdk-lib';
import { Stack } from 'aws-cdk-lib';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { Api, CloudFormationInputHandler, HttpApiBinding, ControlBroker, OpaEvalEngine } from '../constructs';

const app = new cdk.App();
const stack = new Stack(app, 'ControlBroker');

const api = new Api(stack, 'ControlbrokerApi', {});
const cfnInputHandlerApiBinding = new HttpApiBinding('CloudFormation');
const cfnInputHandler = new CloudFormationInputHandler(stack, 'CfnInputHandler', { binding: cfnInputHandlerApiBinding });
const evalEngineBinding = new HttpApiBinding('EvalEngine');
const evalEngine = new OpaEvalEngine(stack, 'EvalEngine', { binding: evalEngineBinding });
new ControlBroker(stack, 'TestControlBroker', {
  api,
  inputBucket: new Bucket(stack, 'InputBucket'),
  evalEngine,
  inputHandlers: [cfnInputHandler],
});
