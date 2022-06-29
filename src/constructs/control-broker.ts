import { Construct } from 'constructs';
import { Api } from './api';
import { BaseInputHandler } from './input-handlers';

export interface ControlBrokerProps {
  readonly api: Api;
}

export class ControlBroker extends Construct {
  public readonly api: Api;
  constructor(scope: Construct, id: string, props: ControlBrokerProps) {
    super(scope, id);
    this.api = props.api;
  }

  public getUrlForInputHandler(inputHandler: BaseInputHandler) {
    return this.api.getUrlForInputHandler(inputHandler);
  }
}
