import { Stack } from 'aws-cdk-lib';
import { Api, ControlBroker, OpaEvalEngine } from '../src';
import { HttpApiBinding } from '../src/constructs/api-bindings';
import { CloudFormationInputHandler } from '../src/constructs/input-handlers';

test('ControlBroker can be created and attached to a stack', () => {
  const stack = new Stack();
  const api = new Api(stack, 'ControlbrokerApi', {});
  const cfnInputHandler = new CloudFormationInputHandler(stack, 'CfnInputHandler');
  const cfnInputHandlerApiBinding = new HttpApiBinding('CloudFormation', api, cfnInputHandler);
  const evalEngine = new OpaEvalEngine(stack, 'EvalEngine');
  const evalEngineBinding = new HttpApiBinding('EvalEngine', api, evalEngine);
  api.setEvalEngine(evalEngine, evalEngineBinding);
  api.addInputHandler(cfnInputHandler, cfnInputHandlerApiBinding);
  new ControlBroker(stack, 'TestControlBroker', {
    api,
  });
});
