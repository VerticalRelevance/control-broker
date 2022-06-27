const { awscdk } = require('projen');
const project = new awscdk.AwsCdkConstructLibrary({
  author: 'Clark Schneider',
  authorAddress: 'cschneider@verticalrelevance.com',
  cdkVersion: '2.28.1',
  defaultReleaseBranch: 'main',
  name: 'control-broker',
  repositoryUrl: 'git@github.com:verticalrelevance/control-broker',
  typescriptVersion: '4.7.3',
  deps: ['@aws-cdk/aws-apigatewayv2-alpha@2.28.1-alpha.0'],
  description:
    'Control Broker allows customers to deploy an HTTP API on AWS that executes Policy as Code (PaC) policies using Open Policy Agent (OPA) or CloudFormation Guard to evaluate inputs and return results. Control Broker is an event-driven, serverless AWS-based API created by Vertical Relevance (VR). Control Broker is a VR Module, which is a ready-to-deploy infrastructure solution that implements a portion of VR’s Control Foundations Solution. Control Broker comes with examples and defaults that can help organizations get started in using PaC on AWS.',
  packageName: 'control-broker',
  peerDeps: ['@aws-cdk/aws-apigatewayv2-alpha@2.28.1-alpha.0'],
});
project.addDevDeps('@types/jest@^27.0.0', 'prettier-eslint');
project.synth();
