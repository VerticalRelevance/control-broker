import { BaseInputHandler } from '.';

export class CloudFormationInputHandler extends BaseInputHandler {
  public get urlSafeName(): string {
    return 'CloudFormation';
  }
}
