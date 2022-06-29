const { awscdk } = require('projen');
const project = new awscdk.AwsCdkConstructLibrary({
  author: 'Clark Schneider',
  authorAddress: 'cschneider@verticalrelevance.com',
  cdkVersion: '2.28.1',
  defaultReleaseBranch: 'main',
  releaseBranches: { release: { majorVersion: 0 } },
  name: 'control-broker',
  repositoryUrl: 'https://github.com/VerticalRelevance/control-broker.git',
  typescriptVersion: '4.7.3',
  deps: [
    '@aws-cdk/aws-apigatewayv2-alpha@2.28.1-alpha.0',
    '@aws-cdk/aws-apigatewayv2-integrations-alpha@2.28.1-alpha.0',
    '@aws-cdk/aws-apigatewayv2-authorizers-alpha@2.28.1-alpha.0',
    '@aws-cdk/aws-lambda-python-alpha@2.28.1-alpha.0',
  ],
  description:
    'Control Broker allows customers to deploy an HTTP API on AWS that executes Policy as Code (PaC) policies using Open Policy Agent (OPA) or CloudFormation Guard to evaluate inputs and return decisions.',
  packageName: 'control-broker',
  peerDeps: [
    '@aws-cdk/aws-apigatewayv2-alpha@2.28.1-alpha.0',
    '@aws-cdk/aws-apigatewayv2-integrations-alpha@2.28.1-alpha.0',
    '@aws-cdk/aws-apigatewayv2-authorizers-alpha@2.28.1-alpha.0',
    '@aws-cdk/aws-lambda-python-alpha@2.28.1-alpha.0',
  ],
  publishToPypi: {
    distName: 'control-broker',
    module: 'control_broker',
  },
  homepage: 'https://github.com/VerticalRelevance/control-broker/',
});

project.addDevDeps('@types/jest@^27.0.0', 'prettier-eslint');
const releaseWorkflowFiles = [
  project.tryFindObjectFile('.github/workflows/release-release.yml'),
  project.tryFindObjectFile('.github/workflows/release.yml'),
];
const buildWorkflowFiles = [
  project.tryFindObjectFile('.github/workflows/build.yml'),
];
const upgradeWorkflowFiles = [
  project.tryFindObjectFile('.github/workflows/upgrade-release.yml'),
  project.tryFindObjectFile('.github/workflows/upgrade-main.yml'),
];
const dockerSocketVolumes = ['/var/run/docker.sock:/var/run/docker.sock'];

releaseWorkflowFiles.forEach((f) => {
  // Add environment specification that causes the release workflow to run in the context of the "npm" GitHub environment,
  // which contains the required NPM_TOKEN, and do the same for PyPI
  f.addOverride('jobs.release_npm.environment', 'npm');
  f.addOverride('jobs.release_pypi.environment', 'pypi');
  // Give access to the docker daemon from inside the container this job runs in
  // so that it can build CDK assets
  f.addOverride('jobs.release.container.volumes', dockerSocketVolumes);
});
buildWorkflowFiles.forEach((f) => f.addOverride('jobs.build.container.volumes', dockerSocketVolumes));
upgradeWorkflowFiles.forEach((f) => f.addOverride('jobs.upgrade.container.volumes', dockerSocketVolumes));
project.synth();
