import { HttpApi } from '@aws-cdk/aws-apigatewayv2-alpha';
import { RestApi } from 'aws-cdk-lib/aws-apigateway';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import { EvalEngine } from '.';

export interface ApiProps {
  readonly evalEngine: EvalEngine;
  readonly accessLogRetention?: RetentionDays;
}
export class Api extends Construct {
  public readonly awsApiGatewayRestApi: RestApi;
  public readonly awsApiGatewayHTTPApi: HttpApi;
  public readonly accessLogRetention: RetentionDays = RetentionDays.ONE_DAY;

  constructor(scope: Construct, id: string, props: ApiProps) {
    super(scope, id);
    if (props.accessLogRetention) {
      this.accessLogRetention = props.accessLogRetention;
    }
    this.awsApiGatewayHTTPApi = new HttpApi(this, `${id}HttpApi`, { createDefaultStage: true });
    this.awsApiGatewayRestApi = new RestApi(this, `${id}RestApi`);
  }

  public get externalBaseUrl(): string {
    if (this.awsApiGatewayHTTPApi.url === undefined) {
      throw new Error('No external URL has been configured for the Control Broker API');
    }
    return this.awsApiGatewayHTTPApi.url;
  }

}