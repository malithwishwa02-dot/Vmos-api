# VMOS Control API Reference

The Control API provides fine-grained control over individual VMOS Android cloud phone instances.

## Base URLs

| Scenario | Base URL |
|----------|----------|
| With Container API installed | `http://{host_ip}:18182/android_api/v2/{db_id}` |
| Control API only (LAN mode) | `http://{cloud_ip}:18185/api` |

## Authentication

See [Authentication Guide](../guides/authentication.md) for HMAC-SHA256 signature details.

---

## Connection & Discovery

### Version Info

Check API support and discover available endpoints.

**Endpoint:** `GET /base/version_info`

**Response:**

```json
{
  "code": 200,
  "data": {
    "version_name": "2.5.0",
    "version_code": 250,
    "supported_list": [
      "/input/click",
      "/screenshot/format",
      "/accessibility/dump_compact"
    ]
  },
  "msg": "OK"
}
```

---

### List Actions

Query available API actions with optional details.

**Endpoint:** `POST /base/list_action`

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| `paths` | array | Specific paths to query (optional) |
| `detail` | boolean | Include detailed parameter info |

**Example - Get all actions:**

```json
{
  "detail": false
}
```

**Example - Get specific action details:**

```json
{
  "paths": ["/activity/start", "/input/click"],
  "detail": true
}
```

---

### Sleep

Pause execution for specified duration.

**Endpoint:** `POST /base/sleep`

**Request Body:**

```json
{
  "duration": 1000
}
```

---

## Observation

### Display Info

Get screen dimensions and configuration.

**Endpoint:** `GET /display/info`

**Response:**

```json
{
  "code": 200,
  "data": {
    "width": 1080,
    "height": 1920,
    "density": 480,
    "rotation": 0
  },
  "msg": "OK"
}
```

---

### Screenshot

Capture device screen.

**Endpoints:**

| Endpoint | Description | Response |
|----------|-------------|----------|
| `GET /screenshot/format` | PNG format | Image bytes |
| `GET /screenshot/raw` | Raw format | Image bytes |
| `GET /screenshot/data_url` | Base64 data URL | JSON with data_url |

**Data URL Response:**

```json
{
  "code": 200,
  "data": {
    "data_url": "data:image/png;base64,iVBORw0KGgo..."
  },
  "msg": "OK"
}
```

**When to use screenshots:**

- Visual layout verification
- Icon/color identification
- Coordinate-based clicking
- Overlay/popup detection

---

### Dump Compact

Get compact UI hierarchy dump.

**Endpoint:** `GET /accessibility/dump_compact`

**Response:**

```json
{
  "code": 200,
  "data": {
    "root": {
      "class_name": "android.widget.FrameLayout",
      "bounds": "[0,0][1080,1920]",
      "children": [
        {
          "text": "Settings",
          "class_name": "android.widget.TextView",
          "bounds": "[100,200][300,250]",
          "clickable": true
        }
      ]
    }
  },
  "msg": "OK"
}
```

**When to use dump_compact:**

- Text-based UI analysis
- Low-cost page verification
- Preparation for /accessibility/node operations

---

### Top Activity

Get current foreground activity.

**Endpoint:** `GET /activity/top_activity`

**Response:**

```json
{
  "code": 200,
  "data": {
    "package_name": "com.android.settings",
    "class_name": ".Settings"
  },
  "msg": "OK"
}
```

---

## UI Node Operations

### Node

Find and optionally interact with UI nodes.

**Endpoint:** `POST /accessibility/node`

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| `selector` | object | Node selector criteria (required) |
| `wait_timeout` | integer | Timeout in ms (default: 0) |
| `wait_interval` | integer | Polling interval in ms (default: 500) |
| `action` | string | Action to perform on found node |
| `action_params` | object | Parameters for the action |

