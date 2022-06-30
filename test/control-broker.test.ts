import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { Stack } from 'aws-cdk-lib';
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
  };
});

test('ControlBroker can be created and attached to a stack', () => {
  const stack = new Stack();
  const api = new Api(stack, 'ControlbrokerApi', {});
  const cfnInputHandler = new CloudFormationInputHandler(stack, 'CfnInputHandler');
  const cfnInputHandlerApiBinding = new HttpApiBinding('CloudFormation', api, cfnInputHandler);
  const evalEngine = new OpaEvalEngine(stack, 'EvalEngine');
  const evalEngineBinding = new HttpApiBinding('EvalEngine', api, evalEngine);
  expect(mockedPythonFunction).toHaveBeenCalled();
  api.setEvalEngine(evalEngine, evalEngineBinding);
  api.addInputHandler(cfnInputHandler, cfnInputHandlerApiBinding);
  new ControlBroker(stack, 'TestControlBroker', {
    api,
  });
});
