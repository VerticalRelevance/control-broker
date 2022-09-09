'''
# AWS APIGatewayv2 Authorizers

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Table of Contents

* [Introduction](#introduction)
* [HTTP APIs](#http-apis)

  * [Default Authorization](#default-authorization)
  * [Route Authorization](#route-authorization)
  * [JWT Authorizers](#jwt-authorizers)

    * [User Pool Authorizer](#user-pool-authorizer)
  * [Lambda Authorizers](#lambda-authorizers)
  * [IAM Authorizers](#iam-authorizers)
* [WebSocket APIs](#websocket-apis)

  * [Lambda Authorizer](#lambda-authorizer)

## Introduction

API Gateway supports multiple mechanisms for controlling and managing access to your HTTP API. They are mainly
classified into Lambda Authorizers, JWT authorizers and standard AWS IAM roles and policies. More information is
available at [Controlling and managing access to an HTTP
API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control.html).

## HTTP APIs

Access control for Http Apis is managed by restricting which routes can be invoked via.

Authorizers and scopes can either be applied to the api, or specifically for each route.

### Default Authorization

When using default authorization, all routes of the api will inherit the configuration.

In the example below, all routes will require the `manage:books` scope present in order to invoke the integration.

```python
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpJwtAuthorizer


issuer = "https://test.us.auth0.com"
authorizer = HttpJwtAuthorizer("DefaultAuthorizer", issuer,
    jwt_audience=["3131231"]
)

api = apigwv2.HttpApi(self, "HttpApi",
    default_authorizer=authorizer,
    default_authorization_scopes=["manage:books"]
)
```

### Route Authorization

Authorization can also configured for each Route. When a route authorization is configured, it takes precedence over default authorization.

The example below showcases default authorization, along with route authorization. It also shows how to remove authorization entirely for a route.

* `GET /books` and `GET /books/{id}` use the default authorizer settings on the api
* `POST /books` will require the [write:books] scope
* `POST /login` removes the default authorizer (unauthenticated route)

```python
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpJwtAuthorizer
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration


issuer = "https://test.us.auth0.com"
authorizer = HttpJwtAuthorizer("DefaultAuthorizer", issuer,
    jwt_audience=["3131231"]
)

api = apigwv2.HttpApi(self, "HttpApi",
    default_authorizer=authorizer,
    default_authorization_scopes=["read:books"]
)

api.add_routes(
    integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/books",
    methods=[apigwv2.HttpMethod.GET]
)

api.add_routes(
    integration=HttpUrlIntegration("BooksIdIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/books/{id}",
    methods=[apigwv2.HttpMethod.GET]
)

api.add_routes(
    integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/books",
    methods=[apigwv2.HttpMethod.POST],
    authorization_scopes=["write:books"]
)

api.add_routes(
    integration=HttpUrlIntegration("LoginIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/login",
    methods=[apigwv2.HttpMethod.POST],
    authorizer=apigwv2.HttpNoneAuthorizer()
)
```

### JWT Authorizers

JWT authorizers allow the use of JSON Web Tokens (JWTs) as part of [OpenID Connect](https://openid.net/specs/openid-connect-core-1_0.html) and [OAuth 2.0](https://oauth.net/2/) frameworks to allow and restrict clients from accessing HTTP APIs.

When configured, API Gateway validates the JWT submitted by the client, and allows or denies access based on its content.

The location of the token is defined by the `identitySource` which defaults to the http `Authorization` header. However it also
[supports a number of other options](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.identity-sources).
It then decodes the JWT and validates the signature and claims, against the options defined in the authorizer and route (scopes).
For more information check the [JWT Authorizer documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html).

Clients that fail authorization are presented with either 2 responses:

* `401 - Unauthorized` - When the JWT validation fails
* `403 - Forbidden` - When the JWT validation is successful but the required scopes are not met

```python
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpJwtAuthorizer
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration


issuer = "https://test.us.auth0.com"
authorizer = HttpJwtAuthorizer("BooksAuthorizer", issuer,
    jwt_audience=["3131231"]
)

api = apigwv2.HttpApi(self, "HttpApi")

api.add_routes(
    integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/books",
    authorizer=authorizer
)
```

#### User Pool Authorizer

User Pool Authorizer is a type of JWT Authorizer that uses a Cognito user pool and app client to control who can access your Api. After a successful authorization from the app client, the generated access token will be used as the JWT.

Clients accessing an API that uses a user pool authorizer must first sign in to a user pool and obtain an identity or access token.
They must then use this token in the specified `identitySource` for the API call. More information is available at [using Amazon Cognito user
pools as authorizer](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html).

```python
import aws_cdk.aws_cognito as cognito
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpUserPoolAuthorizer
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration


user_pool = cognito.UserPool(self, "UserPool")

authorizer = HttpUserPoolAuthorizer("BooksAuthorizer", user_pool)

api = apigwv2.HttpApi(self, "HttpApi")

api.add_routes(
    integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/books",
    authorizer=authorizer
)
```

### Lambda Authorizers

Lambda authorizers use a Lambda function to control access to your HTTP API. When a client calls your API, API Gateway invokes your Lambda function and uses the response to determine whether the client can access your API.

Lambda authorizers depending on their response, fall into either two types - Simple or IAM. You can learn about differences [here](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.payload-format-response).

```python
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration

# This function handles your auth logic
# auth_handler: lambda.Function


authorizer = HttpLambdaAuthorizer("BooksAuthorizer", auth_handler,
    response_types=[HttpLambdaResponseType.SIMPLE]
)

api = apigwv2.HttpApi(self, "HttpApi")

api.add_routes(
    integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/books",
    authorizer=authorizer
)
```

### IAM Authorizers

API Gateway supports IAM via the included `HttpIamAuthorizer` and grant syntax:

```python
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpIamAuthorizer
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration

# principal: iam.AnyPrincipal


authorizer = HttpIamAuthorizer()

http_api = apigwv2.HttpApi(self, "HttpApi",
    default_authorizer=authorizer
)

routes = http_api.add_routes(
    integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
    path="/books/{book}"
)

routes[0].grant_invoke(principal)
```

## WebSocket APIs

You can set an authorizer to your WebSocket API's `$connect` route to control access to your API.

### Lambda Authorizer

Lambda authorizers use a Lambda function to control access to your WebSocket API. When a client connects to your API, API Gateway invokes your Lambda function and uses the response to determine whether the client can access your API.

```python
from aws_cdk.aws_apigatewayv2_authorizers_alpha import WebSocketLambdaAuthorizer
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration

# This function handles your auth logic
# auth_handler: lambda.Function

# This function handles your WebSocket requests
# handler: lambda.Function


authorizer = WebSocketLambdaAuthorizer("Authorizer", auth_handler)

integration = WebSocketLambdaIntegration("Integration", handler)

apigwv2.WebSocketApi(self, "WebSocketApi",
    connect_route_options=apigwv2.WebSocketRouteOptions(
        integration=integration,
        authorizer=authorizer
    )
)
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk
import aws_cdk.aws_apigatewayv2_alpha
import aws_cdk.aws_cognito
import aws_cdk.aws_lambda
import constructs


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteAuthorizer)
class HttpIamAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpIamAuthorizer",
):
    '''(experimental) Authorize HTTP API Routes with IAM.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpIamAuthorizer
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
        
        # principal: iam.AnyPrincipal
        
        
        authorizer = HttpIamAuthorizer()
        
        http_api = apigwv2.HttpApi(self, "HttpApi",
            default_authorizer=authorizer
        )
        
        routes = http_api.add_routes(
            integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
            path="/books/{book}"
        )
        
        routes[0].grant_invoke(principal)
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        _options = aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig, jsii.invoke(self, "bind", [_options]))


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteAuthorizer)
class HttpJwtAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpJwtAuthorizer",
):
    '''(experimental) Authorize Http Api routes on whether the requester is registered as part of an AWS Cognito user pool.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpJwtAuthorizer
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
        
        
        issuer = "https://test.us.auth0.com"
        authorizer = HttpJwtAuthorizer("BooksAuthorizer", issuer,
            jwt_audience=["3131231"]
        )
        
        api = apigwv2.HttpApi(self, "HttpApi")
        
        api.add_routes(
            integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
            path="/books",
            authorizer=authorizer
        )
    '''

    def __init__(
        self,
        id: builtins.str,
        jwt_issuer: builtins.str,
        *,
        jwt_audience: typing.Sequence[builtins.str],
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Initialize a JWT authorizer to be bound with HTTP route.

        :param id: The id of the underlying construct.
        :param jwt_issuer: The base domain of the identity provider that issues JWT.
        :param jwt_audience: (experimental) A list of the intended recipients of the JWT. A valid JWT must provide an aud that matches at least one entry in this list.
        :param authorizer_name: (experimental) The name of the authorizer. Default: - same value as ``id`` passed in the constructor
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']

        :stability: experimental
        '''
        props = HttpJwtAuthorizerProps(
            jwt_audience=jwt_audience,
            authorizer_name=authorizer_name,
            identity_source=identity_source,
        )

        jsii.create(self.__class__, self, [id, jwt_issuer, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpJwtAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "jwt_audience": "jwtAudience",
        "authorizer_name": "authorizerName",
        "identity_source": "identitySource",
    },
)
class HttpJwtAuthorizerProps:
    def __init__(
        self,
        *,
        jwt_audience: typing.Sequence[builtins.str],
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties to initialize HttpJwtAuthorizer.

        :param jwt_audience: (experimental) A list of the intended recipients of the JWT. A valid JWT must provide an aud that matches at least one entry in this list.
        :param authorizer_name: (experimental) The name of the authorizer. Default: - same value as ``id`` passed in the constructor
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpJwtAuthorizer
            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
            
            
            issuer = "https://test.us.auth0.com"
            authorizer = HttpJwtAuthorizer("BooksAuthorizer", issuer,
                jwt_audience=["3131231"]
            )
            
            api = apigwv2.HttpApi(self, "HttpApi")
            
            api.add_routes(
                integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
                path="/books",
                authorizer=authorizer
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "jwt_audience": jwt_audience,
        }
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if identity_source is not None:
            self._values["identity_source"] = identity_source

    @builtins.property
    def jwt_audience(self) -> typing.List[builtins.str]:
        '''(experimental) A list of the intended recipients of the JWT.

        A valid JWT must provide an aud that matches at least one entry in this list.

        :stability: experimental
        '''
        result = self._values.get("jwt_audience")
        assert result is not None, "Required property 'jwt_audience' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the authorizer.

        :default: - same value as ``id`` passed in the constructor

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The identity source for which authorization is requested.

        :default: ['$request.header.Authorization']

        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpJwtAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteAuthorizer)
class HttpLambdaAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpLambdaAuthorizer",
):
    '''(experimental) Authorize Http Api routes via a lambda function.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
        
        # This function handles your auth logic
        # auth_handler: lambda.Function
        
        
        authorizer = HttpLambdaAuthorizer("BooksAuthorizer", auth_handler,
            response_types=[HttpLambdaResponseType.SIMPLE]
        )
        
        api = apigwv2.HttpApi(self, "HttpApi")
        
        api.add_routes(
            integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
            path="/books",
            authorizer=authorizer
        )
    '''

    def __init__(
        self,
        id: builtins.str,
        handler: aws_cdk.aws_lambda.IFunction,
        *,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_types: typing.Optional[typing.Sequence["HttpLambdaResponseType"]] = None,
        results_cache_ttl: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''(experimental) Initialize a lambda authorizer to be bound with HTTP route.

        :param id: The id of the underlying construct.
        :param handler: -
        :param authorizer_name: (experimental) Friendly authorizer name. Default: - same value as ``id`` passed in the constructor.
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param response_types: (experimental) The types of responses the lambda can return. If HttpLambdaResponseType.SIMPLE is included then response format 2.0 will be used. Default: [HttpLambdaResponseType.IAM]
        :param results_cache_ttl: (experimental) How long APIGateway should cache the results. Max 1 hour. Disable caching by setting this to ``Duration.seconds(0)``. Default: Duration.minutes(5)

        :stability: experimental
        '''
        props = HttpLambdaAuthorizerProps(
            authorizer_name=authorizer_name,
            identity_source=identity_source,
            response_types=response_types,
            results_cache_ttl=results_cache_ttl,
        )

        jsii.create(self.__class__, self, [id, handler, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpLambdaAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_name": "authorizerName",
        "identity_source": "identitySource",
        "response_types": "responseTypes",
        "results_cache_ttl": "resultsCacheTtl",
    },
)
class HttpLambdaAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_types: typing.Optional[typing.Sequence["HttpLambdaResponseType"]] = None,
        results_cache_ttl: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''(experimental) Properties to initialize HttpTokenAuthorizer.

        :param authorizer_name: (experimental) Friendly authorizer name. Default: - same value as ``id`` passed in the constructor.
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param response_types: (experimental) The types of responses the lambda can return. If HttpLambdaResponseType.SIMPLE is included then response format 2.0 will be used. Default: [HttpLambdaResponseType.IAM]
        :param results_cache_ttl: (experimental) How long APIGateway should cache the results. Max 1 hour. Disable caching by setting this to ``Duration.seconds(0)``. Default: Duration.minutes(5)

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType
            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
            
            # This function handles your auth logic
            # auth_handler: lambda.Function
            
            
            authorizer = HttpLambdaAuthorizer("BooksAuthorizer", auth_handler,
                response_types=[HttpLambdaResponseType.SIMPLE]
            )
            
            api = apigwv2.HttpApi(self, "HttpApi")
            
            api.add_routes(
                integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
                path="/books",
                authorizer=authorizer
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if response_types is not None:
            self._values["response_types"] = response_types
        if results_cache_ttl is not None:
            self._values["results_cache_ttl"] = results_cache_ttl

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Friendly authorizer name.

        :default: - same value as ``id`` passed in the constructor.

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The identity source for which authorization is requested.

        :default: ['$request.header.Authorization']

        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def response_types(self) -> typing.Optional[typing.List["HttpLambdaResponseType"]]:
        '''(experimental) The types of responses the lambda can return.

        If HttpLambdaResponseType.SIMPLE is included then
        response format 2.0 will be used.

        :default: [HttpLambdaResponseType.IAM]

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.payload-format-response
        :stability: experimental
        '''
        result = self._values.get("response_types")
        return typing.cast(typing.Optional[typing.List["HttpLambdaResponseType"]], result)

    @builtins.property
    def results_cache_ttl(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) How long APIGateway should cache the results.

        Max 1 hour.
        Disable caching by setting this to ``Duration.seconds(0)``.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("results_cache_ttl")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpLambdaAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpLambdaResponseType"
)
class HttpLambdaResponseType(enum.Enum):
    '''(experimental) Specifies the type responses the lambda returns.

    :stability: experimental
    '''

    SIMPLE = "SIMPLE"
    '''(experimental) Returns simple boolean response.

    :stability: experimental
    '''
    IAM = "IAM"
    '''(experimental) Returns an IAM Policy.

    :stability: experimental
    '''


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteAuthorizer)
class HttpUserPoolAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpUserPoolAuthorizer",
):
    '''(experimental) Authorize Http Api routes on whether the requester is registered as part of an AWS Cognito user pool.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_cognito as cognito
        from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpUserPoolAuthorizer
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration
        
        
        user_pool = cognito.UserPool(self, "UserPool")
        
        authorizer = HttpUserPoolAuthorizer("BooksAuthorizer", user_pool)
        
        api = apigwv2.HttpApi(self, "HttpApi")
        
        api.add_routes(
            integration=HttpUrlIntegration("BooksIntegration", "https://get-books-proxy.myproxy.internal"),
            path="/books",
            authorizer=authorizer
        )
    '''

    def __init__(
        self,
        id: builtins.str,
        pool: aws_cdk.aws_cognito.IUserPool,
        *,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_pool_clients: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.IUserPoolClient]] = None,
        user_pool_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Initialize a Cognito user pool authorizer to be bound with HTTP route.

        :param id: The id of the underlying construct.
        :param pool: The user pool to use for authorization.
        :param authorizer_name: (experimental) Friendly name of the authorizer. Default: - same value as ``id`` passed in the constructor
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param user_pool_clients: (experimental) The user pool clients that should be used to authorize requests with the user pool. Default: - a new client will be created for the given user pool
        :param user_pool_region: (experimental) The AWS region in which the user pool is present. Default: - same region as the Route the authorizer is attached to.

        :stability: experimental
        '''
        props = HttpUserPoolAuthorizerProps(
            authorizer_name=authorizer_name,
            identity_source=identity_source,
            user_pool_clients=user_pool_clients,
            user_pool_region=user_pool_region,
        )

        jsii.create(self.__class__, self, [id, pool, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified Http route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteAuthorizerConfig, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.HttpUserPoolAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_name": "authorizerName",
        "identity_source": "identitySource",
        "user_pool_clients": "userPoolClients",
        "user_pool_region": "userPoolRegion",
    },
)
class HttpUserPoolAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_pool_clients: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.IUserPoolClient]] = None,
        user_pool_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties to initialize HttpUserPoolAuthorizer.

        :param authorizer_name: (experimental) Friendly name of the authorizer. Default: - same value as ``id`` passed in the constructor
        :param identity_source: (experimental) The identity source for which authorization is requested. Default: ['$request.header.Authorization']
        :param user_pool_clients: (experimental) The user pool clients that should be used to authorize requests with the user pool. Default: - a new client will be created for the given user pool
        :param user_pool_region: (experimental) The AWS region in which the user pool is present. Default: - same region as the Route the authorizer is attached to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_authorizers_alpha as apigatewayv2_authorizers_alpha
            from aws_cdk import aws_cognito as cognito
            
            # user_pool_client: cognito.UserPoolClient
            
            http_user_pool_authorizer_props = apigatewayv2_authorizers_alpha.HttpUserPoolAuthorizerProps(
                authorizer_name="authorizerName",
                identity_source=["identitySource"],
                user_pool_clients=[user_pool_client],
                user_pool_region="userPoolRegion"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if user_pool_clients is not None:
            self._values["user_pool_clients"] = user_pool_clients
        if user_pool_region is not None:
            self._values["user_pool_region"] = user_pool_region

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Friendly name of the authorizer.

        :default: - same value as ``id`` passed in the constructor

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The identity source for which authorization is requested.

        :default: ['$request.header.Authorization']

        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_pool_clients(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cognito.IUserPoolClient]]:
        '''(experimental) The user pool clients that should be used to authorize requests with the user pool.

        :default: - a new client will be created for the given user pool

        :stability: experimental
        '''
        result = self._values.get("user_pool_clients")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cognito.IUserPoolClient]], result)

    @builtins.property
    def user_pool_region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS region in which the user pool is present.

        :default: - same region as the Route the authorizer is attached to.

        :stability: experimental
        '''
        result = self._values.get("user_pool_region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpUserPoolAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IWebSocketRouteAuthorizer)
class WebSocketLambdaAuthorizer(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.WebSocketLambdaAuthorizer",
):
    '''(experimental) Authorize WebSocket Api routes via a lambda function.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_apigatewayv2_authorizers_alpha import WebSocketLambdaAuthorizer
        from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
        
        # This function handles your auth logic
        # auth_handler: lambda.Function
        
        # This function handles your WebSocket requests
        # handler: lambda.Function
        
        
        authorizer = WebSocketLambdaAuthorizer("Authorizer", auth_handler)
        
        integration = WebSocketLambdaIntegration("Integration", handler)
        
        apigwv2.WebSocketApi(self, "WebSocketApi",
            connect_route_options=apigwv2.WebSocketRouteOptions(
                integration=integration,
                authorizer=authorizer
            )
        )
    '''

    def __init__(
        self,
        id: builtins.str,
        handler: aws_cdk.aws_lambda.IFunction,
        *,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param id: -
        :param handler: -
        :param authorizer_name: (experimental) The name of the authorizer. Default: - same value as ``id`` passed in the constructor.
        :param identity_source: (experimental) The identity source for which authorization is requested. Request parameter match ``'route.request.querystring|header.[a-zA-z0-9._-]+'``. Staged variable match ``'stageVariables.[a-zA-Z0-9._-]+'``. Context parameter match ``'context.[a-zA-Z0-9._-]+'``. Default: ['route.request.header.Authorization']

        :stability: experimental
        '''
        props = WebSocketLambdaAuthorizerProps(
            authorizer_name=authorizer_name, identity_source=identity_source
        )

        jsii.create(self.__class__, self, [id, handler, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IWebSocketRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.WebSocketRouteAuthorizerConfig:
        '''(experimental) Bind this authorizer to a specified WebSocket route.

        :param route: (experimental) The route to which the authorizer is being bound.
        :param scope: (experimental) The scope for any constructs created as part of the bind.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.WebSocketRouteAuthorizerBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.WebSocketRouteAuthorizerConfig, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-authorizers-alpha.WebSocketLambdaAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_name": "authorizerName",
        "identity_source": "identitySource",
    },
)
class WebSocketLambdaAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_name: typing.Optional[builtins.str] = None,
        identity_source: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties to initialize WebSocketTokenAuthorizer.

        :param authorizer_name: (experimental) The name of the authorizer. Default: - same value as ``id`` passed in the constructor.
        :param identity_source: (experimental) The identity source for which authorization is requested. Request parameter match ``'route.request.querystring|header.[a-zA-z0-9._-]+'``. Staged variable match ``'stageVariables.[a-zA-Z0-9._-]+'``. Context parameter match ``'context.[a-zA-Z0-9._-]+'``. Default: ['route.request.header.Authorization']

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_authorizers_alpha as apigatewayv2_authorizers_alpha
            
            web_socket_lambda_authorizer_props = apigatewayv2_authorizers_alpha.WebSocketLambdaAuthorizerProps(
                authorizer_name="authorizerName",
                identity_source=["identitySource"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if identity_source is not None:
            self._values["identity_source"] = identity_source

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the authorizer.

        :default: - same value as ``id`` passed in the constructor.

        :stability: experimental
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The identity source for which authorization is requested.

        Request parameter match ``'route.request.querystring|header.[a-zA-z0-9._-]+'``.
        Staged variable match ``'stageVariables.[a-zA-Z0-9._-]+'``.
        Context parameter match ``'context.[a-zA-Z0-9._-]+'``.

        :default: ['route.request.header.Authorization']

        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketLambdaAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HttpIamAuthorizer",
    "HttpJwtAuthorizer",
    "HttpJwtAuthorizerProps",
    "HttpLambdaAuthorizer",
    "HttpLambdaAuthorizerProps",
    "HttpLambdaResponseType",
    "HttpUserPoolAuthorizer",
    "HttpUserPoolAuthorizerProps",
    "WebSocketLambdaAuthorizer",
    "WebSocketLambdaAuthorizerProps",
]

publication.publish()
