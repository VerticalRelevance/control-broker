'''
# AWS::MediaTailor Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_mediatailor as mediatailor
```

<!--BEGIN CFNONLY DISCLAIMER-->

There are no official hand-written ([L2](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) constructs for this service yet. Here are some suggestions on how to proceed:

* Search [Construct Hub for MediaTailor construct libraries](https://constructs.dev/search?q=mediatailor)
* Use the automatically generated [L1](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_l1_using) constructs, in the same way you would use [the CloudFormation AWS::MediaTailor resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_MediaTailor.html) directly.

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
class CfnPlaybackConfiguration(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration",
):
    '''A CloudFormation ``AWS::MediaTailor::PlaybackConfiguration``.

    :cloudformationResource: AWS::MediaTailor::PlaybackConfiguration
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_mediatailor as mediatailor
        
        # configuration_aliases: Any
        
        cfn_playback_configuration = mediatailor.CfnPlaybackConfiguration(self, "MyCfnPlaybackConfiguration",
            ad_decision_server_url="adDecisionServerUrl",
            name="name",
            video_content_source_url="videoContentSourceUrl",
        
            # the properties below are optional
            avail_suppression=mediatailor.CfnPlaybackConfiguration.AvailSuppressionProperty(
                mode="mode",
                value="value"
            ),
            bumper=mediatailor.CfnPlaybackConfiguration.BumperProperty(
                end_url="endUrl",
                start_url="startUrl"
            ),
            cdn_configuration=mediatailor.CfnPlaybackConfiguration.CdnConfigurationProperty(
                ad_segment_url_prefix="adSegmentUrlPrefix",
                content_segment_url_prefix="contentSegmentUrlPrefix"
            ),
            configuration_aliases={
                "configuration_aliases_key": configuration_aliases
            },
            dash_configuration=mediatailor.CfnPlaybackConfiguration.DashConfigurationForPutProperty(
                mpd_location="mpdLocation",
                origin_manifest_type="originManifestType"
            ),
            live_pre_roll_configuration=mediatailor.CfnPlaybackConfiguration.LivePreRollConfigurationProperty(
                ad_decision_server_url="adDecisionServerUrl",
                max_duration_seconds=123
            ),
            manifest_processing_rules=mediatailor.CfnPlaybackConfiguration.ManifestProcessingRulesProperty(
                ad_marker_passthrough=mediatailor.CfnPlaybackConfiguration.AdMarkerPassthroughProperty(
                    enabled=False
                )
            ),
            personalization_threshold_seconds=123,
            session_initialization_endpoint_prefix="sessionInitializationEndpointPrefix",
            slate_ad_url="slateAdUrl",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            transcode_profile_name="transcodeProfileName"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ad_decision_server_url: builtins.str,
        name: builtins.str,
        video_content_source_url: builtins.str,
        avail_suppression: typing.Optional[typing.Union["CfnPlaybackConfiguration.AvailSuppressionProperty", _IResolvable_da3f097b]] = None,
        bumper: typing.Optional[typing.Union["CfnPlaybackConfiguration.BumperProperty", _IResolvable_da3f097b]] = None,
        cdn_configuration: typing.Optional[typing.Union["CfnPlaybackConfiguration.CdnConfigurationProperty", _IResolvable_da3f097b]] = None,
        configuration_aliases: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Any]]] = None,
        dash_configuration: typing.Optional[typing.Union["CfnPlaybackConfiguration.DashConfigurationForPutProperty", _IResolvable_da3f097b]] = None,
        live_pre_roll_configuration: typing.Optional[typing.Union["CfnPlaybackConfiguration.LivePreRollConfigurationProperty", _IResolvable_da3f097b]] = None,
        manifest_processing_rules: typing.Optional[typing.Union["CfnPlaybackConfiguration.ManifestProcessingRulesProperty", _IResolvable_da3f097b]] = None,
        personalization_threshold_seconds: typing.Optional[jsii.Number] = None,
        session_initialization_endpoint_prefix: typing.Optional[builtins.str] = None,
        slate_ad_url: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        transcode_profile_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::MediaTailor::PlaybackConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param ad_decision_server_url: ``AWS::MediaTailor::PlaybackConfiguration.AdDecisionServerUrl``.
        :param name: ``AWS::MediaTailor::PlaybackConfiguration.Name``.
        :param video_content_source_url: ``AWS::MediaTailor::PlaybackConfiguration.VideoContentSourceUrl``.
        :param avail_suppression: ``AWS::MediaTailor::PlaybackConfiguration.AvailSuppression``.
        :param bumper: ``AWS::MediaTailor::PlaybackConfiguration.Bumper``.
        :param cdn_configuration: ``AWS::MediaTailor::PlaybackConfiguration.CdnConfiguration``.
        :param configuration_aliases: ``AWS::MediaTailor::PlaybackConfiguration.ConfigurationAliases``.
        :param dash_configuration: ``AWS::MediaTailor::PlaybackConfiguration.DashConfiguration``.
        :param live_pre_roll_configuration: ``AWS::MediaTailor::PlaybackConfiguration.LivePreRollConfiguration``.
        :param manifest_processing_rules: ``AWS::MediaTailor::PlaybackConfiguration.ManifestProcessingRules``.
        :param personalization_threshold_seconds: ``AWS::MediaTailor::PlaybackConfiguration.PersonalizationThresholdSeconds``.
        :param session_initialization_endpoint_prefix: ``AWS::MediaTailor::PlaybackConfiguration.SessionInitializationEndpointPrefix``.
        :param slate_ad_url: ``AWS::MediaTailor::PlaybackConfiguration.SlateAdUrl``.
        :param tags: ``AWS::MediaTailor::PlaybackConfiguration.Tags``.
        :param transcode_profile_name: ``AWS::MediaTailor::PlaybackConfiguration.TranscodeProfileName``.
        '''
        props = CfnPlaybackConfigurationProps(
            ad_decision_server_url=ad_decision_server_url,
            name=name,
            video_content_source_url=video_content_source_url,
            avail_suppression=avail_suppression,
            bumper=bumper,
            cdn_configuration=cdn_configuration,
            configuration_aliases=configuration_aliases,
            dash_configuration=dash_configuration,
            live_pre_roll_configuration=live_pre_roll_configuration,
            manifest_processing_rules=manifest_processing_rules,
            personalization_threshold_seconds=personalization_threshold_seconds,
            session_initialization_endpoint_prefix=session_initialization_endpoint_prefix,
            slate_ad_url=slate_ad_url,
            tags=tags,
            transcode_profile_name=transcode_profile_name,
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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::MediaTailor::PlaybackConfiguration.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adDecisionServerUrl")
    def ad_decision_server_url(self) -> builtins.str:
        '''``AWS::MediaTailor::PlaybackConfiguration.AdDecisionServerUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-addecisionserverurl
        '''
        return typing.cast(builtins.str, jsii.get(self, "adDecisionServerUrl"))

    @ad_decision_server_url.setter
    def ad_decision_server_url(self, value: builtins.str) -> None:
        jsii.set(self, "adDecisionServerUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::MediaTailor::PlaybackConfiguration.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="videoContentSourceUrl")
    def video_content_source_url(self) -> builtins.str:
        '''``AWS::MediaTailor::PlaybackConfiguration.VideoContentSourceUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-videocontentsourceurl
        '''
        return typing.cast(builtins.str, jsii.get(self, "videoContentSourceUrl"))

    @video_content_source_url.setter
    def video_content_source_url(self, value: builtins.str) -> None:
        jsii.set(self, "videoContentSourceUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availSuppression")
    def avail_suppression(
        self,
    ) -> typing.Optional[typing.Union["CfnPlaybackConfiguration.AvailSuppressionProperty", _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.AvailSuppression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-availsuppression
        '''
        return typing.cast(typing.Optional[typing.Union["CfnPlaybackConfiguration.AvailSuppressionProperty", _IResolvable_da3f097b]], jsii.get(self, "availSuppression"))

    @avail_suppression.setter
    def avail_suppression(
        self,
        value: typing.Optional[typing.Union["CfnPlaybackConfiguration.AvailSuppressionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "availSuppression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bumper")
    def bumper(
        self,
    ) -> typing.Optional[typing.Union["CfnPlaybackConfiguration.BumperProperty", _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.Bumper``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-bumper
        '''
        return typing.cast(typing.Optional[typing.Union["CfnPlaybackConfiguration.BumperProperty", _IResolvable_da3f097b]], jsii.get(self, "bumper"))

    @bumper.setter
    def bumper(
        self,
        value: typing.Optional[typing.Union["CfnPlaybackConfiguration.BumperProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "bumper", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdnConfiguration")
    def cdn_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnPlaybackConfiguration.CdnConfigurationProperty", _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.CdnConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-cdnconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnPlaybackConfiguration.CdnConfigurationProperty", _IResolvable_da3f097b]], jsii.get(self, "cdnConfiguration"))

    @cdn_configuration.setter
    def cdn_configuration(
        self,
        value: typing.Optional[typing.Union["CfnPlaybackConfiguration.CdnConfigurationProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "cdnConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationAliases")
    def configuration_aliases(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Any]]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.ConfigurationAliases``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-configurationaliases
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Any]]], jsii.get(self, "configurationAliases"))

    @configuration_aliases.setter
    def configuration_aliases(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Any]]],
    ) -> None:
        jsii.set(self, "configurationAliases", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dashConfiguration")
    def dash_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnPlaybackConfiguration.DashConfigurationForPutProperty", _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.DashConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-dashconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnPlaybackConfiguration.DashConfigurationForPutProperty", _IResolvable_da3f097b]], jsii.get(self, "dashConfiguration"))

    @dash_configuration.setter
    def dash_configuration(
        self,
        value: typing.Optional[typing.Union["CfnPlaybackConfiguration.DashConfigurationForPutProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "dashConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="livePreRollConfiguration")
    def live_pre_roll_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnPlaybackConfiguration.LivePreRollConfigurationProperty", _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.LivePreRollConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-liveprerollconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnPlaybackConfiguration.LivePreRollConfigurationProperty", _IResolvable_da3f097b]], jsii.get(self, "livePreRollConfiguration"))

    @live_pre_roll_configuration.setter
    def live_pre_roll_configuration(
        self,
        value: typing.Optional[typing.Union["CfnPlaybackConfiguration.LivePreRollConfigurationProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "livePreRollConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifestProcessingRules")
    def manifest_processing_rules(
        self,
    ) -> typing.Optional[typing.Union["CfnPlaybackConfiguration.ManifestProcessingRulesProperty", _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.ManifestProcessingRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-manifestprocessingrules
        '''
        return typing.cast(typing.Optional[typing.Union["CfnPlaybackConfiguration.ManifestProcessingRulesProperty", _IResolvable_da3f097b]], jsii.get(self, "manifestProcessingRules"))

    @manifest_processing_rules.setter
    def manifest_processing_rules(
        self,
        value: typing.Optional[typing.Union["CfnPlaybackConfiguration.ManifestProcessingRulesProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "manifestProcessingRules", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="personalizationThresholdSeconds")
    def personalization_threshold_seconds(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MediaTailor::PlaybackConfiguration.PersonalizationThresholdSeconds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-personalizationthresholdseconds
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "personalizationThresholdSeconds"))

    @personalization_threshold_seconds.setter
    def personalization_threshold_seconds(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        jsii.set(self, "personalizationThresholdSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionInitializationEndpointPrefix")
    def session_initialization_endpoint_prefix(self) -> typing.Optional[builtins.str]:
        '''``AWS::MediaTailor::PlaybackConfiguration.SessionInitializationEndpointPrefix``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-sessioninitializationendpointprefix
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionInitializationEndpointPrefix"))

    @session_initialization_endpoint_prefix.setter
    def session_initialization_endpoint_prefix(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "sessionInitializationEndpointPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slateAdUrl")
    def slate_ad_url(self) -> typing.Optional[builtins.str]:
        '''``AWS::MediaTailor::PlaybackConfiguration.SlateAdUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-slateadurl
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "slateAdUrl"))

    @slate_ad_url.setter
    def slate_ad_url(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "slateAdUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transcodeProfileName")
    def transcode_profile_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MediaTailor::PlaybackConfiguration.TranscodeProfileName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-transcodeprofilename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "transcodeProfileName"))

    @transcode_profile_name.setter
    def transcode_profile_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "transcodeProfileName", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration.AdMarkerPassthroughProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled"},
    )
    class AdMarkerPassthroughProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param enabled: ``CfnPlaybackConfiguration.AdMarkerPassthroughProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-admarkerpassthrough.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_mediatailor as mediatailor
                
                ad_marker_passthrough_property = mediatailor.CfnPlaybackConfiguration.AdMarkerPassthroughProperty(
                    enabled=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnPlaybackConfiguration.AdMarkerPassthroughProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-admarkerpassthrough.html#cfn-mediatailor-playbackconfiguration-admarkerpassthrough-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AdMarkerPassthroughProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration.AvailSuppressionProperty",
        jsii_struct_bases=[],
        name_mapping={"mode": "mode", "value": "value"},
    )
    class AvailSuppressionProperty:
        def __init__(
            self,
            *,
            mode: typing.Optional[builtins.str] = None,
            value: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param mode: ``CfnPlaybackConfiguration.AvailSuppressionProperty.Mode``.
            :param value: ``CfnPlaybackConfiguration.AvailSuppressionProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-availsuppression.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_mediatailor as mediatailor
                
                avail_suppression_property = mediatailor.CfnPlaybackConfiguration.AvailSuppressionProperty(
                    mode="mode",
                    value="value"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if mode is not None:
                self._values["mode"] = mode
            if value is not None:
                self._values["value"] = value

        @builtins.property
        def mode(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.AvailSuppressionProperty.Mode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-availsuppression.html#cfn-mediatailor-playbackconfiguration-availsuppression-mode
            '''
            result = self._values.get("mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def value(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.AvailSuppressionProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-availsuppression.html#cfn-mediatailor-playbackconfiguration-availsuppression-value
            '''
            result = self._values.get("value")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AvailSuppressionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration.BumperProperty",
        jsii_struct_bases=[],
        name_mapping={"end_url": "endUrl", "start_url": "startUrl"},
    )
    class BumperProperty:
        def __init__(
            self,
            *,
            end_url: typing.Optional[builtins.str] = None,
            start_url: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param end_url: ``CfnPlaybackConfiguration.BumperProperty.EndUrl``.
            :param start_url: ``CfnPlaybackConfiguration.BumperProperty.StartUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-bumper.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_mediatailor as mediatailor
                
                bumper_property = mediatailor.CfnPlaybackConfiguration.BumperProperty(
                    end_url="endUrl",
                    start_url="startUrl"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if end_url is not None:
                self._values["end_url"] = end_url
            if start_url is not None:
                self._values["start_url"] = start_url

        @builtins.property
        def end_url(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.BumperProperty.EndUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-bumper.html#cfn-mediatailor-playbackconfiguration-bumper-endurl
            '''
            result = self._values.get("end_url")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def start_url(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.BumperProperty.StartUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-bumper.html#cfn-mediatailor-playbackconfiguration-bumper-starturl
            '''
            result = self._values.get("start_url")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BumperProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration.CdnConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "ad_segment_url_prefix": "adSegmentUrlPrefix",
            "content_segment_url_prefix": "contentSegmentUrlPrefix",
        },
    )
    class CdnConfigurationProperty:
        def __init__(
            self,
            *,
            ad_segment_url_prefix: typing.Optional[builtins.str] = None,
            content_segment_url_prefix: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param ad_segment_url_prefix: ``CfnPlaybackConfiguration.CdnConfigurationProperty.AdSegmentUrlPrefix``.
            :param content_segment_url_prefix: ``CfnPlaybackConfiguration.CdnConfigurationProperty.ContentSegmentUrlPrefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-cdnconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_mediatailor as mediatailor
                
                cdn_configuration_property = mediatailor.CfnPlaybackConfiguration.CdnConfigurationProperty(
                    ad_segment_url_prefix="adSegmentUrlPrefix",
                    content_segment_url_prefix="contentSegmentUrlPrefix"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if ad_segment_url_prefix is not None:
                self._values["ad_segment_url_prefix"] = ad_segment_url_prefix
            if content_segment_url_prefix is not None:
                self._values["content_segment_url_prefix"] = content_segment_url_prefix

        @builtins.property
        def ad_segment_url_prefix(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.CdnConfigurationProperty.AdSegmentUrlPrefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-cdnconfiguration.html#cfn-mediatailor-playbackconfiguration-cdnconfiguration-adsegmenturlprefix
            '''
            result = self._values.get("ad_segment_url_prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def content_segment_url_prefix(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.CdnConfigurationProperty.ContentSegmentUrlPrefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-cdnconfiguration.html#cfn-mediatailor-playbackconfiguration-cdnconfiguration-contentsegmenturlprefix
            '''
            result = self._values.get("content_segment_url_prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CdnConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration.DashConfigurationForPutProperty",
        jsii_struct_bases=[],
        name_mapping={
            "mpd_location": "mpdLocation",
            "origin_manifest_type": "originManifestType",
        },
    )
    class DashConfigurationForPutProperty:
        def __init__(
            self,
            *,
            mpd_location: typing.Optional[builtins.str] = None,
            origin_manifest_type: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param mpd_location: ``CfnPlaybackConfiguration.DashConfigurationForPutProperty.MpdLocation``.
            :param origin_manifest_type: ``CfnPlaybackConfiguration.DashConfigurationForPutProperty.OriginManifestType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-dashconfigurationforput.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_mediatailor as mediatailor
                
                dash_configuration_for_put_property = mediatailor.CfnPlaybackConfiguration.DashConfigurationForPutProperty(
                    mpd_location="mpdLocation",
                    origin_manifest_type="originManifestType"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if mpd_location is not None:
                self._values["mpd_location"] = mpd_location
            if origin_manifest_type is not None:
                self._values["origin_manifest_type"] = origin_manifest_type

        @builtins.property
        def mpd_location(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.DashConfigurationForPutProperty.MpdLocation``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-dashconfigurationforput.html#cfn-mediatailor-playbackconfiguration-dashconfigurationforput-mpdlocation
            '''
            result = self._values.get("mpd_location")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def origin_manifest_type(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.DashConfigurationForPutProperty.OriginManifestType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-dashconfigurationforput.html#cfn-mediatailor-playbackconfiguration-dashconfigurationforput-originmanifesttype
            '''
            result = self._values.get("origin_manifest_type")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DashConfigurationForPutProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration.LivePreRollConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "ad_decision_server_url": "adDecisionServerUrl",
            "max_duration_seconds": "maxDurationSeconds",
        },
    )
    class LivePreRollConfigurationProperty:
        def __init__(
            self,
            *,
            ad_decision_server_url: typing.Optional[builtins.str] = None,
            max_duration_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param ad_decision_server_url: ``CfnPlaybackConfiguration.LivePreRollConfigurationProperty.AdDecisionServerUrl``.
            :param max_duration_seconds: ``CfnPlaybackConfiguration.LivePreRollConfigurationProperty.MaxDurationSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-liveprerollconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_mediatailor as mediatailor
                
                live_pre_roll_configuration_property = mediatailor.CfnPlaybackConfiguration.LivePreRollConfigurationProperty(
                    ad_decision_server_url="adDecisionServerUrl",
                    max_duration_seconds=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if ad_decision_server_url is not None:
                self._values["ad_decision_server_url"] = ad_decision_server_url
            if max_duration_seconds is not None:
                self._values["max_duration_seconds"] = max_duration_seconds

        @builtins.property
        def ad_decision_server_url(self) -> typing.Optional[builtins.str]:
            '''``CfnPlaybackConfiguration.LivePreRollConfigurationProperty.AdDecisionServerUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-liveprerollconfiguration.html#cfn-mediatailor-playbackconfiguration-liveprerollconfiguration-addecisionserverurl
            '''
            result = self._values.get("ad_decision_server_url")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def max_duration_seconds(self) -> typing.Optional[jsii.Number]:
            '''``CfnPlaybackConfiguration.LivePreRollConfigurationProperty.MaxDurationSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-liveprerollconfiguration.html#cfn-mediatailor-playbackconfiguration-liveprerollconfiguration-maxdurationseconds
            '''
            result = self._values.get("max_duration_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LivePreRollConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfiguration.ManifestProcessingRulesProperty",
        jsii_struct_bases=[],
        name_mapping={"ad_marker_passthrough": "adMarkerPassthrough"},
    )
    class ManifestProcessingRulesProperty:
        def __init__(
            self,
            *,
            ad_marker_passthrough: typing.Optional[typing.Union["CfnPlaybackConfiguration.AdMarkerPassthroughProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param ad_marker_passthrough: ``CfnPlaybackConfiguration.ManifestProcessingRulesProperty.AdMarkerPassthrough``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-manifestprocessingrules.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_mediatailor as mediatailor
                
                manifest_processing_rules_property = mediatailor.CfnPlaybackConfiguration.ManifestProcessingRulesProperty(
                    ad_marker_passthrough=mediatailor.CfnPlaybackConfiguration.AdMarkerPassthroughProperty(
                        enabled=False
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if ad_marker_passthrough is not None:
                self._values["ad_marker_passthrough"] = ad_marker_passthrough

        @builtins.property
        def ad_marker_passthrough(
            self,
        ) -> typing.Optional[typing.Union["CfnPlaybackConfiguration.AdMarkerPassthroughProperty", _IResolvable_da3f097b]]:
            '''``CfnPlaybackConfiguration.ManifestProcessingRulesProperty.AdMarkerPassthrough``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-mediatailor-playbackconfiguration-manifestprocessingrules.html#cfn-mediatailor-playbackconfiguration-manifestprocessingrules-admarkerpassthrough
            '''
            result = self._values.get("ad_marker_passthrough")
            return typing.cast(typing.Optional[typing.Union["CfnPlaybackConfiguration.AdMarkerPassthroughProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ManifestProcessingRulesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_mediatailor.CfnPlaybackConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "ad_decision_server_url": "adDecisionServerUrl",
        "name": "name",
        "video_content_source_url": "videoContentSourceUrl",
        "avail_suppression": "availSuppression",
        "bumper": "bumper",
        "cdn_configuration": "cdnConfiguration",
        "configuration_aliases": "configurationAliases",
        "dash_configuration": "dashConfiguration",
        "live_pre_roll_configuration": "livePreRollConfiguration",
        "manifest_processing_rules": "manifestProcessingRules",
        "personalization_threshold_seconds": "personalizationThresholdSeconds",
        "session_initialization_endpoint_prefix": "sessionInitializationEndpointPrefix",
        "slate_ad_url": "slateAdUrl",
        "tags": "tags",
        "transcode_profile_name": "transcodeProfileName",
    },
)
class CfnPlaybackConfigurationProps:
    def __init__(
        self,
        *,
        ad_decision_server_url: builtins.str,
        name: builtins.str,
        video_content_source_url: builtins.str,
        avail_suppression: typing.Optional[typing.Union[CfnPlaybackConfiguration.AvailSuppressionProperty, _IResolvable_da3f097b]] = None,
        bumper: typing.Optional[typing.Union[CfnPlaybackConfiguration.BumperProperty, _IResolvable_da3f097b]] = None,
        cdn_configuration: typing.Optional[typing.Union[CfnPlaybackConfiguration.CdnConfigurationProperty, _IResolvable_da3f097b]] = None,
        configuration_aliases: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Any]]] = None,
        dash_configuration: typing.Optional[typing.Union[CfnPlaybackConfiguration.DashConfigurationForPutProperty, _IResolvable_da3f097b]] = None,
        live_pre_roll_configuration: typing.Optional[typing.Union[CfnPlaybackConfiguration.LivePreRollConfigurationProperty, _IResolvable_da3f097b]] = None,
        manifest_processing_rules: typing.Optional[typing.Union[CfnPlaybackConfiguration.ManifestProcessingRulesProperty, _IResolvable_da3f097b]] = None,
        personalization_threshold_seconds: typing.Optional[jsii.Number] = None,
        session_initialization_endpoint_prefix: typing.Optional[builtins.str] = None,
        slate_ad_url: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        transcode_profile_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnPlaybackConfiguration``.

        :param ad_decision_server_url: ``AWS::MediaTailor::PlaybackConfiguration.AdDecisionServerUrl``.
        :param name: ``AWS::MediaTailor::PlaybackConfiguration.Name``.
        :param video_content_source_url: ``AWS::MediaTailor::PlaybackConfiguration.VideoContentSourceUrl``.
        :param avail_suppression: ``AWS::MediaTailor::PlaybackConfiguration.AvailSuppression``.
        :param bumper: ``AWS::MediaTailor::PlaybackConfiguration.Bumper``.
        :param cdn_configuration: ``AWS::MediaTailor::PlaybackConfiguration.CdnConfiguration``.
        :param configuration_aliases: ``AWS::MediaTailor::PlaybackConfiguration.ConfigurationAliases``.
        :param dash_configuration: ``AWS::MediaTailor::PlaybackConfiguration.DashConfiguration``.
        :param live_pre_roll_configuration: ``AWS::MediaTailor::PlaybackConfiguration.LivePreRollConfiguration``.
        :param manifest_processing_rules: ``AWS::MediaTailor::PlaybackConfiguration.ManifestProcessingRules``.
        :param personalization_threshold_seconds: ``AWS::MediaTailor::PlaybackConfiguration.PersonalizationThresholdSeconds``.
        :param session_initialization_endpoint_prefix: ``AWS::MediaTailor::PlaybackConfiguration.SessionInitializationEndpointPrefix``.
        :param slate_ad_url: ``AWS::MediaTailor::PlaybackConfiguration.SlateAdUrl``.
        :param tags: ``AWS::MediaTailor::PlaybackConfiguration.Tags``.
        :param transcode_profile_name: ``AWS::MediaTailor::PlaybackConfiguration.TranscodeProfileName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_mediatailor as mediatailor
            
            # configuration_aliases: Any
            
            cfn_playback_configuration_props = mediatailor.CfnPlaybackConfigurationProps(
                ad_decision_server_url="adDecisionServerUrl",
                name="name",
                video_content_source_url="videoContentSourceUrl",
            
                # the properties below are optional
                avail_suppression=mediatailor.CfnPlaybackConfiguration.AvailSuppressionProperty(
                    mode="mode",
                    value="value"
                ),
                bumper=mediatailor.CfnPlaybackConfiguration.BumperProperty(
                    end_url="endUrl",
                    start_url="startUrl"
                ),
                cdn_configuration=mediatailor.CfnPlaybackConfiguration.CdnConfigurationProperty(
                    ad_segment_url_prefix="adSegmentUrlPrefix",
                    content_segment_url_prefix="contentSegmentUrlPrefix"
                ),
                configuration_aliases={
                    "configuration_aliases_key": configuration_aliases
                },
                dash_configuration=mediatailor.CfnPlaybackConfiguration.DashConfigurationForPutProperty(
                    mpd_location="mpdLocation",
                    origin_manifest_type="originManifestType"
                ),
                live_pre_roll_configuration=mediatailor.CfnPlaybackConfiguration.LivePreRollConfigurationProperty(
                    ad_decision_server_url="adDecisionServerUrl",
                    max_duration_seconds=123
                ),
                manifest_processing_rules=mediatailor.CfnPlaybackConfiguration.ManifestProcessingRulesProperty(
                    ad_marker_passthrough=mediatailor.CfnPlaybackConfiguration.AdMarkerPassthroughProperty(
                        enabled=False
                    )
                ),
                personalization_threshold_seconds=123,
                session_initialization_endpoint_prefix="sessionInitializationEndpointPrefix",
                slate_ad_url="slateAdUrl",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                transcode_profile_name="transcodeProfileName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ad_decision_server_url": ad_decision_server_url,
            "name": name,
            "video_content_source_url": video_content_source_url,
        }
        if avail_suppression is not None:
            self._values["avail_suppression"] = avail_suppression
        if bumper is not None:
            self._values["bumper"] = bumper
        if cdn_configuration is not None:
            self._values["cdn_configuration"] = cdn_configuration
        if configuration_aliases is not None:
            self._values["configuration_aliases"] = configuration_aliases
        if dash_configuration is not None:
            self._values["dash_configuration"] = dash_configuration
        if live_pre_roll_configuration is not None:
            self._values["live_pre_roll_configuration"] = live_pre_roll_configuration
        if manifest_processing_rules is not None:
            self._values["manifest_processing_rules"] = manifest_processing_rules
        if personalization_threshold_seconds is not None:
            self._values["personalization_threshold_seconds"] = personalization_threshold_seconds
        if session_initialization_endpoint_prefix is not None:
            self._values["session_initialization_endpoint_prefix"] = session_initialization_endpoint_prefix
        if slate_ad_url is not None:
            self._values["slate_ad_url"] = slate_ad_url
        if tags is not None:
            self._values["tags"] = tags
        if transcode_profile_name is not None:
            self._values["transcode_profile_name"] = transcode_profile_name

    @builtins.property
    def ad_decision_server_url(self) -> builtins.str:
        '''``AWS::MediaTailor::PlaybackConfiguration.AdDecisionServerUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-addecisionserverurl
        '''
        result = self._values.get("ad_decision_server_url")
        assert result is not None, "Required property 'ad_decision_server_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::MediaTailor::PlaybackConfiguration.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def video_content_source_url(self) -> builtins.str:
        '''``AWS::MediaTailor::PlaybackConfiguration.VideoContentSourceUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-videocontentsourceurl
        '''
        result = self._values.get("video_content_source_url")
        assert result is not None, "Required property 'video_content_source_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def avail_suppression(
        self,
    ) -> typing.Optional[typing.Union[CfnPlaybackConfiguration.AvailSuppressionProperty, _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.AvailSuppression``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-availsuppression
        '''
        result = self._values.get("avail_suppression")
        return typing.cast(typing.Optional[typing.Union[CfnPlaybackConfiguration.AvailSuppressionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def bumper(
        self,
    ) -> typing.Optional[typing.Union[CfnPlaybackConfiguration.BumperProperty, _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.Bumper``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-bumper
        '''
        result = self._values.get("bumper")
        return typing.cast(typing.Optional[typing.Union[CfnPlaybackConfiguration.BumperProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def cdn_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnPlaybackConfiguration.CdnConfigurationProperty, _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.CdnConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-cdnconfiguration
        '''
        result = self._values.get("cdn_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnPlaybackConfiguration.CdnConfigurationProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def configuration_aliases(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Any]]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.ConfigurationAliases``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-configurationaliases
        '''
        result = self._values.get("configuration_aliases")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Any]]], result)

    @builtins.property
    def dash_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnPlaybackConfiguration.DashConfigurationForPutProperty, _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.DashConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-dashconfiguration
        '''
        result = self._values.get("dash_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnPlaybackConfiguration.DashConfigurationForPutProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def live_pre_roll_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnPlaybackConfiguration.LivePreRollConfigurationProperty, _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.LivePreRollConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-liveprerollconfiguration
        '''
        result = self._values.get("live_pre_roll_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnPlaybackConfiguration.LivePreRollConfigurationProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def manifest_processing_rules(
        self,
    ) -> typing.Optional[typing.Union[CfnPlaybackConfiguration.ManifestProcessingRulesProperty, _IResolvable_da3f097b]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.ManifestProcessingRules``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-manifestprocessingrules
        '''
        result = self._values.get("manifest_processing_rules")
        return typing.cast(typing.Optional[typing.Union[CfnPlaybackConfiguration.ManifestProcessingRulesProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def personalization_threshold_seconds(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MediaTailor::PlaybackConfiguration.PersonalizationThresholdSeconds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-personalizationthresholdseconds
        '''
        result = self._values.get("personalization_threshold_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def session_initialization_endpoint_prefix(self) -> typing.Optional[builtins.str]:
        '''``AWS::MediaTailor::PlaybackConfiguration.SessionInitializationEndpointPrefix``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-sessioninitializationendpointprefix
        '''
        result = self._values.get("session_initialization_endpoint_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def slate_ad_url(self) -> typing.Optional[builtins.str]:
        '''``AWS::MediaTailor::PlaybackConfiguration.SlateAdUrl``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-slateadurl
        '''
        result = self._values.get("slate_ad_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::MediaTailor::PlaybackConfiguration.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def transcode_profile_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MediaTailor::PlaybackConfiguration.TranscodeProfileName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-mediatailor-playbackconfiguration.html#cfn-mediatailor-playbackconfiguration-transcodeprofilename
        '''
        result = self._values.get("transcode_profile_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPlaybackConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnPlaybackConfiguration",
    "CfnPlaybackConfigurationProps",
]

publication.publish()
