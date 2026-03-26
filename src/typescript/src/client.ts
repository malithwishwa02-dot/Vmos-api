/**
 * VMOS API Main Client
 */

import { execSync } from 'child_process';
import { HMACAuth, NoAuth, IAuth } from './auth';
import { ContainerClient } from './container';
import { ControlClient } from './control';
import { VMOSConnectionError } from './errors';
import { VMOSClientOptions, HealthStatus, SystemInfo, ImageInfo } from './types';
import http from 'http';
import https from 'https';

/**
 * Host management client
 */
class HostClient {
  private baseUrl: string;
  private auth: IAuth;
  private timeout: number;

  constructor(baseUrl: string, auth: IAuth, timeout: number) {
    this.baseUrl = baseUrl;
    this.auth = auth;
    this.timeout = timeout;
  }

  private async request<T>(method: string, path: string): Promise<T> {
    return new Promise((resolve, reject) => {
      const url = `${this.baseUrl}${path}`;
      const parsedUrl = new URL(url);
      const headers = this.auth.signRequest(method, url);

      const options: http.RequestOptions = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || 80,
        path: parsedUrl.pathname,
        method,
        headers,
        timeout: this.timeout,
      };

      const httpModule = parsedUrl.protocol === 'https:' ? https : http;

      const req = httpModule.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          try {
            const response = JSON.parse(data);
            resolve(response.data || response);
          } catch {
            reject(new Error(`Invalid response: ${data}`));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timed out'));
      });

      req.end();
    });
  }

  async heartbeat(): Promise<HealthStatus> {
    return this.request<HealthStatus>('GET', '/v1/heartbeat');
  }

  async systemInfo(): Promise<SystemInfo> {
    return this.request<SystemInfo>('GET', '/v1/systeminfo');
  }

  async listImages(): Promise<ImageInfo[]> {
    return this.request<ImageInfo[]>('GET', '/v1/get_img_list');
  }

  async swapEnable(): Promise<void> {
    await this.request('GET', '/v1/swap/1');
  }

  async swapDisable(): Promise<void> {
    await this.request('GET', '/v1/swap/0');
  }
}

/**
 * Main VMOS API client.
 *
 * Provides access to both Container API and Control API through a unified interface.
 */
export class VMOSClient {
  private _hostIp?: string;
  private _cloudIp?: string;
  private _containerPort: number;
  private _controlPort: number;
  private _timeout: number;
  private _auth: IAuth;
  private _containerClient?: ContainerClient;
  private _hostClient?: HostClient;
  private _controlClients: Map<string, ControlClient> = new Map();

  constructor(options: VMOSClientOptions = {}) {
    this._hostIp = options.hostIp;
    this._cloudIp = options.cloudIp;
    this._containerPort = options.containerPort || 18182;
    this._controlPort = options.controlPort || 18185;
    this._timeout = options.timeout || 30000;

    // Setup authentication
    if (options.accessKey && options.secretKey) {
      this._auth = new HMACAuth(options.accessKey, options.secretKey);
    } else {
      this._auth = new NoAuth();
    }

    // Auto-detect local installation
    if (options.autoDetect !== false && !options.hostIp && !options.cloudIp) {
      this._hostIp = this.detectLocalHost();
    }
  }

  private detectLocalHost(): string | undefined {
    try {
      execSync('pgrep -x cbs_go', { stdio: 'ignore' });
      return '127.0.0.1';
    } catch {
      return undefined;
    }
  }

  get hostIp(): string | undefined {
    return this._hostIp;
  }

  get cloudIp(): string | undefined {
    return this._cloudIp;
  }

  get containerBaseUrl(): string {
    if (!this._hostIp) {
      throw new VMOSConnectionError(
        'No host_ip configured. Please provide hostIp or ensure you are running on a VMOS Edge host machine.'
      );
    }
    return `http://${this._hostIp}:${this._containerPort}`;
  }

  /**
   * Access the Container API client.
   */
  get container(): ContainerClient {
    if (!this._containerClient) {
      this._containerClient = new ContainerClient(
        this.containerBaseUrl,
        this._auth,
        this._timeout
      );
    }
    return this._containerClient;
  }

  /**
   * Access the Host management client.
   */
  get host(): HostClient {
    if (!this._hostClient) {
      this._hostClient = new HostClient(
        this.containerBaseUrl,
        this._auth,
        this._timeout
      );
    }
    return this._hostClient;
  }

  /**
   * Access the Control API client for a specific device.
   */
  control(dbId?: string): ControlClient {
    let baseUrl: string;

    if (this._hostIp && dbId) {
      baseUrl = `http://${this._hostIp}:${this._containerPort}/android_api/v2/${dbId}`;
    } else if (this._cloudIp) {
      baseUrl = `http://${this._cloudIp}:${this._controlPort}/api`;
    } else {
      throw new VMOSConnectionError(
        'Cannot determine Control API endpoint. Please provide either hostIp with dbId, or cloudIp.'
      );
    }

    if (!this._controlClients.has(baseUrl)) {
      this._controlClients.set(
        baseUrl,
        new ControlClient(baseUrl, this._auth, this._timeout)
      );
    }

    return this._controlClients.get(baseUrl)!;
  }

  /**
   * Verify connection to VMOS API.
   */
  async verifyConnection(): Promise<boolean> {
    try {
      if (this._hostIp) {
        await this.host.heartbeat();
        return true;
      }
    } catch (e) {
      throw new VMOSConnectionError(
        `Failed to verify connection: ${e}`,
        this._hostIp,
        this._containerPort
      );
    }
    return false;
  }

  /**
   * Close all connections and cleanup resources.
   */
  close(): void {
    this._containerClient = undefined;
    this._hostClient = undefined;
    this._controlClients.clear();
  }
}
