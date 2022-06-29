import { join } from 'path';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { Duration } from 'aws-cdk-lib';
import { Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { BaseInputHandler } from '.';
import { ILambdaIntegrationTarget, IntegrationTargetType } from '../interfaces';

export class CloudFormationInputHandler extends BaseInputHandler implements ILambdaIntegrationTarget {
  public readonly integrationTargetType: IntegrationTargetType = IntegrationTargetType.LAMBDA;
  public readonly handler: Function;

  constructor(scope: Construct, id: string) {
    super(scope, id);
    this.handler = new PythonFunction(this, `${id}CloudFormationInputHandler`, {
      entry: join(__dirname, 'lambda-function-code/cloudformation-input-handler'),
      runtime: Runtime.PYTHON_3_9,
      index: 'lambda_function.py',
      handler: 'lambda_handler',
      timeout: Duration.seconds(60),
    });
  }

  public get evalEngineCallerPrincipalArn(): string {
    return this.handler.functionArn;
  }

  public get urlSafeName(): string {
    return 'CloudFormation';
  }
}
