# API Reference <a name="API Reference" id="api-reference"></a>

## Constructs <a name="Constructs" id="Constructs"></a>

### Api <a name="Api" id="control-broker.Api"></a>

#### Initializers <a name="Initializers" id="control-broker.Api.Initializer"></a>

```typescript
import { Api } from 'control-broker'

new Api(scope: Construct, id: string, props: ApiProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.Api.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#control-broker.Api.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.Api.Initializer.parameter.props">props</a></code> | <code><a href="#control-broker.ApiProps">ApiProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.Api.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.Api.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="control-broker.Api.Initializer.parameter.props"></a>

- *Type:* <a href="#control-broker.ApiProps">ApiProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.Api.toString">toString</a></code> | Returns a string representation of this construct. |
| <code><a href="#control-broker.Api.addInputHandler">addInputHandler</a></code> | *No description.* |
| <code><a href="#control-broker.Api.getUrlForInputHandler">getUrlForInputHandler</a></code> | *No description.* |
| <code><a href="#control-broker.Api.setEvalEngine">setEvalEngine</a></code> | *No description.* |

---

##### `toString` <a name="toString" id="control-broker.Api.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

##### `addInputHandler` <a name="addInputHandler" id="control-broker.Api.addInputHandler"></a>

```typescript
public addInputHandler(inputHandler: BaseInputHandler, binding: BaseApiBinding): void
```

###### `inputHandler`<sup>Required</sup> <a name="inputHandler" id="control-broker.Api.addInputHandler.parameter.inputHandler"></a>

- *Type:* control-broker.inputHandlers.BaseInputHandler

---

###### `binding`<sup>Required</sup> <a name="binding" id="control-broker.Api.addInputHandler.parameter.binding"></a>

- *Type:* <a href="#control-broker.BaseApiBinding">BaseApiBinding</a>

---

##### `getUrlForInputHandler` <a name="getUrlForInputHandler" id="control-broker.Api.getUrlForInputHandler"></a>

```typescript
public getUrlForInputHandler(inputHandler: BaseInputHandler): string
```

###### `inputHandler`<sup>Required</sup> <a name="inputHandler" id="control-broker.Api.getUrlForInputHandler.parameter.inputHandler"></a>

- *Type:* control-broker.inputHandlers.BaseInputHandler

---

##### `setEvalEngine` <a name="setEvalEngine" id="control-broker.Api.setEvalEngine"></a>

```typescript
public setEvalEngine(evalEngine: BaseEvalEngine, binding: BaseApiBinding): void
```

###### `evalEngine`<sup>Required</sup> <a name="evalEngine" id="control-broker.Api.setEvalEngine.parameter.evalEngine"></a>

- *Type:* <a href="#control-broker.BaseEvalEngine">BaseEvalEngine</a>

---

###### `binding`<sup>Required</sup> <a name="binding" id="control-broker.Api.setEvalEngine.parameter.binding"></a>

- *Type:* <a href="#control-broker.BaseApiBinding">BaseApiBinding</a>

---

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.Api.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

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

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.Api.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#control-broker.Api.property.accessLogRetention">accessLogRetention</a></code> | <code>aws-cdk-lib.aws_logs.RetentionDays</code> | *No description.* |
| <code><a href="#control-broker.Api.property.apiAccessLogGroup">apiAccessLogGroup</a></code> | <code>aws-cdk-lib.aws_logs.LogGroup</code> | *No description.* |
| <code><a href="#control-broker.Api.property.awsApiGatewayHTTPApi">awsApiGatewayHTTPApi</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.HttpApi</code> | *No description.* |
| <code><a href="#control-broker.Api.property.awsApiGatewayRestApi">awsApiGatewayRestApi</a></code> | <code>aws-cdk-lib.aws_apigateway.RestApi</code> | *No description.* |
| <code><a href="#control-broker.Api.property.id">id</a></code> | <code>string</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.Api.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `accessLogRetention`<sup>Required</sup> <a name="accessLogRetention" id="control-broker.Api.property.accessLogRetention"></a>

```typescript
public readonly accessLogRetention: RetentionDays;
```

- *Type:* aws-cdk-lib.aws_logs.RetentionDays

---

##### `apiAccessLogGroup`<sup>Required</sup> <a name="apiAccessLogGroup" id="control-broker.Api.property.apiAccessLogGroup"></a>

```typescript
public readonly apiAccessLogGroup: LogGroup;
```

- *Type:* aws-cdk-lib.aws_logs.LogGroup

---

##### `awsApiGatewayHTTPApi`<sup>Required</sup> <a name="awsApiGatewayHTTPApi" id="control-broker.Api.property.awsApiGatewayHTTPApi"></a>

```typescript
public readonly awsApiGatewayHTTPApi: HttpApi;
```

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.HttpApi

---

##### `awsApiGatewayRestApi`<sup>Required</sup> <a name="awsApiGatewayRestApi" id="control-broker.Api.property.awsApiGatewayRestApi"></a>

```typescript
public readonly awsApiGatewayRestApi: RestApi;
```

- *Type:* aws-cdk-lib.aws_apigateway.RestApi

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.Api.property.id"></a>

```typescript
public readonly id: string;
```

- *Type:* string

---


### BaseEvalEngine <a name="BaseEvalEngine" id="control-broker.BaseEvalEngine"></a>

- *Implements:* <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>

#### Initializers <a name="Initializers" id="control-broker.BaseEvalEngine.Initializer"></a>

```typescript
import { BaseEvalEngine } from 'control-broker'

