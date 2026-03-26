# VMOS API Authentication Guide

VMOS API uses HMAC-SHA256 signature authentication to secure API requests.

## Overview

Each API request must include authentication headers that prove the request comes from an authorized client. This is done by signing the request with a secret key.

## Required Credentials

You need two credentials:

| Credential | Description |
|------------|-------------|
| `access_key` | Your public API access key |
| `secret_key` | Your private secret key (keep secure!) |

## Required Headers

Every authenticated request must include:

| Header | Description |
|--------|-------------|
| `Content-Type` | `application/json` (or `multipart/form-data` for uploads) |
| `x-date` | ISO 8601 timestamp in UTC |
| `x-host` | Target host (e.g., `192.168.1.100:18182`) |
| `Authorization` | HMAC-SHA256 signature |

## Signature Generation

### Step 1: Generate Timestamp

Create an ISO 8601 timestamp in UTC:

```python
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
# Example: "2024-01-15T10:30:00Z"
```

### Step 2: Hash Request Body

Create a SHA256 hash of the request body:

```python
import hashlib
import base64
import json

body = {"user_name": "test-001"}
body_string = json.dumps(body, separators=(",", ":"), sort_keys=True)
body_hash = base64.b64encode(
    hashlib.sha256(body_string.encode("utf-8")).digest()
).decode("utf-8")
```

### Step 3: Create Canonical String

Combine request components into a canonical string:

```python
canonical_string = "\n".join([
    "POST",                              # HTTP method
    "/container_api/v1/create",          # Path
    f"content-type:application/json",    # Content-Type header
    f"x-date:{timestamp}",               # Timestamp header
    f"x-host:192.168.1.100:18182",       # Host header
    body_hash,                           # Body hash
])
```

### Step 4: Generate Signature

Sign the canonical string with HMAC-SHA256:

```python
import hmac

signature = base64.b64encode(
    hmac.new(
        secret_key.encode("utf-8"),
        canonical_string.encode("utf-8"),
        hashlib.sha256,
    ).digest()
).decode("utf-8")
```

### Step 5: Build Authorization Header

```python
authorization = (
    f"HMAC-SHA256 "
    f"Credential={access_key}, "
    f"SignedHeaders=content-type;x-date;x-host, "
    f"Signature={signature}"
)
```

## Complete Python Example

```python
import hashlib
import hmac
import base64
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen


class VMOSAuth:
    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key

    def sign_request(self, method: str, url: str, body: dict = None) -> dict:
        # Parse URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path
        
        # Generate timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Hash body
        if body:
            body_string = json.dumps(body, separators=(",", ":"), sort_keys=True)
        else:
            body_string = ""
        body_hash = base64.b64encode(
            hashlib.sha256(body_string.encode("utf-8")).digest()
        ).decode("utf-8")
        
        # Create canonical string
        content_type = "application/json"
        canonical_string = "\n".join([
            method.upper(),
            path,
            f"content-type:{content_type}",
            f"x-date:{timestamp}",
            f"x-host:{host}",
            body_hash,
        ])
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode("utf-8"),
                canonical_string.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        
        # Build authorization header
        authorization = (
            f"HMAC-SHA256 "
            f"Credential={self.access_key}, "
            f"SignedHeaders=content-type;x-date;x-host, "
            f"Signature={signature}"
        )
        
        return {
            "Content-Type": content_type,
            "x-date": timestamp,
            "x-host": host,
            "Authorization": authorization,
        }


# Usage
auth = VMOSAuth("your_access_key", "your_secret_key")

url = "http://192.168.1.100:18182/container_api/v1/create"
body = {"user_name": "test-001"}

headers = auth.sign_request("POST", url, body)

request = Request(
    url,
    data=json.dumps(body).encode("utf-8"),
    headers=headers,
    method="POST"
)

with urlopen(request) as response:
    result = json.loads(response.read())
    print(result)
```

## TypeScript Example

