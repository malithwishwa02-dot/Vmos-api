/**
 * VMOS Container API Client
 */

import http from 'http';
import https from 'https';
import { IAuth } from './auth';
import { VMOSAPIError, VMOSConnectionError, VMOSTimeoutError } from './errors';
import {
  Instance,
  InstanceDetail,
  InstanceStatus,
  CreateInstanceOptions,
  CreateInstanceResult,
  APIResponse,
} from './types';

export class ContainerClient {
  private baseUrl: string;
  private auth: IAuth;
  private timeout: number;

  constructor(baseUrl: string, auth: IAuth, timeout: number = 30000) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.auth = auth;
    this.timeout = timeout;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: Record<string, unknown>
  ): Promise<APIResponse<T>> {
    return new Promise((resolve, reject) => {
      const url = `${this.baseUrl}${path}`;
      const parsedUrl = new URL(url);
      const headers = this.auth.signRequest(method, url, body);

      const options: http.RequestOptions = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
        path: parsedUrl.pathname + parsedUrl.search,
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
            const response = JSON.parse(data) as APIResponse<T>;
            if (response.code !== 200) {
              reject(
                new VMOSAPIError(
                  response.msg || 'Unknown error',
                  response.code,
                  response.requestId,
                  path
                )
              );
            } else {
              resolve(response);
            }
          } catch {
            reject(new VMOSAPIError(`Invalid response: ${data}`, res.statusCode, undefined, path));
          }
        });
      });

      req.on('error', (err) => {
        reject(new VMOSConnectionError(err.message));
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new VMOSTimeoutError(this.timeout, path));
      });

      if (body) {
        req.write(JSON.stringify(body));
      }
      req.end();
    });
  }

  // ========== Instance Management ==========

  async create(options: CreateInstanceOptions): Promise<CreateInstanceResult> {
    const body: Record<string, unknown> = {
      user_name: options.userName,
    };

    if (options.count !== undefined) body.count = options.count;
    if (options.boolStart !== undefined) body.bool_start = options.boolStart;
    if (options.imageRepository) body.image_repository = options.imageRepository;
    if (options.adiId !== undefined) body.adiID = options.adiId;
    if (options.resolution) body.resolution = options.resolution;
    if (options.locale) body.locale = options.locale;
    if (options.timezone) body.timezone = options.timezone;
    if (options.country) body.country = options.country;
    if (options.userProp) body.userProp = options.userProp;

    const response = await this.request<{ db_ids: string[] }>(
      'POST',
      '/container_api/v1/create',
      body
    );

    return {
      success: response.code === 200,
      dbIds: response.data?.db_ids || [],
      message: response.msg,
    };
  }

  async listInstances(): Promise<Instance[]> {
    let response: APIResponse<Array<Record<string, unknown>>>;
    
    try {
      response = await this.request<Array<Record<string, unknown>>>(
        'POST',
        '/container_api/v1/get_db',
        {}
      );
    } catch {
      response = await this.request<Array<Record<string, unknown>>>(
        'GET',
        '/container_api/v1/get_db'
      );
    }

    return (response.data || []).map((item) => this.parseInstance(item));
  }

  async getDetail(dbId: string): Promise<InstanceDetail> {
    const response = await this.request<Record<string, unknown>>(
      'GET',
      `/container_api/v1/get_android_detail/${dbId}`
    );
    return this.parseInstanceDetail(response.data || {});
  }

  async romStatus(dbId: string): Promise<Record<string, unknown>> {
    const response = await this.request<Record<string, unknown>>(
      'GET',
      `/container_api/v1/rom_status/${dbId}`
    );
    return response.data || {};
  }

  // ========== Lifecycle ==========

  async start(dbIds: string[]): Promise<void> {
    await this.request('POST', '/container_api/v1/run', { db_ids: dbIds });
  }

  async stop(dbIds: string[]): Promise<void> {
    await this.request('POST', '/container_api/v1/stop', { db_ids: dbIds });
  }

  async reboot(dbIds: string[]): Promise<void> {
    await this.request('POST', '/container_api/v1/reboot', { db_ids: dbIds });
  }

  async reset(dbIds: string[]): Promise<void> {
    await this.request('POST', '/container_api/v1/reset', { db_ids: dbIds });
  }

  async delete(dbIds: string[]): Promise<void> {
    await this.request('POST', '/container_api/v1/delete', { db_ids: dbIds });
  }

  async rename(dbId: string, newUserName: string): Promise<void> {
    await this.request('GET', `/container_api/v1/rename/${dbId}/${newUserName}`);
  }

  // ========== App Management ==========

  async appStart(dbIds: string[], app: string): Promise<void> {
    await this.request('POST', '/android_api/v1/app_start', {
      db_ids: dbIds,
      app,
    });
  }

  async appStop(dbIds: string[], app: string): Promise<void> {
    await this.request('POST', '/android_api/v1/app_stop', {
      db_ids: dbIds,
      app,
    });
  }

  async installApkFromUrl(dbIds: string[], url: string): Promise<void> {
    await this.request('POST', '/android_api/v1/install_apk_from_url_batch', {
      db_ids: dbIds.join(','),
      url,
    });
  }

  // ========== Helpers ==========

  private parseInstance(data: Record<string, unknown>): Instance {
    return {
      dbId: String(data.db_id || ''),
      userName: String(data.user_name || ''),
      status: this.parseStatus(String(data.status || '')),
      adbAddress: data.adb_address as string | undefined,
      cloudIp: data.cloud_ip as string | undefined,
      imageRepository: data.image_repository as string | undefined,
      resolution: data.resolution as string | undefined,
      createdAt: data.created_at as string | undefined,
    };
  }

  private parseInstanceDetail(data: Record<string, unknown>): InstanceDetail {
    const instance = this.parseInstance(data);
    return {
      ...instance,
      romStatus: data.rom_status as string | undefined,
      androidVersion: data.android_version as string | undefined,
      cpuCores: data.cpu_cores as number | undefined,
      memoryMb: data.memory_mb as number | undefined,
      storageGb: data.storage_gb as number | undefined,
      adbPort: data.adb_port as number | undefined,
      screenPort: data.screen_port as number | undefined,
      locale: data.locale as string | undefined,
      timezone: data.timezone as string | undefined,
      country: data.country as string | undefined,
      gmsEnabled: data.gms_enabled as boolean | undefined,
    };
  }

  private parseStatus(status: string): InstanceStatus {
    const validStatuses: InstanceStatus[] = [
      'creating',
      'starting',
      'running',
      'stopping',
      'stopped',
      'rebooting',
      'rebuilding',
      'renewing',
      'deleting',
    ];
    const lower = status.toLowerCase() as InstanceStatus;
    return validStatuses.includes(lower) ? lower : 'unknown';
  }
}
