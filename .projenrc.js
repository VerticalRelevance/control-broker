const { awscdk } = require('projen');
const project = new awscdk.AwsCdkConstructLibrary({
  author: 'Clark Schneider',
  authorAddress: 'cschneider@verticalrelevance.com',
  cdkVersion: '2.28.1',
  defaultReleaseBranch: 'main',
  releaseBranches: { release: { majorVersion: 0 } },
  name: 'control-broker',
  repositoryUrl: 'git@github.com:verticalrelevance/control-broker',
  typescriptVersion: '4.7.3',
  deps: ['@aws-cdk/aws-apigatewayv2-alpha@2.28.1-alpha.0'],
  description:
    'Control Broker allows customers to deploy an HTTP API on AWS that executes Policy as Code (PaC) policies using Open Policy Agent (OPA) or CloudFormation Guard to evaluate inputs and return decisions.',
  packageName: 'control-broker',
  peerDeps: ['@aws-cdk/aws-apigatewayv2-alpha@2.28.1-alpha.0'],
});
project.addDevDeps('@types/jest@^27.0.0', 'prettier-eslint');
// Add environment specification that causes the release workflow to run in the context of the "npm" GitHub environment,
// which contains the required NPM_TOKEN
project.tryFindObjectFile('.github/workflows/release-release.yml').addOverride('jobs.release_npm.environment', 'npm');
project.tryFindObjectFile('.github/workflows/release.yml').addOverride('jobs.release_npm.environment', 'npm');
project.synth();
