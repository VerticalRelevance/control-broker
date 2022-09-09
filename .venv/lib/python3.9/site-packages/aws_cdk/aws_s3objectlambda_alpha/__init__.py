'''
# AWS::S3ObjectLambda Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This construct library allows you to define S3 object lambda access points.

```python
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
import aws_cdk as cdk

stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    payload={
        "prop": "value"
    }
)
```

## Handling range and part number requests

Lambdas are currently limited to only transforming `GetObject` requests. However, they can additionally support `GetObject-Range` and `GetObject-PartNumber` requests, which needs to be specified in the access point configuration:

```python
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
import aws_cdk as cdk

stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    supports_get_object_range=True,
    supports_get_object_part_number=True
)
```

## Pass additional data to Lambda function

You can specify an additional object that provides supplemental data to the Lambda function used to transform objects. The data is delivered as a JSON payload to the Lambda:

```python
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
import aws_cdk as cdk

stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    payload={
        "prop": "value"
    }
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
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3objectlambda-alpha.AccessPointAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "access_point_arn": "accessPointArn",
        "access_point_creation_date": "accessPointCreationDate",
    },
)
class AccessPointAttributes:
    def __init__(
        self,
        *,
        access_point_arn: builtins.str,
        access_point_creation_date: builtins.str,
    ) -> None:
        '''(experimental) The access point resource attributes.

        :param access_point_arn: (experimental) The ARN of the access point.
        :param access_point_creation_date: (experimental) The creation data of the access point.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda_alpha
            
            access_point_attributes = s3objectlambda_alpha.AccessPointAttributes(
                access_point_arn="accessPointArn",
                access_point_creation_date="accessPointCreationDate"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "access_point_arn": access_point_arn,
            "access_point_creation_date": access_point_creation_date,
        }

    @builtins.property
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        '''
        result = self._values.get("access_point_arn")
        assert result is not None, "Required property 'access_point_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        '''
        result = self._values.get("access_point_creation_date")
        assert result is not None, "Required property 'access_point_creation_date' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3objectlambda-alpha.AccessPointProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "handler": "handler",
        "access_point_name": "accessPointName",
        "cloud_watch_metrics_enabled": "cloudWatchMetricsEnabled",
        "payload": "payload",
        "supports_get_object_part_number": "supportsGetObjectPartNumber",
        "supports_get_object_range": "supportsGetObjectRange",
    },
)
class AccessPointProps:
    def __init__(
        self,
        *,
        bucket: aws_cdk.aws_s3.IBucket,
        handler: aws_cdk.aws_lambda.IFunction,
        access_point_name: typing.Optional[builtins.str] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        supports_get_object_part_number: typing.Optional[builtins.bool] = None,
        supports_get_object_range: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) The S3 object lambda access point configuration.

        :param bucket: (experimental) The bucket to which this access point belongs.
        :param handler: (experimental) The Lambda function used to transform objects.
        :param access_point_name: (experimental) The name of the S3 object lambda access point. Default: a unique name will be generated
        :param cloud_watch_metrics_enabled: (experimental) Whether CloudWatch metrics are enabled for the access point. Default: false
        :param payload: (experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request. Default: - No data.
        :param supports_get_object_part_number: (experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests. Default: false
        :param supports_get_object_range: (experimental) Whether the Lambda function can process ``GetObject-Range`` requests. Default: false

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_lambda as lambda_
            import aws_cdk.aws_s3 as s3
            import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
            import aws_cdk as cdk
            
            stack = cdk.Stack()
            bucket = s3.Bucket(stack, "MyBucket")
            handler = lambda_.Function(stack, "MyFunction",
                runtime=lambda_.Runtime.NODEJS_14_X,
                handler="index.handler",
                code=lambda_.Code.from_asset("lambda.zip")
            )
            s3objectlambda.AccessPoint(stack, "MyObjectLambda",
                bucket=bucket,
                handler=handler,
                access_point_name="my-access-point",
                payload={
                    "prop": "value"
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "handler": handler,
        }
        if access_point_name is not None:
            self._values["access_point_name"] = access_point_name
        if cloud_watch_metrics_enabled is not None:
            self._values["cloud_watch_metrics_enabled"] = cloud_watch_metrics_enabled
        if payload is not None:
            self._values["payload"] = payload
        if supports_get_object_part_number is not None:
            self._values["supports_get_object_part_number"] = supports_get_object_part_number
        if supports_get_object_range is not None:
            self._values["supports_get_object_range"] = supports_get_object_range

    @builtins.property
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) The bucket to which this access point belongs.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def handler(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The Lambda function used to transform objects.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def access_point_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the S3 object lambda access point.

        :default: a unique name will be generated

        :stability: experimental
        '''
        result = self._values.get("access_point_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_watch_metrics_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether CloudWatch metrics are enabled for the access point.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("cloud_watch_metrics_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def payload(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request.

        :default: - No data.

        :stability: experimental
        '''
        result = self._values.get("payload")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def supports_get_object_part_number(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("supports_get_object_part_number")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def supports_get_object_range(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the Lambda function can process ``GetObject-Range`` requests.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("supports_get_object_range")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-s3objectlambda-alpha.IAccessPoint")
class IAccessPoint(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) The interface that represents the AccessPoint resource.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The IPv4 DNS name of the access point.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The regional domain name of the access point.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) The virtual hosted-style URL of an S3 object through this access point.

        Specify ``regional: false`` at the options for non-regional URL.

        :param key: The S3 key of the object. If not specified, the URL of the bucket is returned.
        :param regional: Specifies the URL includes the region. Default: - true

        :return: an ObjectS3Url token

        :stability: experimental
        '''
        ...


class _IAccessPointProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) The interface that represents the AccessPoint resource.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-s3objectlambda-alpha.IAccessPoint"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointCreationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The IPv4 DNS name of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The regional domain name of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) The virtual hosted-style URL of an S3 object through this access point.

        Specify ``regional: false`` at the options for non-regional URL.

        :param key: The S3 key of the object. If not specified, the URL of the bucket is returned.
        :param regional: Specifies the URL includes the region. Default: - true

        :return: an ObjectS3Url token

        :stability: experimental
        '''
        options = aws_cdk.aws_s3.VirtualHostedStyleUrlOptions(regional=regional)

        return typing.cast(builtins.str, jsii.invoke(self, "virtualHostedUrlForObject", [key, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccessPoint).__jsii_proxy_class__ = lambda : _IAccessPointProxy


@jsii.implements(IAccessPoint)
class AccessPoint(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-s3objectlambda-alpha.AccessPoint",
):
    '''(experimental) An S3 object lambda access point for intercepting and transforming ``GetObject`` requests.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_lambda as lambda_
        import aws_cdk.aws_s3 as s3
        import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
        import aws_cdk as cdk
        
        stack = cdk.Stack()
        bucket = s3.Bucket(stack, "MyBucket")
        handler = lambda_.Function(stack, "MyFunction",
            runtime=lambda_.Runtime.NODEJS_14_X,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda.zip")
        )
        s3objectlambda.AccessPoint(stack, "MyObjectLambda",
            bucket=bucket,
            handler=handler,
            access_point_name="my-access-point",
            payload={
                "prop": "value"
            }
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: aws_cdk.aws_s3.IBucket,
        handler: aws_cdk.aws_lambda.IFunction,
        access_point_name: typing.Optional[builtins.str] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        supports_get_object_part_number: typing.Optional[builtins.bool] = None,
        supports_get_object_range: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket: (experimental) The bucket to which this access point belongs.
        :param handler: (experimental) The Lambda function used to transform objects.
        :param access_point_name: (experimental) The name of the S3 object lambda access point. Default: a unique name will be generated
        :param cloud_watch_metrics_enabled: (experimental) Whether CloudWatch metrics are enabled for the access point. Default: false
        :param payload: (experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request. Default: - No data.
        :param supports_get_object_part_number: (experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests. Default: false
        :param supports_get_object_range: (experimental) Whether the Lambda function can process ``GetObject-Range`` requests. Default: false

        :stability: experimental
        '''
        props = AccessPointProps(
            bucket=bucket,
            handler=handler,
            access_point_name=access_point_name,
            cloud_watch_metrics_enabled=cloud_watch_metrics_enabled,
            payload=payload,
            supports_get_object_part_number=supports_get_object_part_number,
            supports_get_object_range=supports_get_object_range,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAccessPointAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_access_point_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_point_arn: builtins.str,
        access_point_creation_date: builtins.str,
    ) -> IAccessPoint:
        '''(experimental) Reference an existing AccessPoint defined outside of the CDK code.

        :param scope: -
        :param id: -
        :param access_point_arn: (experimental) The ARN of the access point.
        :param access_point_creation_date: (experimental) The creation data of the access point.

        :stability: experimental
        '''
        attrs = AccessPointAttributes(
            access_point_arn=access_point_arn,
            access_point_creation_date=access_point_creation_date,
        )

        return typing.cast(IAccessPoint, jsii.sinvoke(cls, "fromAccessPointAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) Implement the {@link IAccessPoint.virtualHostedUrlForObject} method.

        :param key: -
        :param regional: Specifies the URL includes the region. Default: - true

        :stability: experimental
        '''
        options = aws_cdk.aws_s3.VirtualHostedStyleUrlOptions(regional=regional)

        return typing.cast(builtins.str, jsii.invoke(self, "virtualHostedUrlForObject", [key, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointCreationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointName")
    def access_point_name(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) Implement the {@link IAccessPoint.domainName} field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) Implement the {@link IAccessPoint.regionalDomainName} field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))


__all__ = [
    "AccessPoint",
    "AccessPointAttributes",
    "AccessPointProps",
    "IAccessPoint",
]

publication.publish()
