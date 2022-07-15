import { join } from 'path';
import { HttpRoute, HttpRouteIntegration } from '@aws-cdk/aws-apigatewayv2-alpha';
import { HttpIamAuthorizer } from '@aws-cdk/aws-apigatewayv2-authorizers-alpha';
import { HttpLambdaIntegration } from '@aws-cdk/aws-apigatewayv2-integrations-alpha';
import { HttpMethod } from 'aws-cdk-lib/aws-events';
import { ArnPrincipal } from 'aws-cdk-lib/aws-iam';
import { BaseApiBinding } from '.';
import { Api } from '../api';
import { IIntegrationTarget } from '../interfaces/integration-target-interface';
import { AwsApiType } from './constants';
import { isLambdaIntegrationTarget } from './type-guards';

export interface HttpApiBindingAddToApiOptions {}

export class HttpApiBinding extends BaseApiBinding<HttpRouteIntegration> {
  public readonly apiType: AwsApiType = AwsApiType.HTTP;
  protected api?: Api;
  protected routes: HttpRoute[] = [];
  protected authorizedPrincipalArns: string[] = [];
  public route?: HttpRoute;
  public path?: string;
  public method?: string;

  public constructor(urlSafeName: string) {
    super(urlSafeName);
  }

  public bindTargetToApi(api: Api, target: IIntegrationTarget) {
    this.api = api;
    this.path = join('/', this.urlSafeName);
    this.route = api.awsApiGatewayHTTPApi.addRoutes({
      authorizer: new HttpIamAuthorizer(),
      methods: [HttpMethod.POST],
      integration: this.makeIntegrationForIntegrationTarget(target),
      path: this.path,
    })[0];
    this.method = HttpMethod.POST as string;
    if (api.awsApiGatewayHTTPApi.url === undefined) {
      throw new Error('No default stage defined for the HTTP API');
    }
    return join(api.awsApiGatewayHTTPApi.url, this.path);
  }

  /**
   * Note: JSII complains if we make the return type HTTPRouteIntegration,
   * ostensibly because of its restrictions on Generics.
   */
  protected makeIntegrationForIntegrationTarget(target: IIntegrationTarget): any {
    if (isLambdaIntegrationTarget(target)) {
      return new HttpLambdaIntegration(`${this.urlSafeName}LambdaIntegration`, target.handler);
    } else {
      throw new Error('Only Lambda integrations are supported right now');
    }
  }

  public authorizePrincipalArn(principalArn: string): void {
    this.authorizedPrincipalArns.push(principalArn);
    this.routes.forEach((r) => {
      r.grantInvoke(new ArnPrincipal(principalArn));
    });
  }

  public get url(): string | undefined {
    if (this.api?.awsApiGatewayHTTPApi.url === undefined) {
      throw new Error('Cannot get URL if the base API has no default stage');
    }
    return join(this.api?.awsApiGatewayHTTPApi.url, this.urlSafeName);
  }
}
