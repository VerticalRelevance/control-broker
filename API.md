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

---

##### `toString` <a name="toString" id="control-broker.Api.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

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
| <code><a href="#control-broker.Api.property.awsApiGatewayHTTPApi">awsApiGatewayHTTPApi</a></code> | <code>@aws-cdk/aws-apigatewayv2-alpha.HttpApi</code> | *No description.* |
| <code><a href="#control-broker.Api.property.awsApiGatewayRestApi">awsApiGatewayRestApi</a></code> | <code>aws-cdk-lib.aws_apigateway.RestApi</code> | *No description.* |
| <code><a href="#control-broker.Api.property.externalBaseUrl">externalBaseUrl</a></code> | <code>string</code> | *No description.* |

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

##### `externalBaseUrl`<sup>Required</sup> <a name="externalBaseUrl" id="control-broker.Api.property.externalBaseUrl"></a>

```typescript
public readonly externalBaseUrl: string;
```

- *Type:* string

---


### BaseInputHandler <a name="BaseInputHandler" id="control-broker.inputHandlers.BaseInputHandler"></a>

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
| <code><a href="#control-broker.inputHandlers.BaseInputHandler.property.urlSafeName">urlSafeName</a></code> | <code>string</code> | Return a name for this input handler that is safe for use in the path of a URL. |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.inputHandlers.BaseInputHandler.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.inputHandlers.BaseInputHandler.property.urlSafeName"></a>

```typescript
public readonly urlSafeName: string;
```

- *Type:* string

Return a name for this input handler that is safe for use in the path of a URL.

---


### CloudFormationInputHandler <a name="CloudFormationInputHandler" id="control-broker.inputHandlers.CloudFormationInputHandler"></a>

#### Initializers <a name="Initializers" id="control-broker.inputHandlers.CloudFormationInputHandler.Initializer"></a>

```typescript
import { inputHandlers } from 'control-broker'

new inputHandlers.CloudFormationInputHandler(scope: Construct, id: string)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | The scope in which to define this construct. |
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.id">id</a></code> | <code>string</code> | The scoped construct ID. |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

The scope in which to define this construct.

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.inputHandlers.CloudFormationInputHandler.Initializer.parameter.id"></a>

- *Type:* string

The scoped construct ID.

Must be unique amongst siblings. If
the ID includes a path separator (`/`), then it will be replaced by double
dash `--`.

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
| <code><a href="#control-broker.inputHandlers.CloudFormationInputHandler.property.urlSafeName">urlSafeName</a></code> | <code>string</code> | Return a name for this input handler that is safe for use in the path of a URL. |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.inputHandlers.CloudFormationInputHandler.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

---

##### `urlSafeName`<sup>Required</sup> <a name="urlSafeName" id="control-broker.inputHandlers.CloudFormationInputHandler.property.urlSafeName"></a>

```typescript
public readonly urlSafeName: string;
```

- *Type:* string

Return a name for this input handler that is safe for use in the path of a URL.

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


### EvalEngine <a name="EvalEngine" id="control-broker.EvalEngine"></a>

#### Initializers <a name="Initializers" id="control-broker.EvalEngine.Initializer"></a>

```typescript
import { EvalEngine } from 'control-broker'

new EvalEngine(scope: Construct, id: string)
```

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.EvalEngine.Initializer.parameter.scope">scope</a></code> | <code>constructs.Construct</code> | The scope in which to define this construct. |
| <code><a href="#control-broker.EvalEngine.Initializer.parameter.id">id</a></code> | <code>string</code> | The scoped construct ID. |

---

##### `scope`<sup>Required</sup> <a name="scope" id="control-broker.EvalEngine.Initializer.parameter.scope"></a>

- *Type:* constructs.Construct

The scope in which to define this construct.

---

##### `id`<sup>Required</sup> <a name="id" id="control-broker.EvalEngine.Initializer.parameter.id"></a>

- *Type:* string

The scoped construct ID.

Must be unique amongst siblings. If
the ID includes a path separator (`/`), then it will be replaced by double
dash `--`.

---

#### Methods <a name="Methods" id="Methods"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.EvalEngine.toString">toString</a></code> | Returns a string representation of this construct. |

---

##### `toString` <a name="toString" id="control-broker.EvalEngine.toString"></a>

```typescript
public toString(): string
```

Returns a string representation of this construct.

#### Static Functions <a name="Static Functions" id="Static Functions"></a>

| **Name** | **Description** |
| --- | --- |
| <code><a href="#control-broker.EvalEngine.isConstruct">isConstruct</a></code> | Checks if `x` is a construct. |

---

##### ~~`isConstruct`~~ <a name="isConstruct" id="control-broker.EvalEngine.isConstruct"></a>

```typescript
import { EvalEngine } from 'control-broker'

EvalEngine.isConstruct(x: any)
```

Checks if `x` is a construct.

###### `x`<sup>Required</sup> <a name="x" id="control-broker.EvalEngine.isConstruct.parameter.x"></a>

- *Type:* any

Any object.

---

#### Properties <a name="Properties" id="Properties"></a>

| **Name** | **Type** | **Description** |
| --- | --- | --- |
| <code><a href="#control-broker.EvalEngine.property.node">node</a></code> | <code>constructs.Node</code> | The tree node. |

---

##### `node`<sup>Required</sup> <a name="node" id="control-broker.EvalEngine.property.node"></a>

```typescript
public readonly node: Node;
```

- *Type:* constructs.Node

The tree node.

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
| <code><a href="#control-broker.ApiProps.property.evalEngine">evalEngine</a></code> | <code><a href="#control-broker.EvalEngine">EvalEngine</a></code> | *No description.* |
| <code><a href="#control-broker.ApiProps.property.accessLogRetention">accessLogRetention</a></code> | <code>aws-cdk-lib.aws_logs.RetentionDays</code> | *No description.* |

---

##### `evalEngine`<sup>Required</sup> <a name="evalEngine" id="control-broker.ApiProps.property.evalEngine"></a>

```typescript
public readonly evalEngine: EvalEngine;
```

- *Type:* <a href="#control-broker.EvalEngine">EvalEngine</a>

---

##### `accessLogRetention`<sup>Optional</sup> <a name="accessLogRetention" id="control-broker.ApiProps.property.accessLogRetention"></a>

```typescript
public readonly accessLogRetention: RetentionDays;
```

- *Type:* aws-cdk-lib.aws_logs.RetentionDays

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

##### `api`<sup>Optional</sup> <a name="api" id="control-broker.ControlBrokerProps.property.api"></a>

```typescript
public readonly api: Api;
```

- *Type:* <a href="#control-broker.Api">Api</a>

---



