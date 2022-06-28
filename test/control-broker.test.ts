import { Stack } from 'aws-cdk-lib';
import { Api, ControlBroker, EvalEngine } from '../src';

test('ControlBroker can be created and attached to a stack', () => {
  const stack = new Stack();
  const evalEngine = new EvalEngine(stack, 'ControlBrokerEvalEngine');
  const api = new Api(stack, 'ControlbrokerApi', { evalEngine });
  new ControlBroker(stack, 'TestControlBroker', {
    api,
  });
});
