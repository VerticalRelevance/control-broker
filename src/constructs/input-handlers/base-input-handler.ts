import { Construct } from 'constructs';

export abstract class BaseInputHandler extends Construct {
  /**
     * Return a name for this input handler that is safe for use in the
     * path of a URL.
     */
  public abstract get urlSafeName(): string;
}