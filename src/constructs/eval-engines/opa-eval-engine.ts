import { join } from 'path';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { Duration } from 'aws-cdk-lib';
import { Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { BaseEvalEngine } from '.';
import { ILambdaIntegrationTarget, IntegrationTargetType } from '../interfaces';

export class OpaEvalEngine extends BaseEvalEngine implements ILambdaIntegrationTarget {
  public readonly integrationTargetType: IntegrationTargetType = IntegrationTargetType.LAMBDA;
  public readonly handler: Function;

  constructor(scope: Construct, id: string) {
    super(scope, id);
    this.handler = new PythonFunction(this, `${id}OpaEvalEngineLambdaFunction`, {
      entry: join(__dirname, 'lambda-function-code/opa-eval-engine/'),
      runtime: Runtime.PYTHON_3_9,
      index: 'lambda_function.py',
      handler: 'lambda_handler',
      timeout: Duration.seconds(60),
    });
  }
}