# API Reference <a name="API Reference" id="api-reference"></a>

## Constructs <a name="Constructs" id="Constructs"></a>

### Api <a name="Api" id="control-broker.Api"></a>

#### Initializers <a name="Initializers" id="control-broker.Api.Initializer"></a>

```typescript
import { Api } from 'control-broker'

new Api(scope: Construct, id: string, props?: HttpApiProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.Api.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#control-broker.Api.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.Api.Initializer.parameter.props">props</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.HttpApiProps</code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.Api.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.Api.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.Initializer.parameter.props"></a>

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.HttpApiProps

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.Api.toString">toString</a></code> | Returns a string representation of this construct. |
| <code><a href="#control-broker.Api.applyRemovalPolicy">applyRemovalPolicy</a></code> | Apply the given removal policy to this resource. |
| <code><a href="#control-broker.Api.addRoutes">addRoutes</a></code> | Add multiple routes that uses the same configuration. |
| <code><a href="#control-broker.Api.addStage">addStage</a></code> | Add a new stage. |
| <code><a href="#control-broker.Api.addVpcLink">addVpcLink</a></code> | Add a new VpcLink. |
| <code><a href="#control-broker.Api.metric">metric</a></code> | Return the given named metric for this Api Gateway. |
| <code><a href="#control-broker.Api.metricClientError">metricClientError</a></code> | Metric for the number of client-side errors captured in a given period. |
| <code><a href="#control-broker.Api.metricCount">metricCount</a></code> | Metric for the total number API requests in a given period. |
| <code><a href="#control-broker.Api.metricDataProcessed">metricDataProcessed</a></code> | Metric for the amount of data processed in bytes. |
| <code><a href="#control-broker.Api.metricIntegrationLatency">metricIntegrationLatency</a></code> | Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend. |
| <code><a href="#control-broker.Api.metricLatency">metricLatency</a></code> | The time between when API Gateway receives a request from a client and when it returns a response to the client. |
| <code><a href="#control-broker.Api.metricServerError">metricServerError</a></code> | Metric for the number of server-side errors captured in a given period. |

---

##### `toString` <a name="toString" id="control-broker.Api.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

##### `applyRemovalPolicy` <a name="applyRemovalPolicy" id="control-broker.Api.applyRemovalPolicy"></a>

```typescript
public applyRemovalPolicy(policy: RemovalPolicy): void
```

Apply the given removal policy to this resource.

The Removal Policy controls what happens to this resource when it stops
being managed by CloudFormation, either because you've removed it from the
CDK application or because you've made a change that requires the resource
to be replaced.

The resource can be deleted (`RemovalPolicy.DESTROY`), or left in your AWS
account for data recovery and cleanup later (`RemovalPolicy.RETAIN`).

###### `policy`<sup>Required</sup> <a name="policy" id="control-broker.Api.applyRemovalPolicy.parameter.policy"></a>

- *Type:* aws-cdk-lib.RemovalPolicy

---

##### `addRoutes` <a name="addRoutes" id="control-broker.Api.addRoutes"></a>

```typescript
public addRoutes(options: AddRoutesOptions): HttpRoute[]
```

Add multiple routes that uses the same configuration.

The routes all go to the same path, but for different
methods.

###### `options`<sup>Required</sup> <a name="options" id="control-broker.Api.addRoutes.parameter.options"></a>

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.AddRoutesOptions

---

##### `addStage` <a name="addStage" id="control-broker.Api.addStage"></a>

```typescript
public addStage(id: string, options: HttpStageOptions): HttpStage
```

Add a new stage.

###### `id`<sup>Required</sup> <a name="id" id="control-broker.Api.addStage.parameter.id"></a>

- *Type:* string

---

###### `options`<sup>Required</sup> <a name="options" id="control-broker.Api.addStage.parameter.options"></a>

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.HttpStageOptions

---

##### `addVpcLink` <a name="addVpcLink" id="control-broker.Api.addVpcLink"></a>

```typescript
public addVpcLink(options: VpcLinkProps): VpcLink
```

Add a new VpcLink.

###### `options`<sup>Required</sup> <a name="options" id="control-broker.Api.addVpcLink.parameter.options"></a>

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.VpcLinkProps

---

##### `metric` <a name="metric" id="control-broker.Api.metric"></a>

```typescript
public metric(metricName: string, props?: MetricOptions): Metric
```

Return the given named metric for this Api Gateway.

###### `metricName`<sup>Required</sup> <a name="metricName" id="control-broker.Api.metric.parameter.metricName"></a>

- *Type:* string

---

###### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.metric.parameter.props"></a>

- *Type:* aws-cdk-lib.aws_cloudwatch.MetricOptions

---

##### `metricClientError` <a name="metricClientError" id="control-broker.Api.metricClientError"></a>

```typescript
public metricClientError(props?: MetricOptions): Metric
```

Metric for the number of client-side errors captured in a given period.

###### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.metricClientError.parameter.props"></a>

- *Type:* aws-cdk-lib.aws_cloudwatch.MetricOptions

---

##### `metricCount` <a name="metricCount" id="control-broker.Api.metricCount"></a>

```typescript
public metricCount(props?: MetricOptions): Metric
```

Metric for the total number API requests in a given period.

###### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.metricCount.parameter.props"></a>

- *Type:* aws-cdk-lib.aws_cloudwatch.MetricOptions

---

##### `metricDataProcessed` <a name="metricDataProcessed" id="control-broker.Api.metricDataProcessed"></a>

```typescript
public metricDataProcessed(props?: MetricOptions): Metric
```

Metric for the amount of data processed in bytes.

###### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.metricDataProcessed.parameter.props"></a>

- *Type:* aws-cdk-lib.aws_cloudwatch.MetricOptions

---

##### `metricIntegrationLatency` <a name="metricIntegrationLatency" id="control-broker.Api.metricIntegrationLatency"></a>

```typescript
public metricIntegrationLatency(props?: MetricOptions): Metric
```

Metric for the time between when API Gateway relays a request to the backend and when it receives a response from the backend.

###### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.metricIntegrationLatency.parameter.props"></a>

- *Type:* aws-cdk-lib.aws_cloudwatch.MetricOptions

---

##### `metricLatency` <a name="metricLatency" id="control-broker.Api.metricLatency"></a>

```typescript
public metricLatency(props?: MetricOptions): Metric
```

The time between when API Gateway receives a request from a client and when it returns a response to the client.

The latency includes the integration latency and other API Gateway overhead.

###### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.metricLatency.parameter.props"></a>

- *Type:* aws-cdk-lib.aws_cloudwatch.MetricOptions

---

##### `metricServerError` <a name="metricServerError" id="control-broker.Api.metricServerError"></a>

```typescript
public metricServerError(props?: MetricOptions): Metric
```

Metric for the number of server-side errors captured in a given period.

###### `props`<sup>Optional</sup> <a name="props" id="control-broker.Api.metricServerError.parameter.props"></a>

- *Type:* aws-cdk-lib.aws_cloudwatch.MetricOptions

---

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.Api.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |
| <code><a href="#control-broker.Api.isResource">isResource</a></code> | Check whether the given construct is a Resource. |
| <code><a href="#control-broker.Api.fromHttpApiAttributes">fromHttpApiAttributes</a></code> | Import an existing HTTP API into this CDK app. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="control-broker.Api.isConstruct"></a>

```typescript
import { Api } from 'control-broker'

