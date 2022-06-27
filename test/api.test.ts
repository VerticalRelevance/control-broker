import { Stack } from 'aws-cdk-lib';
import { Api } from '../src';

test('Can import Api from main package and attach to a stack', () => {
  const stack = new Stack();
  new Api(stack, 'TestApi');
});