new BaseEvalEngine(scope: Construct, id: string)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.BaseEvalEngine.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | The scope in which to define this construct. |
| <code><a href="#control-broker.BaseEvalEngine.Initializer.parameter.id">id</a></code> | <code>string</code> | The scoped construct ID. |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.BaseEvalEngine.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

The scope in which to define this construct.

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.BaseEvalEngine.Initializer.parameter.id"></a>

- *Type:* string

The scoped construct ID.

Must be unique amongst siblings. If
the ID includes a path separator (`/`), then it will be replaced by double
dash `--`.

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.BaseEvalEngine.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="control-broker.BaseEvalEngine.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.BaseEvalEngine.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="control-broker.BaseEvalEngine.isConstruct"></a>

```typescript
import { BaseEvalEngine } from 'control-broker'

BaseEvalEngine.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="control-broker.BaseEvalEngine.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.BaseEvalEngine.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#control-broker.BaseEvalEngine.property.integrationTargetType">integrationTargetType</a></code> | <code><a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a></code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.BaseEvalEngine.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `integrationTargetType`<sup>Required</sup> <a name="integrationTargetType" id="control-broker.BaseEvalEngine.property.integrationTargetType"></a>

```typescript
public readonly integrationTargetType: IntegrationTargetType;
```

- *Type:* <a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a>

---


### BaseInputHandler <a name="BaseInputHandler" id="control-broker.inputHandlers.BaseInputHandler"></a>

- *Implements:* <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>

#### Initializers <a name="Initializers" id="control-broker.inputHandlers.BaseInputHandler.Initializer"></a>

```typescript
import { inputHandlers } from 'control-broker'

new inputHandlers.BaseInputHandler(scope: Construct, id: string)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | The scope in which to define this construct. |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.Initializer.parameter.id">id</a></code> | <code>string</code> | The scoped construct ID. |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.inputHandlers.BaseInputHandler.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

The scope in which to define this construct.

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.inputHandlers.BaseInputHandler.Initializer.parameter.id"></a>

- *Type:* string

The scoped construct ID.

Must be unique amongst siblings. If
the ID includes a path separator (`/`), then it will be replaced by double
dash `--`.

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="control-broker.inputHandlers.BaseInputHandler.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="control-broker.inputHandlers.BaseInputHandler.isConstruct"></a>

```typescript
import { inputHandlers } from 'control-broker'

inputHandlers.BaseInputHandler.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="control-broker.inputHandlers.BaseInputHandler.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.property.evalEngineCallerPrincipalArn">evalEngineCallerPrincipalArn</a></code> | <code>string</code> | ARN of the principal that will call the EvalEngine endpoint. |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.property.integrationTargetType">integrationTargetType</a></code> | <code><a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a></code> | *No description.* |
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.property.urlSafeName">urlSafeName</a></code> | <code>string</code> | Return a name for this input handler that is safe for use in the path of a URL. |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.inputHandlers.BaseInputHandler.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `evalEngineCallerPrincipalArn`<sup>Required</sup> <a name="evalEngineCallerPrincipalArn" id="control-broker.inputHandlers.BaseInputHandler.property.evalEngineCallerPrincipalArn"></a>

```typescript
public readonly evalEngineCallerPrincipalArn: string;
```

- *Type:* string

ARN of the principal that will call the EvalEngine endpoint.

---

##### `integrationTargetType`<sup>Required</sup> <a name="integrationTargetType" id="control-broker.inputHandlers.BaseInputHandler.property.integrationTargetType"></a>

```typescript
public readonly integrationTargetType: IntegrationTargetType;
```

- *Type:* <a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a>

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.inputHandlers.BaseInputHandler.property.urlSafeName"></a>

```typescript
public readonly urlSafeName: string;
```

- *Type:* string

Return a name for this input handler that is safe for use in the path of a URL.

---


### CloudFormationInputHandler <a name="CloudFormationInputHandler" id="control-broker.inputHandlers.CloudFormationInputHandler"></a>

- *Implements:* <a href="#control-broker.ILambdaIntegrationTarget">ILambdaIntegrationTarget</a>

#### Initializers <a name="Initializers" id="control-broker.inputHandlers.CloudFormationInputHandler.Initializer"></a>

```typescript
import { inputHandlers } from 'control-broker'

