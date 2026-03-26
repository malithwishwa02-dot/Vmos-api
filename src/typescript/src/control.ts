/**
 * VMOS Control API Client
 */

import http from 'http';
import https from 'https';
import { IAuth } from './auth';
import { VMOSAPIError, VMOSConnectionError, VMOSTimeoutError } from './errors';
import {
  VersionInfo,
  DisplayInfo,
  TopActivity,
  UINode,
  NodeSelector,
  NodeAction,
  NodeOptions,
  PackageInfo,
  ActionInfo,
  APIResponse,
} from './types';

export class ControlClient {
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
    body?: Record<string, unknown>,
    rawResponse: boolean = false
  ): Promise<T> {
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
        const chunks: Buffer[] = [];
        res.on('data', (chunk) => chunks.push(chunk));
        res.on('end', () => {
          const data = Buffer.concat(chunks);
          
          if (rawResponse) {
            resolve(data as unknown as T);
            return;
          }

          try {
            const response = JSON.parse(data.toString()) as APIResponse<T>;
            if (response.code !== undefined && response.code !== 200) {
              reject(
                new VMOSAPIError(
                  response.msg || 'Unknown error',
                  response.code,
                  response.requestId,
                  path
                )
              );
            } else {
              resolve((response.data || response) as T);
            }
          } catch {
            reject(new VMOSAPIError(`Invalid response`, res.statusCode, undefined, path));
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

  // ========== Base / Discovery ==========

  async versionInfo(): Promise<VersionInfo> {
    const data = await this.request<Record<string, unknown>>('GET', '/base/version_info');
    return {
      versionName: String(data.version_name || ''),
      versionCode: Number(data.version_code || 0),
      supportedList: (data.supported_list as string[]) || [],
    };
  }

  async listActions(paths?: string[], detail: boolean = false): Promise<ActionInfo[]> {
    const body: Record<string, unknown> = { detail };
    if (paths) body.paths = paths;

    const data = await this.request<Array<Record<string, unknown>>>('POST', '/base/list_action', body);
    return (data || []).map((item) => ({
      path: String(item.path || ''),
      description: item.description as string | undefined,
      method: item.method as string | undefined,
    }));
  }

  async sleep(durationMs: number): Promise<void> {
    await this.request('POST', '/base/sleep', { duration: durationMs });
  }

  // ========== Observation ==========

  async displayInfo(): Promise<DisplayInfo> {
    const data = await this.request<Record<string, unknown>>('GET', '/display/info');
    return {
      width: Number(data.width || 0),
      height: Number(data.height || 0),
      density: data.density as number | undefined,
      rotation: Number(data.rotation || 0),
    };
  }

  async screenshot(): Promise<Buffer> {
    try {
      return await this.request<Buffer>('GET', '/screenshot/format', undefined, true);
    } catch {
      // Fallback to data URL
      const data = await this.request<{ data_url: string }>('GET', '/screenshot/data_url');
      const base64 = data.data_url.split(',')[1];
      return Buffer.from(base64, 'base64');
    }
  }

  async screenshotDataUrl(): Promise<string> {
    const data = await this.request<{ data_url: string }>('GET', '/screenshot/data_url');
    return data.data_url;
  }

  async dumpCompact(): Promise<UINode | null> {
    const data = await this.request<Record<string, unknown>>('GET', '/accessibility/dump_compact');
    if (data.root) {
      return this.parseUINode(data.root as Record<string, unknown>);
    }
    if (data.hierarchy) {
      return this.parseUINode(data.hierarchy as Record<string, unknown>);
    }
    return null;
  }

  async topActivity(): Promise<TopActivity> {
    const data = await this.request<Record<string, unknown>>('GET', '/activity/top_activity');
    return {
      packageName: String(data.package_name || ''),
      className: String(data.class_name || ''),
      activityName: data.activity_name as string | undefined,
    };
  }

  // ========== UI Node Operations ==========

  async node(options: NodeOptions): Promise<UINode | null> {
    const body: Record<string, unknown> = {
      selector: this.buildSelector(options.selector),
    };

    if (options.waitTimeout !== undefined && options.waitTimeout > 0) {
      body.wait_timeout = options.waitTimeout;
      body.wait_interval = options.waitInterval || 500;
    }

    if (options.action) {
      body.action = options.action;
    }

    if (options.actionParams) {
      body.action_params = options.actionParams;
    }

    const data = await this.request<Record<string, unknown> | null>(
      'POST',
      '/accessibility/node',
      body
    );

    return data ? this.parseUINode(data) : null;
  }

  // ========== Input Control ==========

  async click(x: number, y: number): Promise<void> {
    await this.request('POST', '/input/click', { x, y });
  }

  async multiClick(
    x: number,
    y: number,
    times: number = 2,
    interval: number = 100
  ): Promise<void> {
    await this.request('POST', '/input/multi_click', { x, y, times, interval });
  }

  async swipe(
    startX: number,
    startY: number,
    endX: number,
    endY: number,
    duration: number = 300,
    upDelay: number = 0
  ): Promise<void> {
    await this.request('POST', '/input/swipe', {
      start_x: startX,
      start_y: startY,
      end_x: endX,
      end_y: endY,
      duration,
      up_delay: upDelay,
    });
  }

  async scrollBezier(
    startX: number,
    startY: number,
    endX: number,
    endY: number,
    duration: number = 500,
    upDelay: number = 0,
    clearFling: boolean = false
  ): Promise<void> {
    await this.request('POST', '/input/scroll_bezier', {
      start_x: startX,
      start_y: startY,
      end_x: endX,
      end_y: endY,
      duration,
      up_delay: upDelay,
      clear_fling: clearFling,
    });
  }

  async inputText(text: string): Promise<void> {
    await this.request('POST', '/input/text', { text });
  }

  async keyEvent(keyCode?: number, keyCodes?: number[]): Promise<void> {
    const body: Record<string, unknown> = {};
    if (keyCode !== undefined) body.key_code = keyCode;
    if (keyCodes !== undefined) body.key_codes = keyCodes;
    await this.request('POST', '/input/keyevent', body);
  }

  async pressBack(): Promise<void> {
    await this.keyEvent(4);
  }

  async pressHome(): Promise<void> {
    await this.keyEvent(3);
  }

  async pressEnter(): Promise<void> {
    await this.keyEvent(66);
  }

  // ========== Activity & Package ==========

  async startApp(packageName: string): Promise<void> {
    await this.request('POST', '/activity/start', { package_name: packageName });
  }

  async launchApp(
    packageName: string,
    grantAllPermissions: boolean = false
  ): Promise<void> {
    await this.request('POST', '/activity/launch_app', {
      package_name: packageName,
      grant_all_permissions: grantAllPermissions,
    });
  }

  async startActivity(
    packageName: string,
    options: {
      className?: string;
      action?: string;
      data?: string;
      extras?: Record<string, unknown>;
    } = {}
  ): Promise<void> {
    const body: Record<string, unknown> = { package_name: packageName };
    if (options.className) body.class_name = options.className;
    if (options.action) body.action = options.action;
    if (options.data) body.data = options.data;
    if (options.extras) body.extras = options.extras;

    await this.request('POST', '/activity/start_activity', body);
  }

  async stopApp(packageName: string): Promise<void> {
    await this.request('POST', '/activity/stop', { package_name: packageName });
  }

  async listPackages(type: 'user' | 'system' = 'user'): Promise<PackageInfo[]> {
    const data = await this.request<Array<Record<string, unknown>>>(
      'GET',
      `/package/list?type=${type}`
    );

    return (data || []).map((item) => ({
      packageName: String(item.package_name || ''),
      label: item.label as string | undefined,
      versionCode: item.version_code as number | undefined,
      versionName: item.version_name as string | undefined,
      isSystem: Boolean(item.is_system),
    }));
  }

  async installUriSync(uri: string): Promise<void> {
    await this.request('POST', '/package/install_uri_sync', { uri });
  }

  async uninstall(packageName: string, keepData: boolean = false): Promise<void> {
    await this.request('POST', '/package/uninstall', {
      package_name: packageName,
      keep_data: keepData,
    });
  }

  // ========== System Operations ==========

  async shell(command: string, asRoot: boolean = false): Promise<Record<string, unknown>> {
    return await this.request('POST', '/system/shell', { command, as_root: asRoot });
  }

  async settingsGet(namespace: string, key: string): Promise<string> {
    const data = await this.request<Record<string, unknown>>('POST', '/system/settings_get', {
      namespace,
      key,
    });
    return String(data.value || '');
  }

  async settingsPut(namespace: string, key: string, value: string): Promise<void> {
    await this.request('POST', '/system/settings_put', { namespace, key, value });
  }

  // ========== Clipboard ==========

  async clipboardSet(text: string): Promise<void> {
    await this.request('POST', '/clipboard/set', { text });
  }

  async clipboardGet(): Promise<string> {
    const data = await this.request<{ text: string }>('GET', '/clipboard/get');
    return data.text || '';
  }

  async clipboardClear(): Promise<void> {
    await this.request('POST', '/clipboard/clear', {});
  }

  // ========== Google Services ==========

  async setGoogleEnabled(enabled: boolean): Promise<void> {
    await this.request('POST', '/google/set_enabled', { enabled });
  }

  async getGoogleEnabled(): Promise<boolean> {
    const data = await this.request<{ enabled: boolean }>('GET', '/google/get_enabled');
    return Boolean(data.enabled);
  }

  async resetGaid(): Promise<void> {
    await this.request('POST', '/google/reset_gaid', {});
  }

  // ========== Convenience Methods ==========

  async openUrl(url: string, browser: string = 'mark.via'): Promise<void> {
    await this.startActivity(browser, {
      action: 'android.intent.action.VIEW',
      data: url,
    });
  }

  async findAndClick(
    selector: NodeSelector,
    timeout: number = 5000
  ): Promise<boolean> {
    const node = await this.node({
      selector,
      waitTimeout: timeout,
      action: 'click',
    });
    return node !== null;
  }

  async waitForText(text: string, timeout: number = 10000): Promise<boolean> {
    const node = await this.node({
      selector: { text },
      waitTimeout: timeout,
    });
    return node !== null;
  }

  // ========== Helpers ==========

  private buildSelector(selector: NodeSelector): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    if (selector.xpath) result.xpath = selector.xpath;
    if (selector.text) result.text = selector.text;
    if (selector.contentDesc) result.content_desc = selector.contentDesc;
    if (selector.resourceId) result.resource_id = selector.resourceId;
    if (selector.className) result.class_name = selector.className;
    if (selector.package) result.package = selector.package;
    if (selector.clickable !== undefined) result.clickable = selector.clickable;
    if (selector.enabled !== undefined) result.enabled = selector.enabled;
    if (selector.scrollable !== undefined) result.scrollable = selector.scrollable;
    if (selector.index !== undefined) result.index = selector.index;
    return result;
  }

  private parseUINode(data: Record<string, unknown>): UINode {
    const children: UINode[] = [];
    if (Array.isArray(data.children)) {
      for (const child of data.children) {
        children.push(this.parseUINode(child as Record<string, unknown>));
      }
    }

    let bounds: number[] | undefined;
    if (typeof data.bounds === 'string') {
      const match = data.bounds.match(/\d+/g);
      if (match && match.length === 4) {
        bounds = match.map(Number);
      }
    } else if (Array.isArray(data.bounds)) {
      bounds = data.bounds as number[];
    }

    return {
      text: data.text as string | undefined,
      contentDesc: (data.content_desc || data.contentDescription) as string | undefined,
      resourceId: (data.resource_id || data.resourceId) as string | undefined,
      className: (data.class_name || data.className) as string | undefined,
      package: data.package as string | undefined,
      bounds,
      clickable: Boolean(data.clickable),
      enabled: data.enabled !== false,
      scrollable: Boolean(data.scrollable),
      index: Number(data.index || 0),
      children,
    };
  }
}
