import { Construct } from 'constructs';
import { IIntegrationTarget, IntegrationTargetType } from '../interfaces';

export abstract class BaseInputHandler extends Construct implements IIntegrationTarget {
  public abstract readonly integrationTargetType: IntegrationTargetType;

  /**
   * Return a name for this input handler that is safe for use in the
   * path of a URL.
   */
  public abstract get urlSafeName(): string;
  /**
   * ARN of the principal that will call the EvalEngine endpoint.
   */
  public abstract get evalEngineCallerPrincipalArn(): string;
}
