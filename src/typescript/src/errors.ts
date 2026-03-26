/**
 * VMOS API Errors
 */

export class VMOSError extends Error {
  details: Record<string, unknown>;

  constructor(message: string, details: Record<string, unknown> = {}) {
    super(message);
    this.name = 'VMOSError';
    this.details = details;
  }
}

export class VMOSConnectionError extends VMOSError {
  constructor(
    message: string = 'Failed to connect to VMOS API',
    host?: string,
    port?: number
  ) {
    const details: Record<string, unknown> = {};
    if (host) details.host = host;
    if (port) details.port = port;
    super(message, details);
    this.name = 'VMOSConnectionError';
  }
}

export class VMOSAuthenticationError extends VMOSError {
  constructor(
    message: string = 'Authentication failed',
    statusCode?: number
  ) {
    const details: Record<string, unknown> = {};
    if (statusCode) details.statusCode = statusCode;
    super(message, details);
    this.name = 'VMOSAuthenticationError';
  }
}

export class VMOSAPIError extends VMOSError {
  code?: number;
  requestId?: string;
  endpoint?: string;

  constructor(
    message: string,
    code?: number,
    requestId?: string,
    endpoint?: string
  ) {
    const details: Record<string, unknown> = {};
    if (code !== undefined) details.code = code;
    if (requestId) details.requestId = requestId;
    if (endpoint) details.endpoint = endpoint;
    super(message, details);
    this.name = 'VMOSAPIError';
    this.code = code;
    this.requestId = requestId;
    this.endpoint = endpoint;
  }
}

export class VMOSTimeoutError extends VMOSError {
  constructor(timeout?: number, endpoint?: string) {
    const details: Record<string, unknown> = {};
    if (timeout) details.timeout = timeout;
    if (endpoint) details.endpoint = endpoint;
    super('Request timed out', details);
    this.name = 'VMOSTimeoutError';
  }
}

export class VMOSInstanceNotFoundError extends VMOSError {
  dbId: string;

  constructor(dbId: string) {
    super(`Instance not found: ${dbId}`, { dbId });
    this.name = 'VMOSInstanceNotFoundError';
    this.dbId = dbId;
  }
}