new inputHandlers.CloudFormationInputHandler(scope: Construct, id: string)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.id"></a>

- *Type:* string

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="control-broker.inputHandlers.CloudFormationInputHandler.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="control-broker.inputHandlers.CloudFormationInputHandler.isConstruct"></a>

```typescript
import { inputHandlers } from 'control-broker'

inputHandlers.CloudFormationInputHandler.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="control-broker.inputHandlers.CloudFormationInputHandler.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.property.evalEngineCallerPrincipalArn">evalEngineCallerPrincipalArn</a></code> | <code>string</code> | ARN of the principal that will call the EvalEngine endpoint. |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.property.integrationTargetType">integrationTargetType</a></code> | <code><a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a></code> | *No description.* |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.property.urlSafeName">urlSafeName</a></code> | <code>string</code> | Return a name for this input handler that is safe for use in the path of a URL. |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.property.handler">handler</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.inputHandlers.CloudFormationInputHandler.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `evalEngineCallerPrincipalArn`<sup>Required</sup> <a name="evalEngineCallerPrincipalArn" id="control-broker.inputHandlers.CloudFormationInputHandler.property.evalEngineCallerPrincipalArn"></a>

```typescript
public readonly evalEngineCallerPrincipalArn: string;
```

- *Type:* string

ARN of the principal that will call the EvalEngine endpoint.

---

##### `integrationTargetType`<sup>Required</sup> <a name="integrationTargetType" id="control-broker.inputHandlers.CloudFormationInputHandler.property.integrationTargetType"></a>

```typescript
public readonly integrationTargetType: IntegrationTargetType;
```

- *Type:* <a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a>

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.inputHandlers.CloudFormationInputHandler.property.urlSafeName"></a>

```typescript
public readonly urlSafeName: string;
```

- *Type:* string

Return a name for this input handler that is safe for use in the path of a URL.

---

##### `handler`<sup>Required</sup> <a name="handler" id="control-broker.inputHandlers.CloudFormationInputHandler.property.handler"></a>

```typescript
public readonly handler: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

---


### ControlBroker <a name="ControlBroker" id="control-broker.ControlBroker"></a>

#### Initializers <a name="Initializers" id="control-broker.ControlBroker.Initializer"></a>

```typescript
import { ControlBroker } from 'control-broker'

new ControlBroker(scope: Construct, id: string, props: ControlBrokerProps)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.ControlBroker.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#control-broker.ControlBroker.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.ControlBroker.Initializer.parameter.props">props</a></code> | <code><a href="#control-broker.ControlBrokerProps">ControlBrokerProps</a></code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.ControlBroker.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.ControlBroker.Initializer.parameter.id"></a>

- *Type:* string

---

##### `props`<sup>Required</sup> <a name="props" id="control-broker.ControlBroker.Initializer.parameter.props"></a>

- *Type:* <a href="#control-broker.ControlBrokerProps">ControlBrokerProps</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.ControlBroker.toString">toString</a></code> | Returns a string representation of this construct. |
| <code><a href="#control-broker.ControlBroker.getUrlForInputHandler">getUrlForInputHandler</a></code> | *No description.* |

---

##### `toString` <a name="toString" id="control-broker.ControlBroker.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

##### `getUrlForInputHandler` <a name="getUrlForInputHandler" id="control-broker.ControlBroker.getUrlForInputHandler"></a>

```typescript
public getUrlForInputHandler(inputHandler: BaseInputHandler): string
```

###### `inputHandler`<sup>Required</sup> <a name="inputHandler" id="control-broker.ControlBroker.getUrlForInputHandler.parameter.inputHandler"></a>

- *Type:* control-broker.inputHandlers.BaseInputHandler

---

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.ControlBroker.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="control-broker.ControlBroker.isConstruct"></a>

```typescript
import { ControlBroker } from 'control-broker'

