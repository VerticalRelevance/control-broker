import { Construct } from 'constructs';
import { Api } from '../api';
import { BaseApiBinding } from '../api-bindings';
import { ControlBrokerParams } from '../control-broker';
import { IIntegrationTarget, IntegrationTargetType } from '../interfaces';

export interface BaseInputHandlerProps {
  readonly binding: BaseApiBinding<any>;
}

export abstract class BaseInputHandler extends Construct implements IIntegrationTarget {
  public abstract readonly integrationTargetType: IntegrationTargetType;
  public readonly binding: BaseApiBinding<any>;

  constructor (scope: Construct, id: string, props: BaseInputHandlerProps) {
    super(scope, id);
    this.binding = props.binding;
  }

  /**
   * Return a name for this input handler that is safe for use in the
   * path of a URL.
   */
  public abstract get urlSafeName(): string;
  /**
   * ARN of the principal that will call the EvalEngine endpoint.
   */
  public abstract get evalEngineCallerPrincipalArn(): string;

  public abstract bindToApi(api: Api): void;

  public get url() {
    return this.binding.url;
  }

  public abstract set controlBrokerParams(params: ControlBrokerParams);
}
