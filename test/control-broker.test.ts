import { Stack } from 'aws-cdk-lib';
import { ControlBroker } from '../src';

test('ControlBroker can be created and attached to a stack', () => {
  const stack = new Stack();
  new ControlBroker(stack, 'TestControlBroker');
});