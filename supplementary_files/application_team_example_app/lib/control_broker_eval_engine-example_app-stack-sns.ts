import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import { aws_sns as sns } from 'aws-cdk-lib';
import { aws_sns_subscriptions as snsSubs } from 'aws-cdk-lib';

export class ControlBrokerEvalEngineExampleAppStackSNS extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

  // sns

  // PASS

  const passMeTopic = new sns.Topic(this, 'passMeTopic', {
    displayName: 'passMeTopic',
    topicName: 'passMeTopic',
    contentBasedDeduplication: true,
    fifo: true,
  });
  
  // FAIL
  
  // const failMeTopic = new sns.Topic(this, 'failMeTopic', {
  //   displayName: 'failMeTopic',
  //   topicName: 'failMeTopic',
  //   contentBasedDeduplication: false,
  //   fifo: false,
  // });
  
  // failMeTopic.addSubscription(new snsSubs.UrlSubscription('https://example.com/'));
  
  }
}
