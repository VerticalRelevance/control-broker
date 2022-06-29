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
  protected routes: HttpRoute[] = [];
  protected authorizedPrincipalArns: string[] = [];
  public readonly route: HttpRoute;
  public readonly path: string;
  public readonly method: string;

  public constructor(urlSafeName: string, api: Api, integrationTarget: IIntegrationTarget) {
    super(urlSafeName, api, integrationTarget);
    this.path = join('/', this.urlSafeName);
    this.route = api.awsApiGatewayHTTPApi.addRoutes({
      authorizer: new HttpIamAuthorizer(),
      methods: [HttpMethod.POST],
      integration: this.makeIntegrationForIntegrationTarget(),
      path: this.path,
    })[0];
    this.method = HttpMethod.POST as string;
  }

  /**
   *
   *
   * Note: JSII complains if we make the return type HTTPRouteIntegration,
   * ostensibly because of its restrictions on Generics.
   */
  protected makeIntegrationForIntegrationTarget(): any {
    if (isLambdaIntegrationTarget(this.integrationTarget)) {
      return new HttpLambdaIntegration(`${this.urlSafeName}LambdaIntegration`, this.integrationTarget.handler);
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
}
