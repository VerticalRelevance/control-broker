import { Construct } from 'constructs';
import { BaseApiBinding } from '../api-bindings';
import { IIntegrationTarget, IntegrationTargetType } from '../interfaces';

export interface BaseEvalEngineProps {
  readonly binding: BaseApiBinding<any>;
}

export abstract class BaseEvalEngine extends Construct implements IIntegrationTarget {
  public readonly abstract integrationTargetType: IntegrationTargetType;
  public readonly binding: BaseApiBinding<any>;

  public constructor(scope: Construct, id: string, props: BaseEvalEngineProps) {
    super(scope, id);
    this.binding = props.binding;
  }

  public authorizePrincipalArn(principalArn: string) {
    this.binding.authorizePrincipalArn(principalArn);
  }
}
