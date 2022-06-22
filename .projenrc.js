const { awscdk } = require("projen");
const project = new awscdk.AwsCdkConstructLibrary({
  author: "Clark Schneider",
  authorAddress: "cschneider@verticalrelevance.com",
  cdkVersion: "2.28.1",
  defaultReleaseBranch: "main",
  name: "control-broker",
  repositoryUrl: "git@github.com:verticalrelevance/control-broker",
  typescriptVersion: "4.7.3",

  // deps: [],                /* Runtime dependencies of this module. */
  // description: undefined,  /* The description is just a string that helps people understand the purpose of the package. */
  // devDeps: [],             /* Build dependencies for this module. */
  // packageName: undefined,  /* The "name" in package.json. */
});
project.addDevDeps("@types/jest==^27.0.0");
project.synth();