ControlBroker.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="control-broker.ControlBroker.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.ControlBroker.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#control-broker.ControlBroker.property.api">api</a></code> | <code><a href="#control-broker.Api">Api</a></code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.ControlBroker.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `api`<sup>Required</sup> <a name="api" id="control-broker.ControlBroker.property.api"></a>

```typescript
public readonly api: Api;
```

- *Type:* <a href="#control-broker.Api">Api</a>

---


### OpaEvalEngine <a name="OpaEvalEngine" id="control-broker.OpaEvalEngine"></a>

- *Implements:* <a href="#control-broker.ILambdaIntegrationTarget">ILambdaIntegrationTarget</a>

#### Initializers <a name="Initializers" id="control-broker.OpaEvalEngine.Initializer"></a>

```typescript
import { OpaEvalEngine } from 'control-broker'

new OpaEvalEngine(scope: Construct, id: string)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.OpaEvalEngine.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | *No description.* |
| <code><a href="#control-broker.OpaEvalEngine.Initializer.parameter.id">id</a></code> | <code>string</code> | *No description.* |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.OpaEvalEngine.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.OpaEvalEngine.Initializer.parameter.id"></a>

- *Type:* string

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.OpaEvalEngine.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="control-broker.OpaEvalEngine.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.OpaEvalEngine.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="control-broker.OpaEvalEngine.isConstruct"></a>

```typescript
import { OpaEvalEngine } from 'control-broker'

OpaEvalEngine.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="control-broker.OpaEvalEngine.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.OpaEvalEngine.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |
| <code><a href="#control-broker.OpaEvalEngine.property.integrationTargetType">integrationTargetType</a></code> | <code><a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a></code> | *No description.* |
| <code><a href="#control-broker.OpaEvalEngine.property.handler">handler</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | *No description.* |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.OpaEvalEngine.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `integrationTargetType`<sup>Required</sup> <a name="integrationTargetType" id="control-broker.OpaEvalEngine.property.integrationTargetType"></a>

```typescript
public readonly integrationTargetType: IntegrationTargetType;
```

- *Type:* <a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a>

---

##### `handler`<sup>Required</sup> <a name="handler" id="control-broker.OpaEvalEngine.property.handler"></a>

```typescript
public readonly handler: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

---


## Structs <a name="Structs" id="Structs"></a>

### ApiProps <a name="ApiProps" id="control-broker.ApiProps"></a>

#### Initializer <a name="Initializer" id="control-broker.ApiProps.Initializer"></a>

```typescript
import { ApiProps } from 'control-broker'

const apiProps: ApiProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.ApiProps.property.apiAccessLogGroup">apiAccessLogGroup</a></code> | <code>aws-cdk-lib.aws_logs.LogGroup</code> | *No description.* |

---

##### `apiAccessLogGroup`<sup>Optional</sup> <a name="apiAccessLogGroup" id="control-broker.ApiProps.property.apiAccessLogGroup"></a>

```typescript
public readonly apiAccessLogGroup: LogGroup;
```

- *Type:* aws-cdk-lib.aws_logs.LogGroup

---

### BaseApiBindingProps <a name="BaseApiBindingProps" id="control-broker.BaseApiBindingProps"></a>

#### Initializer <a name="Initializer" id="control-broker.BaseApiBindingProps.Initializer"></a>

```typescript
import { BaseApiBindingProps } from 'control-broker'

const baseApiBindingProps: BaseApiBindingProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.BaseApiBindingProps.property.integration">integration</a></code> | <code>any</code> | *No description.* |

---

##### `integration`<sup>Required</sup> <a name="integration" id="control-broker.BaseApiBindingProps.property.integration"></a>

```typescript
public readonly integration: any;
```

- *Type:* any

---

### ControlBrokerProps <a name="ControlBrokerProps" id="control-broker.ControlBrokerProps"></a>

#### Initializer <a name="Initializer" id="control-broker.ControlBrokerProps.Initializer"></a>

```typescript
import { ControlBrokerProps } from 'control-broker'

const controlBrokerProps: ControlBrokerProps = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.ControlBrokerProps.property.api">api</a></code> | <code><a href="#control-broker.Api">Api</a></code> | *No description.* |

---

##### `api`<sup>Required</sup> <a name="api" id="control-broker.ControlBrokerProps.property.api"></a>

```typescript
public readonly api: Api;
```

- *Type:* <a href="#control-broker.Api">Api</a>