**Selector Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `xpath` | string | XPath expression |
| `text` | string | Exact text match |
| `content_desc` | string | Content description |
| `resource_id` | string | Resource ID |
| `class_name` | string | Widget class name |
| `package` | string | Package name |
| `clickable` | boolean | Clickable filter |
| `enabled` | boolean | Enabled filter |
| `scrollable` | boolean | Scrollable filter |
| `index` | integer | Child index |

**Available Actions:**

| Action | Description |
|--------|-------------|
| `click` | Click the node |
| `long_click` | Long press the node |
| `set_text` | Set text (requires action_params.text) |
| `clear_text` | Clear text content |
| `scroll_forward` | Scroll forward |
| `scroll_backward` | Scroll backward |
| `scroll_up` | Scroll up |
| `scroll_down` | Scroll down |
| `focus` | Focus the node |
| `copy` | Copy content |
| `paste` | Paste content |
| `cut` | Cut content |

**Example - Find node:**

```json
{
  "selector": {
    "text": "Settings",
    "clickable": true
  }
}
```

**Example - Wait and click:**

```json
{
  "selector": {
    "resource_id": "com.example:id/button"
  },
  "wait_timeout": 5000,
  "action": "click"
}
```

**Example - Set text:**

```json
{
  "selector": {
    "class_name": "android.widget.EditText"
  },
  "action": "set_text",
  "action_params": {
    "text": "Hello World"
  }
}
```

---

## Input Control

### Click

Perform a click at coordinates.

**Endpoint:** `POST /input/click`

**Request Body:**

```json
{
  "x": 540,
  "y": 960
}
```

---

### Multi Click

Perform multiple clicks at coordinates.

**Endpoint:** `POST /input/multi_click`

**Request Body:**

```json
{
  "x": 540,
  "y": 960,
  "times": 2,
  "interval": 100
}
```

---

### Swipe

Perform linear swipe gesture.

**Endpoint:** `POST /input/swipe`

**Request Body:**

```json
{
  "start_x": 540,
  "start_y": 1500,
  "end_x": 540,
  "end_y": 500,
  "duration": 300,
  "up_delay": 0
}
```

---

### Scroll Bezier

Perform curved swipe (more natural movement).

**Endpoint:** `POST /input/scroll_bezier`

**Request Body:**

```json
{
  "start_x": 540,
  "start_y": 1500,
  "end_x": 540,
  "end_y": 500,
  "duration": 500,
  "up_delay": 0,
  "clear_fling": false
}
```

---

### Input Text

Type text at current focus.

**Endpoint:** `POST /input/text`

**Request Body:**

```json
{
  "text": "Hello World!"
}
```

---

### Key Event

Send key events.

**Endpoint:** `POST /input/keyevent`

**Request Body:**

```json
{
  "key_code": 4
}
```

Or multiple keys:

```json
{
  "key_codes": [4, 66]
}
```

**Common Key Codes:**

| Code | Key |
|------|-----|
| 3 | HOME |
| 4 | BACK |
| 24 | VOLUME_UP |
| 25 | VOLUME_DOWN |
| 26 | POWER |
| 66 | ENTER |
| 67 | DEL (backspace) |

---

## Activity & Package

### Start App

Start an application.

**Endpoint:** `POST /activity/start`

**Request Body:**

```json
{
  "package_name": "com.android.settings"
}
```

---

### Launch App

Launch with optional permission grants.

**Endpoint:** `POST /activity/launch_app`

**Request Body:**

```json
{
  "package_name": "com.example.app",
  "grant_all_permissions": true
}
```

---

### Start Activity

Start specific activity with intent.

**Endpoint:** `POST /activity/start_activity`

**Request Body:**

```json
{
  "package_name": "com.android.chrome",
  "action": "android.intent.action.VIEW",
  "data": "https://www.google.com"
}
```

**Open URL in browser:**

```json
{
  "package_name": "mark.via",
  "action": "android.intent.action.VIEW",
  "data": "https://example.com"
}
```

**Note:** Browser preference order: `mark.via` > `com.android.chrome`

---

### Stop App

Force stop an application.

**Endpoint:** `POST /activity/stop`

**Request Body:**

```json
{
  "package_name": "com.example.app"
}
```

