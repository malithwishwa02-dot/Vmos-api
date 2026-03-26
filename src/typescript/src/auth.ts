/**
 * VMOS API Authentication
 *
 * Provides HMAC-SHA256 authentication for VMOS API requests.
 */

import crypto from 'crypto';

export interface AuthHeaders {
  'Content-Type': string;
  'x-date': string;
  'x-host': string;
  Authorization: string;
}

export interface IAuth {
  signRequest(
    method: string,
    url: string,
    body?: Record<string, unknown>
  ): Record<string, string>;
}

/**
 * HMAC-SHA256 Authentication handler for VMOS API.
 */
export class HMACAuth implements IAuth {
  private accessKey: string;
  private secretKey: string;

  constructor(accessKey: string, secretKey: string) {
    this.accessKey = accessKey;
    this.secretKey = secretKey;
  }

  private getTimestamp(): string {
    return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  }

  private hashBody(body?: Record<string, unknown>): string {
    const bodyString = body ? JSON.stringify(body) : '';
    return crypto.createHash('sha256').update(bodyString).digest('base64');
  }

  private createCanonicalString(
    method: string,
    path: string,
    host: string,
    timestamp: string,
    contentType: string,
    bodyHash: string
  ): string {
    return [
      method.toUpperCase(),
      path,
      `content-type:${contentType}`,
      `x-date:${timestamp}`,
      `x-host:${host}`,
      bodyHash,
    ].join('\n');
  }

  private sign(stringToSign: string): string {
    return crypto
      .createHmac('sha256', this.secretKey)
      .update(stringToSign)
      .digest('base64');
  }

  signRequest(
    method: string,
    url: string,
    body?: Record<string, unknown>,
    contentType: string = 'application/json'
  ): Record<string, string> {
    // Parse URL
    const parsedUrl = new URL(url);
    const host = parsedUrl.host;
    const path = parsedUrl.pathname;

    // Generate timestamp
    const timestamp = this.getTimestamp();

    // Hash body
    const bodyHash = this.hashBody(body);

    // Create canonical string
    const canonicalString = this.createCanonicalString(
      method,
      path,
      host,
      timestamp,
      contentType,
      bodyHash
    );

    // Generate signature
    const signature = this.sign(canonicalString);

    // Build authorization header
    const signedHeaders = 'content-type;x-date;x-host';
    const authorization =
      `HMAC-SHA256 ` +
      `Credential=${this.accessKey}, ` +
      `SignedHeaders=${signedHeaders}, ` +
      `Signature=${signature}`;

    return {
      'Content-Type': contentType,
      'x-date': timestamp,
      'x-host': host,
      Authorization: authorization,
    };
  }
}

/**
 * No authentication (for local development or unsecured APIs).
 */
export class NoAuth implements IAuth {
  signRequest(
    method: string,
    url: string,
    body?: Record<string, unknown>,
    contentType: string = 'application/json'
  ): Record<string, string> {
    return {
      'Content-Type': contentType,
    };
  }
}