---

### EvalEngineBindingConfiguration <a name="EvalEngineBindingConfiguration" id="control-broker.EvalEngineBindingConfiguration"></a>

#### Initializer <a name="Initializer" id="control-broker.EvalEngineBindingConfiguration.Initializer"></a>

```typescript
import { EvalEngineBindingConfiguration } from 'control-broker'

const evalEngineBindingConfiguration: EvalEngineBindingConfiguration = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.EvalEngineBindingConfiguration.property.binding">binding</a></code> | <code><a href="#control-broker.BaseApiBinding">BaseApiBinding</a></code> | *No description.* |
| <code><a href="#control-broker.EvalEngineBindingConfiguration.property.evalEngine">evalEngine</a></code> | <code><a href="#control-broker.BaseEvalEngine">BaseEvalEngine</a></code> | *No description.* |

---

##### `binding`<sup>Optional</sup> <a name="binding" id="control-broker.EvalEngineBindingConfiguration.property.binding"></a>

```typescript
public readonly binding: BaseApiBinding;
```

- *Type:* <a href="#control-broker.BaseApiBinding">BaseApiBinding</a>

---

##### `evalEngine`<sup>Optional</sup> <a name="evalEngine" id="control-broker.EvalEngineBindingConfiguration.property.evalEngine"></a>

```typescript
public readonly evalEngine: BaseEvalEngine;
```

- *Type:* <a href="#control-broker.BaseEvalEngine">BaseEvalEngine</a>

---

### HttpApiBindingAddToApiOptions <a name="HttpApiBindingAddToApiOptions" id="control-broker.HttpApiBindingAddToApiOptions"></a>

#### Initializer <a name="Initializer" id="control-broker.HttpApiBindingAddToApiOptions.Initializer"></a>

```typescript
import { HttpApiBindingAddToApiOptions } from 'control-broker'

const httpApiBindingAddToApiOptions: HttpApiBindingAddToApiOptions = { ... }
```


### InputHandlerBindingConfiguration <a name="InputHandlerBindingConfiguration" id="control-broker.InputHandlerBindingConfiguration"></a>

#### Initializer <a name="Initializer" id="control-broker.InputHandlerBindingConfiguration.Initializer"></a>

```typescript
import { InputHandlerBindingConfiguration } from 'control-broker'

const inputHandlerBindingConfiguration: InputHandlerBindingConfiguration = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.InputHandlerBindingConfiguration.property.binding">binding</a></code> | <code><a href="#control-broker.BaseApiBinding">BaseApiBinding</a></code> | *No description.* |
| <code><a href="#control-broker.InputHandlerBindingConfiguration.property.inputHandler">inputHandler</a></code> | <code>control-broker.inputHandlers.BaseInputHandler</code> | *No description.* |

---

##### `binding`<sup>Required</sup> <a name="binding" id="control-broker.InputHandlerBindingConfiguration.property.binding"></a>

```typescript
public readonly binding: BaseApiBinding;
```

- *Type:* <a href="#control-broker.BaseApiBinding">BaseApiBinding</a>

---

##### `inputHandler`<sup>Required</sup> <a name="inputHandler" id="control-broker.InputHandlerBindingConfiguration.property.inputHandler"></a>

```typescript
public readonly inputHandler: BaseInputHandler;
```

- *Type:* control-broker.inputHandlers.BaseInputHandler

---

### InputHandlerBindingConfigurations <a name="InputHandlerBindingConfigurations" id="control-broker.InputHandlerBindingConfigurations"></a>

#### Initializer <a name="Initializer" id="control-broker.InputHandlerBindingConfigurations.Initializer"></a>

```typescript
import { InputHandlerBindingConfigurations } from 'control-broker'

const inputHandlerBindingConfigurations: InputHandlerBindingConfigurations = { ... }
```


### InputHandlerIntegrationContext <a name="InputHandlerIntegrationContext" id="control-broker.inputHandlers.InputHandlerIntegrationContext"></a>

#### Initializer <a name="Initializer" id="control-broker.inputHandlers.InputHandlerIntegrationContext.Initializer"></a>

```typescript
import { inputHandlers } from 'control-broker'

const inputHandlerIntegrationContext: inputHandlers.InputHandlerIntegrationContext = { ... }
```

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.inputHandlers.InputHandlerIntegrationContext.property.externalUrl">externalUrl</a></code> | <code>string</code> | *No description.* |

---

##### `externalUrl`<sup>Required</sup> <a name="externalUrl" id="control-broker.inputHandlers.InputHandlerIntegrationContext.property.externalUrl"></a>

