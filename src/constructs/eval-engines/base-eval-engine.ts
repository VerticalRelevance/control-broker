import { Construct } from 'constructs';
import { IIntegrationTarget, IntegrationTargetType } from '../interfaces';

export abstract class BaseEvalEngine extends Construct implements IIntegrationTarget {
  public readonly abstract integrationTargetType: IntegrationTargetType;
}