import { Function } from 'aws-cdk-lib/aws-lambda';
import { BaseApiBinding } from '../api-bindings';

export enum IntegrationTargetType {
  LAMBDA,
  STEP_FUNCTION,
}

export interface IIntegrationTarget {
  readonly integrationTargetType: IntegrationTargetType;
  readonly binding: BaseApiBinding<any>;
}

export interface ILambdaIntegrationTarget extends IIntegrationTarget {
  readonly handler: Function;
}