```typescript
public readonly externalUrl: string;
```

- *Type:* string

---

## Classes <a name="Classes" id="Classes"></a>

### BaseApiBinding <a name="BaseApiBinding" id="control-broker.BaseApiBinding"></a>

Base class for an API Binding, which attaches an integration to an API and authorizes principals to invoke the integration via the API attachment.

Defined abstractly since there are different types of APIs to attach integrations with
and different principals to allow.

#### Initializers <a name="Initializers" id="control-broker.BaseApiBinding.Initializer"></a>

```typescript
import { BaseApiBinding } from 'control-broker'

new BaseApiBinding(urlSafeName: string, api: Api, integrationTarget: IIntegrationTarget)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.BaseApiBinding.Initializer.parameter.urlSafeName">urlSafeName</a></code> | <code>string</code> | A name suitable for use in an integration's URL. |
| <code><a href="#control-broker.BaseApiBinding.Initializer.parameter.api">api</a></code> | <code><a href="#control-broker.Api">Api</a></code> | The API to bind to. |
| <code><a href="#control-broker.BaseApiBinding.Initializer.parameter.integrationTarget">integrationTarget</a></code> | <code><a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a></code> | The integration target to bind to the API via an integration. |

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.BaseApiBinding.Initializer.parameter.urlSafeName"></a>

- *Type:* string

A name suitable for use in an integration's URL.

Can contain slashes.

---

##### `api`<sup>Required</sup> <a name="api" id="control-broker.BaseApiBinding.Initializer.parameter.api"></a>

- *Type:* <a href="#control-broker.Api">Api</a>

The API to bind to.

---

##### `integrationTarget`<sup>Required</sup> <a name="integrationTarget" id="control-broker.BaseApiBinding.Initializer.parameter.integrationTarget"></a>

- *Type:* <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>

The integration target to bind to the API via an integration.

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.BaseApiBinding.authorizePrincipalArn">authorizePrincipalArn</a></code> | Give permission to a principal to call this API using this binding. |

---

##### `authorizePrincipalArn` <a name="authorizePrincipalArn" id="control-broker.BaseApiBinding.authorizePrincipalArn"></a>

```typescript
public authorizePrincipalArn(principalArn: string): void
```

Give permission to a principal to call this API using this binding.

This should be called after the binding has been added to all APIs.

###### `principalArn`<sup>Required</sup> <a name="principalArn" id="control-broker.BaseApiBinding.authorizePrincipalArn.parameter.principalArn"></a>

- *Type:* string

Principal to give calling permissions to.

---


#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.BaseApiBinding.property.api">api</a></code> | <code><a href="#control-broker.Api">Api</a></code> | The API to bind to. |
| <code><a href="#control-broker.BaseApiBinding.property.apiType">apiType</a></code> | <code><a href="#control-broker.AwsApiType">AwsApiType</a></code> | *No description.* |
| <code><a href="#control-broker.BaseApiBinding.property.integrationTarget">integrationTarget</a></code> | <code><a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a></code> | The integration target to bind to the API via an integration. |
| <code><a href="#control-broker.BaseApiBinding.property.method">method</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.BaseApiBinding.property.path">path</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.BaseApiBinding.property.url">url</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.BaseApiBinding.property.urlSafeName">urlSafeName</a></code> | <code>string</code> | A name suitable for use in an integration's URL. |

---

##### `api`<sup>Required</sup> <a name="api" id="control-broker.BaseApiBinding.property.api"></a>

```typescript
public readonly api: Api;
```

- *Type:* <a href="#control-broker.Api">Api</a>

The API to bind to.

---

##### `apiType`<sup>Required</sup> <a name="apiType" id="control-broker.BaseApiBinding.property.apiType"></a>

```typescript
public readonly apiType: AwsApiType;
```

- *Type:* <a href="#control-broker.AwsApiType">AwsApiType</a>

---

##### `integrationTarget`<sup>Required</sup> <a name="integrationTarget" id="control-broker.BaseApiBinding.property.integrationTarget"></a>

```typescript
public readonly integrationTarget: IIntegrationTarget;
```

- *Type:* <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>

The integration target to bind to the API via an integration.

---

##### `method`<sup>Required</sup> <a name="method" id="control-broker.BaseApiBinding.property.method"></a>

```typescript
public readonly method: string;
```

- *Type:* string

---

##### `path`<sup>Required</sup> <a name="path" id="control-broker.BaseApiBinding.property.path"></a>

```typescript
public readonly path: string;
```

- *Type:* string

---

##### `url`<sup>Required</sup> <a name="url" id="control-broker.BaseApiBinding.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.BaseApiBinding.property.urlSafeName"></a>

```typescript
public readonly urlSafeName: string;
```

- *Type:* string

A name suitable for use in an integration's URL.

Can contain slashes.

---


### HttpApiBinding <a name="HttpApiBinding" id="control-broker.HttpApiBinding"></a>

#### Initializers <a name="Initializers" id="control-broker.HttpApiBinding.Initializer"></a>

```typescript
import { HttpApiBinding } from 'control-broker'

