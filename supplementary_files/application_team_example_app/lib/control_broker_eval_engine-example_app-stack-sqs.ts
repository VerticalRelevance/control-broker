import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import { aws_sqs as sqs } from 'aws-cdk-lib';

export class ControlBrokerEvalEngineExampleAppStackSQS extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

  // sqs
  
  // (1) PASS
  
  const passMeQueue = new sqs.Queue(this, 'passMeQueue', {
    fifo: true,
    contentBasedDeduplication: true
  });
  
  // (2) FAIL
  
  // const failMeQueue = new sqs.Queue(this, 'failMeQueue', {
  //   fifo: false,
    // contentBasedDeduplication: false
  // });
  
  // (3) EDIT OPA POLICIES TO PASS
  
  // const fifoFalseQueueMakeMePass = new sqs.Queue(this, 'fifoFalseQueueMakeMePass', {
  //   fifo: false,
  // });
  
  }
}