```typescript
import crypto from 'crypto';

class VMOSAuth {
  constructor(
    private accessKey: string,
    private secretKey: string
  ) {}

  signRequest(method: string, url: string, body?: object): Record<string, string> {
    const parsedUrl = new URL(url);
    const host = parsedUrl.host;
    const path = parsedUrl.pathname;
    
    // Generate timestamp
    const timestamp = new Date().toISOString().replace(/\.\d{3}/, '');
    
    // Hash body
    const bodyString = body ? JSON.stringify(body) : '';
    const bodyHash = crypto
      .createHash('sha256')
      .update(bodyString)
      .digest('base64');
    
    // Create canonical string
    const contentType = 'application/json';
    const canonicalString = [
      method.toUpperCase(),
      path,
      `content-type:${contentType}`,
      `x-date:${timestamp}`,
      `x-host:${host}`,
      bodyHash,
    ].join('\n');
    
    // Generate signature
    const signature = crypto
      .createHmac('sha256', this.secretKey)
      .update(canonicalString)
      .digest('base64');
    
    // Build authorization header
    const authorization = 
      `HMAC-SHA256 ` +
      `Credential=${this.accessKey}, ` +
      `SignedHeaders=content-type;x-date;x-host, ` +
      `Signature=${signature}`;
    
    return {
      'Content-Type': contentType,
      'x-date': timestamp,
      'x-host': host,
      'Authorization': authorization,
    };
  }
}

// Usage
const auth = new VMOSAuth('your_access_key', 'your_secret_key');

const url = 'http://192.168.1.100:18182/container_api/v1/create';
const body = { user_name: 'test-001' };

const headers = auth.signRequest('POST', url, body);

fetch(url, {
  method: 'POST',
  headers,
  body: JSON.stringify(body),
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## cURL Example

For testing, you can use this bash function:

```bash
#!/bin/bash

vmos_request() {
    local METHOD="$1"
    local URL="$2"
    local BODY="$3"
    
    local ACCESS_KEY="your_access_key"
    local SECRET_KEY="your_secret_key"
    
    # Parse URL
    local HOST=$(echo "$URL" | sed -E 's|https?://([^/]+).*|\1|')
    local PATH=$(echo "$URL" | sed -E 's|https?://[^/]+||')
    
    # Generate timestamp
    local TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Hash body
    if [ -n "$BODY" ]; then
        local BODY_HASH=$(echo -n "$BODY" | openssl dgst -sha256 -binary | base64)
    else
        local BODY_HASH=$(echo -n "" | openssl dgst -sha256 -binary | base64)
    fi
    
    # Create canonical string
    local CANONICAL=$(printf "%s\n%s\ncontent-type:application/json\nx-date:%s\nx-host:%s\n%s" \
        "$METHOD" "$PATH" "$TIMESTAMP" "$HOST" "$BODY_HASH")
    
    # Generate signature
    local SIGNATURE=$(echo -n "$CANONICAL" | openssl dgst -sha256 -hmac "$SECRET_KEY" -binary | base64)
    
    # Build authorization
    local AUTH="HMAC-SHA256 Credential=$ACCESS_KEY, SignedHeaders=content-type;x-date;x-host, Signature=$SIGNATURE"
    
    # Make request
    if [ -n "$BODY" ]; then
        curl -s -X "$METHOD" "$URL" \
            -H "Content-Type: application/json" \
            -H "x-date: $TIMESTAMP" \
            -H "x-host: $HOST" \
            -H "Authorization: $AUTH" \
            -d "$BODY"
    else
        curl -s -X "$METHOD" "$URL" \
            -H "Content-Type: application/json" \
            -H "x-date: $TIMESTAMP" \
            -H "x-host: $HOST" \
            -H "Authorization: $AUTH"
    fi
}

# Usage
vmos_request POST "http://192.168.1.100:18182/container_api/v1/create" '{"user_name":"test-001"}'
```

## Security Best Practices

1. **Never expose secret key** - Keep it server-side only
2. **Use HTTPS in production** - Encrypt all traffic
3. **Rotate keys regularly** - Change credentials periodically
4. **Use environment variables** - Don't hardcode credentials
5. **Validate timestamps** - Servers may reject stale requests

## Troubleshooting

### 401 Unauthorized

- Check access_key and secret_key are correct
- Verify timestamp is in correct format and timezone (UTC)
- Ensure canonical string components match exactly
- Check signature encoding is base64

### 403 Forbidden

- Verify the access_key has permission for the endpoint
- Check if the API is enabled for your account

### Clock Skew

If your system clock is significantly different from the server:

```python
# Check your system time
import time
print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
```

Servers typically allow 5-15 minutes of clock skew.

## SDK Authentication

The VMOS SDK handles authentication automatically:

```python
from vmos_api import VMOSClient

# Authentication is handled internally
client = VMOSClient(
    host_ip="192.168.1.100",
    access_key="your_access_key",
    secret_key="your_secret_key"
)

# All requests are automatically signed
instances = client.container.list_instances()
```
