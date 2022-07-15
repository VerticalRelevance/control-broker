import { AwsApiType } from '.';
import { Api } from '../api';
import { IIntegrationTarget } from '../interfaces/integration-target-interface';

export interface BaseApiBindingProps<IntegrationType> {
  readonly integration: IntegrationType;
}

export interface ApiBindingHeaders {
  [headerName: string]: string;
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
  public method?: string;
  public path?: string;
  protected headers: ApiBindingHeaders = {};

  /**
   * @param urlSafeName A name suitable for use in an integration's URL. Can contain slashes.
   */
  public constructor(public readonly urlSafeName: string) {}

  /**
   * Give permission to a principal to call this API using this binding.
   *
   * This should be called after the binding has been added to all APIs.
   *
   * @param principalArn Principal to give calling permissions to.
   */
  public abstract authorizePrincipalArn(principalArn: string): void;

  /**
   *
   * @param headers Headers to send to the integration.
   */
  public addHeaders(headers: ApiBindingHeaders): void {
    this.headers = {
      ...this.headers,
      ...headers,
    };
  }

  /***
   * Return an integration built for the integration target.
   */
  protected abstract makeIntegrationForIntegrationTarget(target: IIntegrationTarget): IntegrationType;

  /**
   * Bind this target to the API.
   *
   * @return url
   */
  public abstract bindTargetToApi(api: Api, target: IIntegrationTarget): string;

  public abstract get url(): string | undefined;
}
