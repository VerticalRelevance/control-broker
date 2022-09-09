'''
# AWS::BillingConductor Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_billingconductor as billingconductor
```

<!--BEGIN CFNONLY DISCLAIMER-->

There are no official hand-written ([L2](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) constructs for this service yet. Here are some suggestions on how to proceed:

* Search [Construct Hub for BillingConductor construct libraries](https://constructs.dev/search?q=billingconductor)
* Use the automatically generated [L1](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_l1_using) constructs, in the same way you would use [the CloudFormation AWS::BillingConductor resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_BillingConductor.html) directly.

(Read the [CDK Contributing Guide](https://github.com/aws/aws-cdk/blob/master/CONTRIBUTING.md) if you are interested in contributing to this construct library.)

<!--END CFNONLY DISCLAIMER-->
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_9df397a6,
    CfnTag as _CfnTag_f6864754,
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnBillingGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnBillingGroup",
):
    '''A CloudFormation ``AWS::BillingConductor::BillingGroup``.

    :cloudformationResource: AWS::BillingConductor::BillingGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_billingconductor as billingconductor
        
        cfn_billing_group = billingconductor.CfnBillingGroup(self, "MyCfnBillingGroup",
            account_grouping=billingconductor.CfnBillingGroup.AccountGroupingProperty(
                linked_account_ids=["linkedAccountIds"]
            ),
            computation_preference=billingconductor.CfnBillingGroup.ComputationPreferenceProperty(
                pricing_plan_arn="pricingPlanArn"
            ),
            name="name",
            primary_account_id="primaryAccountId",
        
            # the properties below are optional
            description="description",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_grouping: typing.Union["CfnBillingGroup.AccountGroupingProperty", _IResolvable_da3f097b],
        computation_preference: typing.Union["CfnBillingGroup.ComputationPreferenceProperty", _IResolvable_da3f097b],
        name: builtins.str,
        primary_account_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::BillingConductor::BillingGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param account_grouping: ``AWS::BillingConductor::BillingGroup.AccountGrouping``.
        :param computation_preference: ``AWS::BillingConductor::BillingGroup.ComputationPreference``.
        :param name: ``AWS::BillingConductor::BillingGroup.Name``.
        :param primary_account_id: ``AWS::BillingConductor::BillingGroup.PrimaryAccountId``.
        :param description: ``AWS::BillingConductor::BillingGroup.Description``.
        :param tags: ``AWS::BillingConductor::BillingGroup.Tags``.
        '''
        props = CfnBillingGroupProps(
            account_grouping=account_grouping,
            computation_preference=computation_preference,
            name=name,
            primary_account_id=primary_account_id,
            description=description,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLastModifiedTime")
    def attr_last_modified_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: LastModifiedTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrLastModifiedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrSize")
    def attr_size(self) -> jsii.Number:
        '''
        :cloudformationAttribute: Size
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatusReason")
    def attr_status_reason(self) -> builtins.str:
        '''
        :cloudformationAttribute: StatusReason
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::BillingConductor::BillingGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountGrouping")
    def account_grouping(
        self,
    ) -> typing.Union["CfnBillingGroup.AccountGroupingProperty", _IResolvable_da3f097b]:
        '''``AWS::BillingConductor::BillingGroup.AccountGrouping``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-accountgrouping
        '''
        return typing.cast(typing.Union["CfnBillingGroup.AccountGroupingProperty", _IResolvable_da3f097b], jsii.get(self, "accountGrouping"))

    @account_grouping.setter
    def account_grouping(
        self,
        value: typing.Union["CfnBillingGroup.AccountGroupingProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "accountGrouping", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computationPreference")
    def computation_preference(
        self,
    ) -> typing.Union["CfnBillingGroup.ComputationPreferenceProperty", _IResolvable_da3f097b]:
        '''``AWS::BillingConductor::BillingGroup.ComputationPreference``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-computationpreference
        '''
        return typing.cast(typing.Union["CfnBillingGroup.ComputationPreferenceProperty", _IResolvable_da3f097b], jsii.get(self, "computationPreference"))

    @computation_preference.setter
    def computation_preference(
        self,
        value: typing.Union["CfnBillingGroup.ComputationPreferenceProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "computationPreference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::BillingGroup.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryAccountId")
    def primary_account_id(self) -> builtins.str:
        '''``AWS::BillingConductor::BillingGroup.PrimaryAccountId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-primaryaccountid
        '''
        return typing.cast(builtins.str, jsii.get(self, "primaryAccountId"))

    @primary_account_id.setter
    def primary_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "primaryAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::BillingGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_billingconductor.CfnBillingGroup.AccountGroupingProperty",
        jsii_struct_bases=[],
        name_mapping={"linked_account_ids": "linkedAccountIds"},
    )
    class AccountGroupingProperty:
        def __init__(
            self,
            *,
            linked_account_ids: typing.Sequence[builtins.str],
        ) -> None:
            '''
            :param linked_account_ids: ``CfnBillingGroup.AccountGroupingProperty.LinkedAccountIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-billinggroup-accountgrouping.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_billingconductor as billingconductor
                
                account_grouping_property = billingconductor.CfnBillingGroup.AccountGroupingProperty(
                    linked_account_ids=["linkedAccountIds"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "linked_account_ids": linked_account_ids,
            }

        @builtins.property
        def linked_account_ids(self) -> typing.List[builtins.str]:
            '''``CfnBillingGroup.AccountGroupingProperty.LinkedAccountIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-billinggroup-accountgrouping.html#cfn-billingconductor-billinggroup-accountgrouping-linkedaccountids
            '''
            result = self._values.get("linked_account_ids")
            assert result is not None, "Required property 'linked_account_ids' is missing"
            return typing.cast(typing.List[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AccountGroupingProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_billingconductor.CfnBillingGroup.ComputationPreferenceProperty",
        jsii_struct_bases=[],
        name_mapping={"pricing_plan_arn": "pricingPlanArn"},
    )
    class ComputationPreferenceProperty:
        def __init__(self, *, pricing_plan_arn: builtins.str) -> None:
            '''
            :param pricing_plan_arn: ``CfnBillingGroup.ComputationPreferenceProperty.PricingPlanArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-billinggroup-computationpreference.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_billingconductor as billingconductor
                
                computation_preference_property = billingconductor.CfnBillingGroup.ComputationPreferenceProperty(
                    pricing_plan_arn="pricingPlanArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "pricing_plan_arn": pricing_plan_arn,
            }

        @builtins.property
        def pricing_plan_arn(self) -> builtins.str:
            '''``CfnBillingGroup.ComputationPreferenceProperty.PricingPlanArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-billinggroup-computationpreference.html#cfn-billingconductor-billinggroup-computationpreference-pricingplanarn
            '''
            result = self._values.get("pricing_plan_arn")
            assert result is not None, "Required property 'pricing_plan_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ComputationPreferenceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnBillingGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_grouping": "accountGrouping",
        "computation_preference": "computationPreference",
        "name": "name",
        "primary_account_id": "primaryAccountId",
        "description": "description",
        "tags": "tags",
    },
)
class CfnBillingGroupProps:
    def __init__(
        self,
        *,
        account_grouping: typing.Union[CfnBillingGroup.AccountGroupingProperty, _IResolvable_da3f097b],
        computation_preference: typing.Union[CfnBillingGroup.ComputationPreferenceProperty, _IResolvable_da3f097b],
        name: builtins.str,
        primary_account_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``CfnBillingGroup``.

        :param account_grouping: ``AWS::BillingConductor::BillingGroup.AccountGrouping``.
        :param computation_preference: ``AWS::BillingConductor::BillingGroup.ComputationPreference``.
        :param name: ``AWS::BillingConductor::BillingGroup.Name``.
        :param primary_account_id: ``AWS::BillingConductor::BillingGroup.PrimaryAccountId``.
        :param description: ``AWS::BillingConductor::BillingGroup.Description``.
        :param tags: ``AWS::BillingConductor::BillingGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_billingconductor as billingconductor
            
            cfn_billing_group_props = billingconductor.CfnBillingGroupProps(
                account_grouping=billingconductor.CfnBillingGroup.AccountGroupingProperty(
                    linked_account_ids=["linkedAccountIds"]
                ),
                computation_preference=billingconductor.CfnBillingGroup.ComputationPreferenceProperty(
                    pricing_plan_arn="pricingPlanArn"
                ),
                name="name",
                primary_account_id="primaryAccountId",
            
                # the properties below are optional
                description="description",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_grouping": account_grouping,
            "computation_preference": computation_preference,
            "name": name,
            "primary_account_id": primary_account_id,
        }
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def account_grouping(
        self,
    ) -> typing.Union[CfnBillingGroup.AccountGroupingProperty, _IResolvable_da3f097b]:
        '''``AWS::BillingConductor::BillingGroup.AccountGrouping``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-accountgrouping
        '''
        result = self._values.get("account_grouping")
        assert result is not None, "Required property 'account_grouping' is missing"
        return typing.cast(typing.Union[CfnBillingGroup.AccountGroupingProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def computation_preference(
        self,
    ) -> typing.Union[CfnBillingGroup.ComputationPreferenceProperty, _IResolvable_da3f097b]:
        '''``AWS::BillingConductor::BillingGroup.ComputationPreference``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-computationpreference
        '''
        result = self._values.get("computation_preference")
        assert result is not None, "Required property 'computation_preference' is missing"
        return typing.cast(typing.Union[CfnBillingGroup.ComputationPreferenceProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::BillingGroup.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary_account_id(self) -> builtins.str:
        '''``AWS::BillingConductor::BillingGroup.PrimaryAccountId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-primaryaccountid
        '''
        result = self._values.get("primary_account_id")
        assert result is not None, "Required property 'primary_account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::BillingGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::BillingConductor::BillingGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-billinggroup.html#cfn-billingconductor-billinggroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnBillingGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnCustomLineItem(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnCustomLineItem",
):
    '''A CloudFormation ``AWS::BillingConductor::CustomLineItem``.

    :cloudformationResource: AWS::BillingConductor::CustomLineItem
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_billingconductor as billingconductor
        
        cfn_custom_line_item = billingconductor.CfnCustomLineItem(self, "MyCfnCustomLineItem",
            billing_group_arn="billingGroupArn",
            name="name",
        
            # the properties below are optional
            billing_period_range=billingconductor.CfnCustomLineItem.BillingPeriodRangeProperty(
                exclusive_end_billing_period="exclusiveEndBillingPeriod",
                inclusive_start_billing_period="inclusiveStartBillingPeriod"
            ),
            custom_line_item_charge_details=billingconductor.CfnCustomLineItem.CustomLineItemChargeDetailsProperty(
                type="type",
        
                # the properties below are optional
                flat=billingconductor.CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty(
                    charge_value=123
                ),
                percentage=billingconductor.CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty(
                    percentage_value=123,
        
                    # the properties below are optional
                    child_associated_resources=["childAssociatedResources"]
                )
            ),
            description="description",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        billing_group_arn: builtins.str,
        name: builtins.str,
        billing_period_range: typing.Optional[typing.Union["CfnCustomLineItem.BillingPeriodRangeProperty", _IResolvable_da3f097b]] = None,
        custom_line_item_charge_details: typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemChargeDetailsProperty", _IResolvable_da3f097b]] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::BillingConductor::CustomLineItem``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param billing_group_arn: ``AWS::BillingConductor::CustomLineItem.BillingGroupArn``.
        :param name: ``AWS::BillingConductor::CustomLineItem.Name``.
        :param billing_period_range: ``AWS::BillingConductor::CustomLineItem.BillingPeriodRange``.
        :param custom_line_item_charge_details: ``AWS::BillingConductor::CustomLineItem.CustomLineItemChargeDetails``.
        :param description: ``AWS::BillingConductor::CustomLineItem.Description``.
        :param tags: ``AWS::BillingConductor::CustomLineItem.Tags``.
        '''
        props = CfnCustomLineItemProps(
            billing_group_arn=billing_group_arn,
            name=name,
            billing_period_range=billing_period_range,
            custom_line_item_charge_details=custom_line_item_charge_details,
            description=description,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrAssociationSize")
    def attr_association_size(self) -> jsii.Number:
        '''
        :cloudformationAttribute: AssociationSize
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrAssociationSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCurrencyCode")
    def attr_currency_code(self) -> builtins.str:
        '''
        :cloudformationAttribute: CurrencyCode
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCurrencyCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLastModifiedTime")
    def attr_last_modified_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: LastModifiedTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrLastModifiedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrProductCode")
    def attr_product_code(self) -> builtins.str:
        '''
        :cloudformationAttribute: ProductCode
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrProductCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::BillingConductor::CustomLineItem.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="billingGroupArn")
    def billing_group_arn(self) -> builtins.str:
        '''``AWS::BillingConductor::CustomLineItem.BillingGroupArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-billinggrouparn
        '''
        return typing.cast(builtins.str, jsii.get(self, "billingGroupArn"))

    @billing_group_arn.setter
    def billing_group_arn(self, value: builtins.str) -> None:
        jsii.set(self, "billingGroupArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::CustomLineItem.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="billingPeriodRange")
    def billing_period_range(
        self,
    ) -> typing.Optional[typing.Union["CfnCustomLineItem.BillingPeriodRangeProperty", _IResolvable_da3f097b]]:
        '''``AWS::BillingConductor::CustomLineItem.BillingPeriodRange``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-billingperiodrange
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCustomLineItem.BillingPeriodRangeProperty", _IResolvable_da3f097b]], jsii.get(self, "billingPeriodRange"))

    @billing_period_range.setter
    def billing_period_range(
        self,
        value: typing.Optional[typing.Union["CfnCustomLineItem.BillingPeriodRangeProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "billingPeriodRange", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customLineItemChargeDetails")
    def custom_line_item_charge_details(
        self,
    ) -> typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemChargeDetailsProperty", _IResolvable_da3f097b]]:
        '''``AWS::BillingConductor::CustomLineItem.CustomLineItemChargeDetails``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-customlineitemchargedetails
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemChargeDetailsProperty", _IResolvable_da3f097b]], jsii.get(self, "customLineItemChargeDetails"))

    @custom_line_item_charge_details.setter
    def custom_line_item_charge_details(
        self,
        value: typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemChargeDetailsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "customLineItemChargeDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::CustomLineItem.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_billingconductor.CfnCustomLineItem.BillingPeriodRangeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "exclusive_end_billing_period": "exclusiveEndBillingPeriod",
            "inclusive_start_billing_period": "inclusiveStartBillingPeriod",
        },
    )
    class BillingPeriodRangeProperty:
        def __init__(
            self,
            *,
            exclusive_end_billing_period: typing.Optional[builtins.str] = None,
            inclusive_start_billing_period: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param exclusive_end_billing_period: ``CfnCustomLineItem.BillingPeriodRangeProperty.ExclusiveEndBillingPeriod``.
            :param inclusive_start_billing_period: ``CfnCustomLineItem.BillingPeriodRangeProperty.InclusiveStartBillingPeriod``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-billingperiodrange.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_billingconductor as billingconductor
                
                billing_period_range_property = billingconductor.CfnCustomLineItem.BillingPeriodRangeProperty(
                    exclusive_end_billing_period="exclusiveEndBillingPeriod",
                    inclusive_start_billing_period="inclusiveStartBillingPeriod"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if exclusive_end_billing_period is not None:
                self._values["exclusive_end_billing_period"] = exclusive_end_billing_period
            if inclusive_start_billing_period is not None:
                self._values["inclusive_start_billing_period"] = inclusive_start_billing_period

        @builtins.property
        def exclusive_end_billing_period(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomLineItem.BillingPeriodRangeProperty.ExclusiveEndBillingPeriod``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-billingperiodrange.html#cfn-billingconductor-customlineitem-billingperiodrange-exclusiveendbillingperiod
            '''
            result = self._values.get("exclusive_end_billing_period")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def inclusive_start_billing_period(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomLineItem.BillingPeriodRangeProperty.InclusiveStartBillingPeriod``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-billingperiodrange.html#cfn-billingconductor-customlineitem-billingperiodrange-inclusivestartbillingperiod
            '''
            result = self._values.get("inclusive_start_billing_period")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BillingPeriodRangeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_billingconductor.CfnCustomLineItem.CustomLineItemChargeDetailsProperty",
        jsii_struct_bases=[],
        name_mapping={"type": "type", "flat": "flat", "percentage": "percentage"},
    )
    class CustomLineItemChargeDetailsProperty:
        def __init__(
            self,
            *,
            type: builtins.str,
            flat: typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty", _IResolvable_da3f097b]] = None,
            percentage: typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param type: ``CfnCustomLineItem.CustomLineItemChargeDetailsProperty.Type``.
            :param flat: ``CfnCustomLineItem.CustomLineItemChargeDetailsProperty.Flat``.
            :param percentage: ``CfnCustomLineItem.CustomLineItemChargeDetailsProperty.Percentage``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitemchargedetails.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_billingconductor as billingconductor
                
                custom_line_item_charge_details_property = billingconductor.CfnCustomLineItem.CustomLineItemChargeDetailsProperty(
                    type="type",
                
                    # the properties below are optional
                    flat=billingconductor.CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty(
                        charge_value=123
                    ),
                    percentage=billingconductor.CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty(
                        percentage_value=123,
                
                        # the properties below are optional
                        child_associated_resources=["childAssociatedResources"]
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "type": type,
            }
            if flat is not None:
                self._values["flat"] = flat
            if percentage is not None:
                self._values["percentage"] = percentage

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnCustomLineItem.CustomLineItemChargeDetailsProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitemchargedetails.html#cfn-billingconductor-customlineitem-customlineitemchargedetails-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def flat(
            self,
        ) -> typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty", _IResolvable_da3f097b]]:
            '''``CfnCustomLineItem.CustomLineItemChargeDetailsProperty.Flat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitemchargedetails.html#cfn-billingconductor-customlineitem-customlineitemchargedetails-flat
            '''
            result = self._values.get("flat")
            return typing.cast(typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def percentage(
            self,
        ) -> typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty", _IResolvable_da3f097b]]:
            '''``CfnCustomLineItem.CustomLineItemChargeDetailsProperty.Percentage``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitemchargedetails.html#cfn-billingconductor-customlineitem-customlineitemchargedetails-percentage
            '''
            result = self._values.get("percentage")
            return typing.cast(typing.Optional[typing.Union["CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CustomLineItemChargeDetailsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_billingconductor.CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty",
        jsii_struct_bases=[],
        name_mapping={"charge_value": "chargeValue"},
    )
    class CustomLineItemFlatChargeDetailsProperty:
        def __init__(self, *, charge_value: jsii.Number) -> None:
            '''
            :param charge_value: ``CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty.ChargeValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitemflatchargedetails.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_billingconductor as billingconductor
                
                custom_line_item_flat_charge_details_property = billingconductor.CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty(
                    charge_value=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "charge_value": charge_value,
            }

        @builtins.property
        def charge_value(self) -> jsii.Number:
            '''``CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty.ChargeValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitemflatchargedetails.html#cfn-billingconductor-customlineitem-customlineitemflatchargedetails-chargevalue
            '''
            result = self._values.get("charge_value")
            assert result is not None, "Required property 'charge_value' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CustomLineItemFlatChargeDetailsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_billingconductor.CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "percentage_value": "percentageValue",
            "child_associated_resources": "childAssociatedResources",
        },
    )
    class CustomLineItemPercentageChargeDetailsProperty:
        def __init__(
            self,
            *,
            percentage_value: jsii.Number,
            child_associated_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param percentage_value: ``CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty.PercentageValue``.
            :param child_associated_resources: ``CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty.ChildAssociatedResources``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitempercentagechargedetails.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_billingconductor as billingconductor
                
                custom_line_item_percentage_charge_details_property = billingconductor.CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty(
                    percentage_value=123,
                
                    # the properties below are optional
                    child_associated_resources=["childAssociatedResources"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "percentage_value": percentage_value,
            }
            if child_associated_resources is not None:
                self._values["child_associated_resources"] = child_associated_resources

        @builtins.property
        def percentage_value(self) -> jsii.Number:
            '''``CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty.PercentageValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitempercentagechargedetails.html#cfn-billingconductor-customlineitem-customlineitempercentagechargedetails-percentagevalue
            '''
            result = self._values.get("percentage_value")
            assert result is not None, "Required property 'percentage_value' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def child_associated_resources(
            self,
        ) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty.ChildAssociatedResources``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-billingconductor-customlineitem-customlineitempercentagechargedetails.html#cfn-billingconductor-customlineitem-customlineitempercentagechargedetails-childassociatedresources
            '''
            result = self._values.get("child_associated_resources")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CustomLineItemPercentageChargeDetailsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnCustomLineItemProps",
    jsii_struct_bases=[],
    name_mapping={
        "billing_group_arn": "billingGroupArn",
        "name": "name",
        "billing_period_range": "billingPeriodRange",
        "custom_line_item_charge_details": "customLineItemChargeDetails",
        "description": "description",
        "tags": "tags",
    },
)
class CfnCustomLineItemProps:
    def __init__(
        self,
        *,
        billing_group_arn: builtins.str,
        name: builtins.str,
        billing_period_range: typing.Optional[typing.Union[CfnCustomLineItem.BillingPeriodRangeProperty, _IResolvable_da3f097b]] = None,
        custom_line_item_charge_details: typing.Optional[typing.Union[CfnCustomLineItem.CustomLineItemChargeDetailsProperty, _IResolvable_da3f097b]] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``CfnCustomLineItem``.

        :param billing_group_arn: ``AWS::BillingConductor::CustomLineItem.BillingGroupArn``.
        :param name: ``AWS::BillingConductor::CustomLineItem.Name``.
        :param billing_period_range: ``AWS::BillingConductor::CustomLineItem.BillingPeriodRange``.
        :param custom_line_item_charge_details: ``AWS::BillingConductor::CustomLineItem.CustomLineItemChargeDetails``.
        :param description: ``AWS::BillingConductor::CustomLineItem.Description``.
        :param tags: ``AWS::BillingConductor::CustomLineItem.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_billingconductor as billingconductor
            
            cfn_custom_line_item_props = billingconductor.CfnCustomLineItemProps(
                billing_group_arn="billingGroupArn",
                name="name",
            
                # the properties below are optional
                billing_period_range=billingconductor.CfnCustomLineItem.BillingPeriodRangeProperty(
                    exclusive_end_billing_period="exclusiveEndBillingPeriod",
                    inclusive_start_billing_period="inclusiveStartBillingPeriod"
                ),
                custom_line_item_charge_details=billingconductor.CfnCustomLineItem.CustomLineItemChargeDetailsProperty(
                    type="type",
            
                    # the properties below are optional
                    flat=billingconductor.CfnCustomLineItem.CustomLineItemFlatChargeDetailsProperty(
                        charge_value=123
                    ),
                    percentage=billingconductor.CfnCustomLineItem.CustomLineItemPercentageChargeDetailsProperty(
                        percentage_value=123,
            
                        # the properties below are optional
                        child_associated_resources=["childAssociatedResources"]
                    )
                ),
                description="description",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "billing_group_arn": billing_group_arn,
            "name": name,
        }
        if billing_period_range is not None:
            self._values["billing_period_range"] = billing_period_range
        if custom_line_item_charge_details is not None:
            self._values["custom_line_item_charge_details"] = custom_line_item_charge_details
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def billing_group_arn(self) -> builtins.str:
        '''``AWS::BillingConductor::CustomLineItem.BillingGroupArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-billinggrouparn
        '''
        result = self._values.get("billing_group_arn")
        assert result is not None, "Required property 'billing_group_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::CustomLineItem.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def billing_period_range(
        self,
    ) -> typing.Optional[typing.Union[CfnCustomLineItem.BillingPeriodRangeProperty, _IResolvable_da3f097b]]:
        '''``AWS::BillingConductor::CustomLineItem.BillingPeriodRange``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-billingperiodrange
        '''
        result = self._values.get("billing_period_range")
        return typing.cast(typing.Optional[typing.Union[CfnCustomLineItem.BillingPeriodRangeProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def custom_line_item_charge_details(
        self,
    ) -> typing.Optional[typing.Union[CfnCustomLineItem.CustomLineItemChargeDetailsProperty, _IResolvable_da3f097b]]:
        '''``AWS::BillingConductor::CustomLineItem.CustomLineItemChargeDetails``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-customlineitemchargedetails
        '''
        result = self._values.get("custom_line_item_charge_details")
        return typing.cast(typing.Optional[typing.Union[CfnCustomLineItem.CustomLineItemChargeDetailsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::CustomLineItem.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::BillingConductor::CustomLineItem.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-customlineitem.html#cfn-billingconductor-customlineitem-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCustomLineItemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnPricingPlan(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnPricingPlan",
):
    '''A CloudFormation ``AWS::BillingConductor::PricingPlan``.

    :cloudformationResource: AWS::BillingConductor::PricingPlan
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_billingconductor as billingconductor
        
        cfn_pricing_plan = billingconductor.CfnPricingPlan(self, "MyCfnPricingPlan",
            name="name",
        
            # the properties below are optional
            description="description",
            pricing_rule_arns=["pricingRuleArns"],
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        pricing_rule_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::BillingConductor::PricingPlan``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param name: ``AWS::BillingConductor::PricingPlan.Name``.
        :param description: ``AWS::BillingConductor::PricingPlan.Description``.
        :param pricing_rule_arns: ``AWS::BillingConductor::PricingPlan.PricingRuleArns``.
        :param tags: ``AWS::BillingConductor::PricingPlan.Tags``.
        '''
        props = CfnPricingPlanProps(
            name=name,
            description=description,
            pricing_rule_arns=pricing_rule_arns,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLastModifiedTime")
    def attr_last_modified_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: LastModifiedTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrLastModifiedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrSize")
    def attr_size(self) -> jsii.Number:
        '''
        :cloudformationAttribute: Size
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::BillingConductor::PricingPlan.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingPlan.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::PricingPlan.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pricingRuleArns")
    def pricing_rule_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::BillingConductor::PricingPlan.PricingRuleArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-pricingrulearns
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pricingRuleArns"))

    @pricing_rule_arns.setter
    def pricing_rule_arns(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "pricingRuleArns", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnPricingPlanProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "description": "description",
        "pricing_rule_arns": "pricingRuleArns",
        "tags": "tags",
    },
)
class CfnPricingPlanProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        pricing_rule_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``CfnPricingPlan``.

        :param name: ``AWS::BillingConductor::PricingPlan.Name``.
        :param description: ``AWS::BillingConductor::PricingPlan.Description``.
        :param pricing_rule_arns: ``AWS::BillingConductor::PricingPlan.PricingRuleArns``.
        :param tags: ``AWS::BillingConductor::PricingPlan.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_billingconductor as billingconductor
            
            cfn_pricing_plan_props = billingconductor.CfnPricingPlanProps(
                name="name",
            
                # the properties below are optional
                description="description",
                pricing_rule_arns=["pricingRuleArns"],
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if pricing_rule_arns is not None:
            self._values["pricing_rule_arns"] = pricing_rule_arns
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingPlan.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::PricingPlan.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pricing_rule_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::BillingConductor::PricingPlan.PricingRuleArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-pricingrulearns
        '''
        result = self._values.get("pricing_rule_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::BillingConductor::PricingPlan.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingplan.html#cfn-billingconductor-pricingplan-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPricingPlanProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnPricingRule(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnPricingRule",
):
    '''A CloudFormation ``AWS::BillingConductor::PricingRule``.

    :cloudformationResource: AWS::BillingConductor::PricingRule
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_billingconductor as billingconductor
        
        cfn_pricing_rule = billingconductor.CfnPricingRule(self, "MyCfnPricingRule",
            modifier_percentage=123,
            name="name",
            scope="scope",
            type="type",
        
            # the properties below are optional
            description="description",
            service="service",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope_: constructs.Construct,
        id: builtins.str,
        *,
        modifier_percentage: jsii.Number,
        name: builtins.str,
        scope: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::BillingConductor::PricingRule``.

        :param scope_: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param modifier_percentage: ``AWS::BillingConductor::PricingRule.ModifierPercentage``.
        :param name: ``AWS::BillingConductor::PricingRule.Name``.
        :param scope: ``AWS::BillingConductor::PricingRule.Scope``.
        :param type: ``AWS::BillingConductor::PricingRule.Type``.
        :param description: ``AWS::BillingConductor::PricingRule.Description``.
        :param service: ``AWS::BillingConductor::PricingRule.Service``.
        :param tags: ``AWS::BillingConductor::PricingRule.Tags``.
        '''
        props = CfnPricingRuleProps(
            modifier_percentage=modifier_percentage,
            name=name,
            scope=scope,
            type=type,
            description=description,
            service=service,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope_, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrAssociatedPricingPlanCount")
    def attr_associated_pricing_plan_count(self) -> jsii.Number:
        '''
        :cloudformationAttribute: AssociatedPricingPlanCount
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrAssociatedPricingPlanCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreationTime")
    def attr_creation_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: CreationTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLastModifiedTime")
    def attr_last_modified_time(self) -> jsii.Number:
        '''
        :cloudformationAttribute: LastModifiedTime
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrLastModifiedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::BillingConductor::PricingRule.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modifierPercentage")
    def modifier_percentage(self) -> jsii.Number:
        '''``AWS::BillingConductor::PricingRule.ModifierPercentage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-modifierpercentage
        '''
        return typing.cast(jsii.Number, jsii.get(self, "modifierPercentage"))

    @modifier_percentage.setter
    def modifier_percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "modifierPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingRule.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingRule.Scope``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-scope
        '''
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        jsii.set(self, "scope", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingRule.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-type
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::PricingRule.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::PricingRule.Service``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-service
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "service"))

    @service.setter
    def service(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "service", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_billingconductor.CfnPricingRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "modifier_percentage": "modifierPercentage",
        "name": "name",
        "scope": "scope",
        "type": "type",
        "description": "description",
        "service": "service",
        "tags": "tags",
    },
)
class CfnPricingRuleProps:
    def __init__(
        self,
        *,
        modifier_percentage: jsii.Number,
        name: builtins.str,
        scope: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``CfnPricingRule``.

        :param modifier_percentage: ``AWS::BillingConductor::PricingRule.ModifierPercentage``.
        :param name: ``AWS::BillingConductor::PricingRule.Name``.
        :param scope: ``AWS::BillingConductor::PricingRule.Scope``.
        :param type: ``AWS::BillingConductor::PricingRule.Type``.
        :param description: ``AWS::BillingConductor::PricingRule.Description``.
        :param service: ``AWS::BillingConductor::PricingRule.Service``.
        :param tags: ``AWS::BillingConductor::PricingRule.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_billingconductor as billingconductor
            
            cfn_pricing_rule_props = billingconductor.CfnPricingRuleProps(
                modifier_percentage=123,
                name="name",
                scope="scope",
                type="type",
            
                # the properties below are optional
                description="description",
                service="service",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "modifier_percentage": modifier_percentage,
            "name": name,
            "scope": scope,
            "type": type,
        }
        if description is not None:
            self._values["description"] = description
        if service is not None:
            self._values["service"] = service
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def modifier_percentage(self) -> jsii.Number:
        '''``AWS::BillingConductor::PricingRule.ModifierPercentage``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-modifierpercentage
        '''
        result = self._values.get("modifier_percentage")
        assert result is not None, "Required property 'modifier_percentage' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingRule.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingRule.Scope``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-scope
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''``AWS::BillingConductor::PricingRule.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::PricingRule.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''``AWS::BillingConductor::PricingRule.Service``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-service
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::BillingConductor::PricingRule.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-billingconductor-pricingrule.html#cfn-billingconductor-pricingrule-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPricingRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnBillingGroup",
    "CfnBillingGroupProps",
    "CfnCustomLineItem",
    "CfnCustomLineItemProps",
    "CfnPricingPlan",
    "CfnPricingPlanProps",
    "CfnPricingRule",
    "CfnPricingRuleProps",
]

publication.publish()