new HttpApiBinding(urlSafeName: string, api: Api, integrationTarget: IIntegrationTarget)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.HttpApiBinding.Initializer.parameter.urlSafeName">urlSafeName</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.HttpApiBinding.Initializer.parameter.api">api</a></code> | <code><a href="#control-broker.Api">Api</a></code> | *No description.* |
| <code><a href="#control-broker.HttpApiBinding.Initializer.parameter.integrationTarget">integrationTarget</a></code> | <code><a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a></code> | *No description.* |

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.HttpApiBinding.Initializer.parameter.urlSafeName"></a>

- *Type:* string

---

##### `api`<sup>Required</sup> <a name="api" id="control-broker.HttpApiBinding.Initializer.parameter.api"></a>

- *Type:* <a href="#control-broker.Api">Api</a>

---

##### `integrationTarget`<sup>Required</sup> <a name="integrationTarget" id="control-broker.HttpApiBinding.Initializer.parameter.integrationTarget"></a>

- *Type:* <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.HttpApiBinding.authorizePrincipalArn">authorizePrincipalArn</a></code> | Give permission to a principal to call this API using this binding. |

---

##### `authorizePrincipalArn` <a name="authorizePrincipalArn" id="control-broker.HttpApiBinding.authorizePrincipalArn"></a>

```typescript
public authorizePrincipalArn(principalArn: string): void
```

Give permission to a principal to call this API using this binding.

This should be called after the binding has been added to all APIs.

###### `principalArn`<sup>Required</sup> <a name="principalArn" id="control-broker.HttpApiBinding.authorizePrincipalArn.parameter.principalArn"></a>

- *Type:* string

---


#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.HttpApiBinding.property.api">api</a></code> | <code><a href="#control-broker.Api">Api</a></code> | The API to bind to. |
| <code><a href="#control-broker.HttpApiBinding.property.apiType">apiType</a></code> | <code><a href="#control-broker.AwsApiType">AwsApiType</a></code> | *No description.* |
| <code><a href="#control-broker.HttpApiBinding.property.integrationTarget">integrationTarget</a></code> | <code><a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a></code> | The integration target to bind to the API via an integration. |
| <code><a href="#control-broker.HttpApiBinding.property.method">method</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.HttpApiBinding.property.path">path</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.HttpApiBinding.property.url">url</a></code> | <code>string</code> | *No description.* |
| <code><a href="#control-broker.HttpApiBinding.property.urlSafeName">urlSafeName</a></code> | <code>string</code> | A name suitable for use in an integration's URL. |
| <code><a href="#control-broker.HttpApiBinding.property.route">route</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.HttpRoute</code> | *No description.* |

---

##### `api`<sup>Required</sup> <a name="api" id="control-broker.HttpApiBinding.property.api"></a>

```typescript
public readonly api: Api;
```

- *Type:* <a href="#control-broker.Api">Api</a>

The API to bind to.

---

##### `apiType`<sup>Required</sup> <a name="apiType" id="control-broker.HttpApiBinding.property.apiType"></a>

```typescript
public readonly apiType: AwsApiType;
```

- *Type:* <a href="#control-broker.AwsApiType">AwsApiType</a>

---

##### `integrationTarget`<sup>Required</sup> <a name="integrationTarget" id="control-broker.HttpApiBinding.property.integrationTarget"></a>

```typescript
public readonly integrationTarget: IIntegrationTarget;
```

- *Type:* <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>

The integration target to bind to the API via an integration.

---

##### `method`<sup>Required</sup> <a name="method" id="control-broker.HttpApiBinding.property.method"></a>

```typescript
public readonly method: string;
```

- *Type:* string

---

##### `path`<sup>Required</sup> <a name="path" id="control-broker.HttpApiBinding.property.path"></a>

```typescript
public readonly path: string;
```

- *Type:* string

---

##### `url`<sup>Required</sup> <a name="url" id="control-broker.HttpApiBinding.property.url"></a>