Api.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="control-broker.Api.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

##### `isResource` <a name="isResource" id="control-broker.Api.isResource"></a>

```typescript
import { Api } from 'control-broker'

Api.isResource(construct: IConstruct)
```

Check whether the given construct is a Resource.

###### `construct`<sup>Required</sup> <a name="construct" id="control-broker.Api.isResource.parameter.construct"></a>

- *Type:* constructs.IConstruct

---

##### `fromHttpApiAttributes` <a name="fromHttpApiAttributes" id="control-broker.Api.fromHttpApiAttributes"></a>

```typescript
import { Api } from 'control-broker'

Api.fromHttpApiAttributes(scope: Construct, id: string, attrs: HttpApiAttributes)
```

Import an existing HTTP API into this CDK app.

###### `scope`<sup>Required</sup> <a name="scope" id="control-broker.Api.fromHttpApiAttributes.parameter.scope"></a>

- *Type:* constructs.Construct

---

###### `id`<sup>Required</sup> <a name="id" id="control-broker.Api.fromHttpApiAttributes.parameter.id"></a>

- *Type:* string

---

###### `attrs`<sup>Required</sup> <a name="attrs" id="control-broker.Api.fromHttpApiAttributes.parameter.attrs"></a>

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.HttpApiAttributes

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.Api.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#control-broker.Api.property.env">env</a></code> | <code>aws-cdk-lib.ResourceEnvironment</code> | The environment this resource belongs to. |
| <code><a href="#control-broker.Api.property.stack">stack</a></code> | <code>aws-cdk-lib.Stack</code> | The stack in which this resource is defined. |
| <code><a href="#control-broker.Api.property.apiEndpoint">apiEndpoint</a></code> | <code>string</code> | Get the default endpoint for this API. |
| <code><a href="#control-broker.Api.property.apiId">apiId</a></code> | <code>string</code> | The identifier of this API Gateway API. |
| <code><a href="#control-broker.Api.property.httpApiId">httpApiId</a></code> | <code>string</code> | The identifier of this API Gateway HTTP API. |
| <code><a href="#control-broker.Api.property.defaultStage">defaultStage</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.IHttpStage</code> | The default stage of this API. |
| <code><a href="#control-broker.Api.property.disableExecuteApiEndpoint">disableExecuteApiEndpoint</a></code> | <code>boolean</code> | Specifies whether clients can invoke this HTTP API by using the default execute-api endpoint. |
| <code><a href="#control-broker.Api.property.httpApiName">httpApiName</a></code> | <code>string</code> | A human friendly name for this HTTP API. |
| <code><a href="#control-broker.Api.property.url">url</a></code> | <code>string</code> | Get the URL to the default stage of this API. |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.Api.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `env`<sup>Required</sup> <a name="env" id="control-broker.Api.property.env"></a>

