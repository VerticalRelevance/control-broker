import { Function } from 'aws-cdk-lib/aws-lambda';

export enum IntegrationTargetType {
  LAMBDA,
  STEP_FUNCTION,
}

export interface IIntegrationTarget {
  readonly integrationTargetType: IntegrationTargetType;
}

export interface ILambdaIntegrationTarget extends IIntegrationTarget {
  readonly handler: Function;
}