```typescript
public readonly url: string;
```

- *Type:* string

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.HttpApiBinding.property.urlSafeName"></a>

```typescript
public readonly urlSafeName: string;
```

- *Type:* string

A name suitable for use in an integration's URL.

Can contain slashes.

---

##### `route`<sup>Required</sup> <a name="route" id="control-broker.HttpApiBinding.property.route"></a>

```typescript
public readonly route: HttpRoute;
```

- *Type:* @aws-cdk/aws-apigatewayv2-alpha.HttpRoute

---


## Protocols <a name="Protocols" id="Protocols"></a>

### IIntegrationTarget <a name="IIntegrationTarget" id="control-broker.IIntegrationTarget"></a>

- *Implemented By:* control-broker.inputHandlers.BaseInputHandler, control-broker.inputHandlers.CloudFormationInputHandler, <a href="#control-broker.BaseEvalEngine">BaseEvalEngine</a>, <a href="#control-broker.OpaEvalEngine">OpaEvalEngine</a>, <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>, <a href="#control-broker.ILambdaIntegrationTarget">ILambdaIntegrationTarget</a>


#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.IIntegrationTarget.property.integrationTargetType">integrationTargetType</a></code> | <code><a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a></code> | *No description.* |

---

##### `integrationTargetType`<sup>Required</sup> <a name="integrationTargetType" id="control-broker.IIntegrationTarget.property.integrationTargetType"></a>

```typescript
public readonly integrationTargetType: IntegrationTargetType;
```

- *Type:* <a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a>

---

### ILambdaIntegrationTarget <a name="ILambdaIntegrationTarget" id="control-broker.ILambdaIntegrationTarget"></a>

- *Extends:* <a href="#control-broker.IIntegrationTarget">IIntegrationTarget</a>

- *Implemented By:* control-broker.inputHandlers.CloudFormationInputHandler, <a href="#control-broker.OpaEvalEngine">OpaEvalEngine</a>, <a href="#control-broker.ILambdaIntegrationTarget">ILambdaIntegrationTarget</a>


#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.ILambdaIntegrationTarget.property.integrationTargetType">integrationTargetType</a></code> | <code><a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a></code> | *No description.* |
| <code><a href="#control-broker.ILambdaIntegrationTarget.property.handler">handler</a></code> | <code>aws-cdk-lib.aws_lambda.Function</code> | *No description.* |

---

##### `integrationTargetType`<sup>Required</sup> <a name="integrationTargetType" id="control-broker.ILambdaIntegrationTarget.property.integrationTargetType"></a>

```typescript
public readonly integrationTargetType: IntegrationTargetType;
```

- *Type:* <a href="#control-broker.IntegrationTargetType">IntegrationTargetType</a>

---

##### `handler`<sup>Required</sup> <a name="handler" id="control-broker.ILambdaIntegrationTarget.property.handler"></a>

```typescript
public readonly handler: Function;
```

- *Type:* aws-cdk-lib.aws_lambda.Function

---

## Enums <a name="Enums" id="Enums"></a>

### AwsApiType <a name="AwsApiType" id="control-broker.AwsApiType"></a>

#### Members <a name="Members" id="Members"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.AwsApiType.HTTP">HTTP</a></code> | *No description.* |
| <code><a href="#control-broker.AwsApiType.REST">REST</a></code> | *No description.* |
| <code><a href="#control-broker.AwsApiType.WEBSOCKET">WEBSOCKET</a></code> | *No description.* |

---

##### `HTTP` <a name="HTTP" id="control-broker.AwsApiType.HTTP"></a>

---


##### `REST` <a name="REST" id="control-broker.AwsApiType.REST"></a>

---


##### `WEBSOCKET` <a name="WEBSOCKET" id="control-broker.AwsApiType.WEBSOCKET"></a>

---


### IntegrationTargetType <a name="IntegrationTargetType" id="control-broker.IntegrationTargetType"></a>

#### Members <a name="Members" id="Members"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.IntegrationTargetType.LAMBDA">LAMBDA</a></code> | *No description.* |
| <code><a href="#control-broker.IntegrationTargetType.STEP_FUNCTION">STEP_FUNCTION</a></code> | *No description.* |

---

##### `LAMBDA` <a name="LAMBDA" id="control-broker.IntegrationTargetType.LAMBDA"></a>

---


##### `STEP_FUNCTION` <a name="STEP_FUNCTION" id="control-broker.IntegrationTargetType.STEP_FUNCTION"></a>

---

