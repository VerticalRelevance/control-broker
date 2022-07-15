import { HttpApi } from '@aws-cdk/aws-apigatewayv2-alpha';
import { CfnOutput } from 'aws-cdk-lib';
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
}

export class Api extends Construct {
  public readonly accessLogRetention: RetentionDays = RetentionDays.ONE_DAY;
  public readonly apiAccessLogGroup: LogGroup;

  protected inputHandlers: BaseInputHandler[] = [];
  /**
   * @internal
   */
  protected _evalEngine?: BaseEvalEngine = undefined;
  /**
   * @internal
   */
  protected _awsApiGatewayHttpApi?: HttpApi;
  /**
   * @internal
   */
  protected _awsApiGatewayRestApi?: RestApi;

  constructor(scope: Construct, public readonly id: string, props: ApiProps) {
    super(scope, id);
    if (props.apiAccessLogGroup) {
      this.apiAccessLogGroup = props.apiAccessLogGroup;
    } else {
      this.apiAccessLogGroup = new LogGroup(this, `${id}AccessLogGroup`, { retention: this.accessLogRetention });
      this.apiAccessLogGroup.grantWrite(new ServicePrincipal('apigateway.amazonaws.com'));
    }
    this.configureAwsApiGatewayHTTPApiLogging();
  }

  /**
   * Lazily create the HTTP API when it is first accessed.
   */
  public get awsApiGatewayHTTPApi() {
    if (this._awsApiGatewayHttpApi === undefined) {
      this._awsApiGatewayHttpApi = new HttpApi(this, `${this.id}HttpApi`, { createDefaultStage: true });
    }
    return this._awsApiGatewayHttpApi;
  }

  /**
   * Lazily create the Rest API when it is first accessed.
   */
  public get awsApiGatewayRestApi() {
    if (this._awsApiGatewayRestApi === undefined) {
      this._awsApiGatewayRestApi = new RestApi(this, `${this.id}RestApi`);
    }
    return this._awsApiGatewayRestApi;
  }

  protected configureAwsApiGatewayHTTPApiLogging() {
    const cfnDefaultStage = this.awsApiGatewayHTTPApi.defaultStage!.node.defaultChild as CfnStage;
    cfnDefaultStage.addPropertyOverride('AccessLogSettings', {
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

  public set evalEngine(evalEngine: BaseEvalEngine | undefined) {
    this._evalEngine = evalEngine;
  }

  public get evalEngine() {
    return this._evalEngine;
  }

  public addInputHandler(inputHandler: BaseInputHandler) {
    if (this.evalEngine === undefined) {
      throw new Error('You must add an eval engine before trying to add input handlers');
    }
    inputHandler.bindToApi(this);
    this.evalEngine.authorizePrincipalArn(inputHandler.evalEngineCallerPrincipalArn);
    this.inputHandlers.push(inputHandler);
    if (inputHandler.url === undefined) {
      throw new Error("Input handler's URL was undefined even after binding to the API");
    }
    new CfnOutput(this, `${inputHandler.urlSafeName}HandlerURL`, { value: inputHandler.url });
  }

  public getUrlForInputHandler(inputHandler: BaseInputHandler) {
    const currentInputHandler = this.inputHandlers.find((ih) => ih === inputHandler);
    return currentInputHandler?.url;
  }
}