```typescript
public readonly env: ResourceEnvironment;
```

- *Type:* aws-cdk-lib.ResourceEnvironment

The environment this resource belongs to.

For resources that are created and managed by the CDK
(generally, those created by creating new class instances like Role, Bucket, etc.),
this is always the same as the environment of the stack they belong to;
however, for imported resources
(those obtained from static methods like fromRoleArn, fromBucketName, etc.),
that might be different than the stack they were imported into.

---

##### `stack`<sup>Required</sup> <a name="stack" id="control-broker.Api.property.stack"></a>

```typescript
public readonly stack: Stack;
```

- *Type:* aws-cdk-lib.Stack

The stack in which this resource is defined.

---

##### `apiEndpoint`<sup>Required</sup> <a name="apiEndpoint" id="control-broker.Api.property.apiEndpoint"></a>

```typescript
public readonly apiEndpoint: string;
```

- *Type:* string

Get the default endpoint for this API.

---

##### `apiId`<sup>Required</sup> <a name="apiId" id="control-broker.Api.property.apiId"></a>

```typescript
public readonly apiId: string;
```

- *Type:* string

The identifier of this API Gateway API.

---

##### `httpApiId`<sup>Required</sup> <a name="httpApiId" id="control-broker.Api.property.httpApiId"></a>

```typescript
public readonly httpApiId: string;
```

- *Type:* string

The identifier of this API Gateway HTTP API.

---

##### `defaultStage`<sup>Optional</sup> <a name="defaultStage" id="control-broker.Api.property.defaultStage"></a>

```typescript
public readonly defaultStage: IHttpStage;
```

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.IHttpStage

The default stage of this API.

---

##### `disableExecuteApiEndpoint`<sup>Optional</sup> <a name="disableExecuteApiEndpoint" id="control-broker.Api.property.disableExecuteApiEndpoint"></a>

```typescript
public readonly disableExecuteApiEndpoint: boolean;
```

- *Type:* boolean

Specifies whether clients can invoke this HTTP API by using the default execute-api endpoint.

---

##### `httpApiName`<sup>Optional</sup> <a name="httpApiName" id="control-broker.Api.property.httpApiName"></a>

```typescript
public readonly httpApiName: string;
```

- *Type:* string

A human friendly name for this HTTP API.

Note that this is different from `httpApiId`.

---

##### `url`<sup>Optional</sup> <a name="url" id="control-broker.Api.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

Get the URL to the default stage of this API.

Returns `undefined` if `createDefaultStage` is unset.

---



## Classes <a name="Classes" id="Classes"></a>

### ControlBroker <a name="ControlBroker" id="control-broker.ControlBroker"></a>

#### Initializers <a name="Initializers" id="control-broker.ControlBroker.Initializer"></a>

```typescript
import { ControlBroker } from 'control-broker'

new ControlBroker()
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |

---