---

### List Packages

Get installed packages.

**Endpoint:** `GET /package/list`

**Query Parameters:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| `type` | `user`, `system` | Package type filter |

**Example:** `GET /package/list?type=user`

---

### Install APK (Sync)

Install APK from local path.

**Endpoint:** `POST /package/install_sync`

**Request Body:**

```json
{
  "path": "/sdcard/Download/app.apk"
}
```

**Supported formats:** `apk`, `apks`, `apkm`, `xapk`

---

### Install from URI (Sync)

Install APK from URL.

**Endpoint:** `POST /package/install_uri_sync`

**Request Body:**

```json
{
  "uri": "https://example.com/app.apk"
}
```

---

### Uninstall

Remove an application.

**Endpoint:** `POST /package/uninstall`

**Request Body:**

```json
{
  "package_name": "com.example.app",
  "keep_data": false
}
```

---

## System Operations

### Shell Command

Execute shell command.

**Endpoint:** `POST /system/shell`

**Request Body:**

```json
{
  "command": "ls /sdcard",
  "as_root": false
}
```

**Note:** Use specialized APIs when available instead of shell.

---

### Settings Get

Read Android system setting.

**Endpoint:** `POST /system/settings_get`

**Request Body:**

```json
{
  "namespace": "system",
  "key": "screen_brightness"
}
```

**Namespaces:** `system`, `secure`, `global`

---

### Settings Put

Write Android system setting.

**Endpoint:** `POST /system/settings_put`

**Request Body:**

```json
{
  "namespace": "system",
  "key": "screen_brightness",
  "value": "128"
}
```

---

## Clipboard

### Set Clipboard

**Endpoint:** `POST /clipboard/set`

**Request Body:**

```json
{
  "text": "Copied text"
}
```

---

### Get Clipboard

**Endpoint:** `GET /clipboard/get`

---

### List Clipboard

Get clipboard history.

**Endpoint:** `GET /clipboard/list`

---

### Clear Clipboard

**Endpoint:** `POST /clipboard/clear`

---

## Google Services

### Set Google Enabled

**Endpoint:** `POST /google/set_enabled`

**Request Body:**

```json
{
  "enabled": true
}
```

---

### Get Google Enabled

**Endpoint:** `GET /google/get_enabled`

---

### Reset GAID

Reset Google Advertising ID.

**Endpoint:** `POST /google/reset_gaid`

---

## Observation Strategy

### When to use Screenshots

- Visual layout verification
- Icon/color/image identification
- Coordinate-based interactions
- Overlay/popup detection
- Complex UI verification

### When to use Dump Compact

- Text-based UI analysis
- Form field identification
- Low-cost page verification
- Preparation for node operations

### Recommended Approach

1. Use screenshot for visual understanding
2. Use dump_compact for structural analysis
3. Use /accessibility/node for interactions
4. Fall back to coordinates when necessary

---

## Common Workflows

### Observe-Plan-Act-Verify

1. `GET /base/version_info` - Verify API support
2. `POST /base/list_action` - Discover capabilities
3. Take screenshot or dump_compact
4. Plan action based on observation
5. Execute action
6. Verify result with observation

### Open App and Navigate

```python
# 1. Launch app
POST /activity/launch_app {"package_name": "com.example.app"}

# 2. Wait for UI
POST /base/sleep {"duration": 2000}

# 3. Find and click button
POST /accessibility/node {
  "selector": {"text": "Continue"},
  "wait_timeout": 5000,
  "action": "click"
}

# 4. Verify navigation
GET /activity/top_activity
```

---

## Error Handling

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Endpoint or node not found |
| 408 | Timeout - Wait timeout exceeded |
| 500 | Internal Server Error |

---

## Security Considerations

**Always confirm user intent before:**

- Deleting applications
- Clearing app data
- Modifying system settings
- Changing permissions
- Executing shell commands

**Do not modify without explicit request:**

- Timezone
- Language
- Country
- Google status
- Device info
- Location/sensors
