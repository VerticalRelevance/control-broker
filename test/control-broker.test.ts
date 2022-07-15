import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { Stack } from 'aws-cdk-lib';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { Api, ControlBroker, OpaEvalEngine } from '../src';
import { HttpApiBinding } from '../src/constructs/api-bindings';
import { CloudFormationInputHandler } from '../src/constructs/input-handlers';

jest.mock('@aws-cdk/aws-lambda-python-alpha');

const mockedPythonFunction = <jest.Mock<typeof PythonFunction>>(PythonFunction as unknown);
mockedPythonFunction.mockImplementation(() => {
  const original = jest.requireActual('@aws-cdk/aws-lambda-python-alpha');
  return {
    ...original.PythonFunction,
    functionArn: 'arn:aws:lambda:us-east-1:123456789012:function:mockfunction',
    addPermission: () => {},
    addEnvironment: () => {},
  };
});

test('ControlBroker can be created and attached to a stack', () => {
  const stack = new Stack();
  const api = new Api(stack, 'ControlbrokerApi', {});
  const cfnInputHandlerApiBinding = new HttpApiBinding('CloudFormation');
  const cfnInputHandler = new CloudFormationInputHandler(stack, 'CfnInputHandler', { binding: cfnInputHandlerApiBinding });
  const evalEngineBinding = new HttpApiBinding('EvalEngine');
  const evalEngine = new OpaEvalEngine(stack, 'EvalEngine', { binding: evalEngineBinding });
  expect(mockedPythonFunction).toHaveBeenCalled();
  const inputBucket = new Bucket(stack, 'CBInputBucket', {});
  new ControlBroker(stack, 'TestControlBroker', {
    api,
    inputBucket,
    evalEngine,
    inputHandlers: [cfnInputHandler],
  });
});
