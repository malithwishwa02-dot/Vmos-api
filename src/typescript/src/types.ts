/**
 * VMOS API Types
 */

// ========== Instance Types ==========

export type InstanceStatus =
  | 'creating'
  | 'starting'
  | 'running'
  | 'stopping'
  | 'stopped'
  | 'rebooting'
  | 'rebuilding'
  | 'renewing'
  | 'deleting'
  | 'unknown';

export interface Instance {
  dbId: string;
  userName: string;
  status: InstanceStatus;
  adbAddress?: string;
  cloudIp?: string;
  imageRepository?: string;
  resolution?: string;
  createdAt?: string;
}

export interface InstanceDetail extends Instance {
  romStatus?: string;
  androidVersion?: string;
  cpuCores?: number;
  memoryMb?: number;
  storageGb?: number;
  adbPort?: number;
  screenPort?: number;
  locale?: string;
  timezone?: string;
  country?: string;
  gmsEnabled?: boolean;
}

export interface CreateInstanceOptions {
  userName: string;
  count?: number;
  boolStart?: boolean;
  boolMacvlan?: boolean;
  macvlanNetwork?: string;
  macvlanStartIp?: string;
  imageRepository?: string;
  adiId?: number;
  resolution?: string;
  locale?: string;
  timezone?: string;
  country?: string;
  userProp?: Record<string, unknown>;
  certHash?: string;
  certContent?: string;
}

export interface CreateInstanceResult {
  success: boolean;
  dbIds: string[];
  message?: string;
}

// ========== Host Types ==========

export interface SystemInfo {
  cpuUsage?: number;
  memoryUsed?: string;
  memoryTotal?: string;
  diskUsed?: string;
  diskTotal?: string;
}

export interface HealthStatus {
  hostOk?: boolean;
  dockerOk?: boolean;
  pingOk?: boolean;
}

export interface ImageInfo {
  name: string;
  size?: string;
}

// ========== Control API Types ==========

export interface VersionInfo {
  versionName: string;
  versionCode: number;
  supportedList: string[];
}

export interface DisplayInfo {
  width: number;
  height: number;
  density?: number;
  rotation: number;
}

export interface TopActivity {
  packageName: string;
  className: string;
  activityName?: string;
}

export interface UINode {
  text?: string;
  contentDesc?: string;
  resourceId?: string;
  className?: string;
  package?: string;
  bounds?: number[];
  clickable: boolean;
  enabled: boolean;
  scrollable: boolean;
  index: number;
  children: UINode[];
}

export interface NodeSelector {
  xpath?: string;
  text?: string;
  contentDesc?: string;
  resourceId?: string;
  className?: string;
  package?: string;
  clickable?: boolean;
  enabled?: boolean;
  scrollable?: boolean;
  index?: number;
}

export type NodeAction =
  | 'click'
  | 'long_click'
  | 'set_text'
  | 'clear_text'
  | 'scroll_forward'
  | 'scroll_backward'
  | 'scroll_up'
  | 'scroll_down'
  | 'focus'
  | 'copy'
  | 'paste'
  | 'cut';

export interface NodeOptions {
  selector: NodeSelector;
  waitTimeout?: number;
  waitInterval?: number;
  action?: NodeAction;
  actionParams?: Record<string, unknown>;
}

export interface PackageInfo {
  packageName: string;
  label?: string;
  versionCode?: number;
  versionName?: string;
  isSystem: boolean;
}

export interface ActionInfo {
  path: string;
  description?: string;
  method?: string;
  parameters?: Record<string, unknown>[];
}

// ========== Client Options ==========

export interface VMOSClientOptions {
  hostIp?: string;
  cloudIp?: string;
  accessKey?: string;
  secretKey?: string;
  containerPort?: number;
  controlPort?: number;
  timeout?: number;
  autoDetect?: boolean;
}

// ========== API Response ==========

export interface APIResponse<T = unknown> {
  code: number;
  data?: T;
  msg?: string;
  requestId?: string;
}
