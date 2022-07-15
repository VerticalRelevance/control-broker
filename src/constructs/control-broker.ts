import { CfnOutput } from 'aws-cdk-lib';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';
import { BaseEvalEngine } from '.';
import { Api } from './api';
import { BaseInputHandler } from './input-handlers';

export interface ControlBrokerProps {
  readonly api: Api;
  readonly inputBucket: Bucket;
  readonly evalEngine: BaseEvalEngine;
  readonly inputHandlers: BaseInputHandler[];
}

/**
 * Parameters that components of Control Broker may need.
 */
export interface ControlBrokerParams {
  readonly inputBucket: Bucket;
}

export class ControlBroker extends Construct {
  public readonly api: Api;
  protected readonly params: ControlBrokerParams;
  constructor(scope: Construct, id: string, props: ControlBrokerProps) {
    super(scope, id);
    this.api = props.api;
    this.params = {
      inputBucket: props.inputBucket,
    };
    this.evalEngine = props.evalEngine;
    props.inputHandlers.forEach((ih) => this.addInputHandler(ih));
    new CfnOutput(this, 'InputBucketName', { value: props.inputBucket.bucketName });
  }

  public addInputHandler(inputHandler: BaseInputHandler) {
    this.api.addInputHandler(inputHandler);
    inputHandler.controlBrokerParams = this.params;
    return this.getUrlForInputHandler(inputHandler);
  }

  public getUrlForInputHandler(inputHandler: BaseInputHandler) {
    return this.api.getUrlForInputHandler(inputHandler);
  }

  public set evalEngine(evalEngine: BaseEvalEngine | undefined) {
    this.api.evalEngine = evalEngine;
  }
}
