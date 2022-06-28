import { join } from 'path';
import { Construct } from 'constructs';
import { EvalEngine } from '.';
import { Api } from './api';
import { BaseInputHandler } from './input-handlers';

export interface ControlBrokerProps {
  readonly api?: Api;
}

export class ControlBroker extends Construct {
  public readonly api: Api;
  constructor(scope: Construct, id: string, props: ControlBrokerProps) {
    super(scope, id);
    this.api = props.api ?? new Api(this, `${id}Api`, { evalEngine: new EvalEngine(this, `${id}EvalEngine`) });
  }

  public getUrlForInputHandler(inputHandler: BaseInputHandler) {
    return join(this.api.externalBaseUrl, inputHandler.urlSafeName);
  }
}
