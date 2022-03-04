import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import { aws_sqs as sqs } from 'aws-cdk-lib';

export class ControlBrokerEvalEngineExampleAppStackSQS extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

  // sqs
  
  // PASS
  
  const passMeQueue = new sqs.Queue(this, 'passMeQueue', {
    fifo: true,
    contentBasedDeduplication: true,
  });
  
  // FAIL
  
  const failMeQueue = new sqs.Queue(this, 'failMeQueue', {
    fifo: false,
  });
  
  }
}
