import { ILambdaIntegrationTarget, IntegrationTargetType } from '../interfaces/integration-target-interface';

export function isLambdaIntegrationTarget(object: any): object is ILambdaIntegrationTarget {
  return object.integrationTargetType === IntegrationTargetType.LAMBDA;
}
