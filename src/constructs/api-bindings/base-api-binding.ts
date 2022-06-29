import { join } from 'path';
import { AwsApiType } from '.';
import { Api } from '../api';
import { IIntegrationTarget } from '../interfaces/integration-target-interface';

export interface BaseApiBindingProps<IntegrationType> {
  readonly integration: IntegrationType;
}

/**
 * Base class for an API Binding, which attaches an integration to an API and
 * authorizes principals to invoke the integration via the API attachment.
 *
 * Defined abstractly since there are different types of APIs to attach integrations with
 * and different principals to allow.
 */
export abstract class BaseApiBinding<IntegrationType> {
  public abstract readonly apiType: AwsApiType;
  public abstract readonly method: string;
  public abstract readonly path: string;

  /**
   *
   * This should create an invocable URL with the given integration.
   *
   * @param urlSafeName A name suitable for use in an integration's URL. Can contain slashes.
   * @param api The API to bind to.
   * @param integrationTarget The integration target to bind to the API via an integration.
   */
  public constructor(public readonly urlSafeName: string, public readonly api: Api, public readonly integrationTarget: IIntegrationTarget) {
    this.makeIntegrationForIntegrationTarget();
  }

  /**
   * Give permission to a principal to call this API using this binding.
   *
   * This should be called after the binding has been added to all APIs.
   *
   * @param principalArn Principal to give calling permissions to.
   */
  public abstract authorizePrincipalArn(principalArn: string): void;

  public get url() {
    if (this.apiType === AwsApiType.HTTP) {
      if (this.api.awsApiGatewayHTTPApi.url === undefined) {
        throw new Error('No default stage defined for the HTTP API');
      }
      return join(this.api.awsApiGatewayHTTPApi.url, this.path);
    } else if (this.apiType === AwsApiType.REST) {
      return this.api.awsApiGatewayRestApi.urlForPath(this.path);
    } else {
      throw new Error(`API type ${this.apiType} is not yet supported`);
    }
  }

  /***
   * Return an integration built for the integration target.
   */
  protected abstract makeIntegrationForIntegrationTarget(): IntegrationType;
}
