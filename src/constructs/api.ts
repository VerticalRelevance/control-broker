import { HttpApi } from '@aws-cdk/aws-apigatewayv2-alpha';
import { RestApi } from 'aws-cdk-lib/aws-apigateway';
import { CfnStage } from 'aws-cdk-lib/aws-apigatewayv2';
import { ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { LogGroup, RetentionDays } from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import { BaseEvalEngine } from '.';
import { BaseApiBinding } from './api-bindings';
import { BaseInputHandler } from './input-handlers';

export interface ApiProps {
  readonly apiAccessLogGroup?: LogGroup;
}

export interface InputHandlerBindingConfiguration {
  readonly inputHandler: BaseInputHandler;
  readonly binding: BaseApiBinding<any>;
}

export interface InputHandlerBindingConfigurations {
  [inputHandlerName: string]: InputHandlerBindingConfiguration;
}

export interface EvalEngineBindingConfiguration {
  readonly evalEngine: BaseEvalEngine | undefined;
  readonly binding: BaseApiBinding<any> | undefined;
};

export class Api extends Construct {
  public readonly awsApiGatewayRestApi: RestApi;
  public readonly awsApiGatewayHTTPApi: HttpApi;
  public readonly accessLogRetention: RetentionDays = RetentionDays.ONE_DAY;
  public readonly apiAccessLogGroup: LogGroup;
  protected inputHandlerBindings: InputHandlerBindingConfigurations = {};
  protected evalEngineBinding: EvalEngineBindingConfiguration = { evalEngine: undefined, binding: undefined };

  constructor(scope: Construct, public readonly id: string, props: ApiProps) {
    super(scope, id);
    if (props.apiAccessLogGroup) {
      this.apiAccessLogGroup = props.apiAccessLogGroup;
    } else {
      this.apiAccessLogGroup = new LogGroup(this, `${id}AccessLogGroup`, { retention: this.accessLogRetention });
      this.apiAccessLogGroup.grantWrite(new ServicePrincipal('apigateway.amazonaws.com'));
    }
    this.awsApiGatewayHTTPApi = new HttpApi(this, `${id}HttpApi`, { createDefaultStage: true });
    this.configureAwsApiGatewayHTTPApiLogging();
    this.awsApiGatewayRestApi = new RestApi(this, `${id}RestApi`);
  }

  protected configureAwsApiGatewayHTTPApiLogging() {
    const cfnDefaultStage = this.awsApiGatewayHTTPApi.node.defaultChild as CfnStage;
    cfnDefaultStage.addOverride('AccessLogSettings', {
      DestinationArn: this.apiAccessLogGroup.logGroupArn,
      Format: JSON.stringify({
        requestId: '$context.requestId',
        ip: '$context.identity.sourceIp',
        requestTime: '$context.requestTime',
        httpMethod: '$context.httpMethod',
        routeKey: '$context.routeKey',
        status: '$context.status',
        protocol: '$context.protocol',
        responseLength: '$context.responseLength',
        integrationErrorMessage: '$context.integrationErrorMessage',
      }),
    });
  }

  public setEvalEngine(evalEngine: BaseEvalEngine, binding: BaseApiBinding<any>) {
    this.evalEngineBinding = { evalEngine, binding };
  }

  protected get evalEngineUrl() {
    if (this.evalEngineBinding.binding === undefined) {
      throw new Error('You must add an eval engine binding before trying to get its URL');
    }
    return this.evalEngineBinding.binding.url;
  }

  public addInputHandler(inputHandler: BaseInputHandler, binding: BaseApiBinding<any>) {
    if (this.evalEngineBinding.binding === undefined) {
      throw new Error('You must add an eval engine binding before trying to add input handlers');
    }
    this.evalEngineBinding.binding.authorizePrincipalArn(inputHandler.evalEngineCallerPrincipalArn);
    this.inputHandlerBindings[inputHandler.urlSafeName] = { inputHandler, binding };
  }

  public getUrlForInputHandler(inputHandler: BaseInputHandler) {
    return this.inputHandlerBindings[inputHandler.urlSafeName].binding.url;
  }
}
