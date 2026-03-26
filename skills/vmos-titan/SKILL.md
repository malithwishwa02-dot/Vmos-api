---
name: vmos-titan
description: Comprehensive VMOS Cloud/Edge Android control skill. Use this skill when managing VMOS cloud phone instances or controlling Android cloud devices. Combines Container API (instance management) and Control API (device control) capabilities.
---

# VMOS Titan - AI Agent Skill

VMOS Titan provides AI agents with comprehensive knowledge to control VMOS Cloud/Edge Android virtual machines.

## Capabilities

### Container API (Instance Management)
- Create, start, stop, reboot, delete instances
- Batch operations on multiple devices
- App distribution and management
- Host system management
- Image and ADI management

### Control API (Device Control)
- Input control (click, swipe, text)
- Screenshot and UI observation
- Accessibility node operations
- App lifecycle management
- System settings and clipboard
- Google services control

## Connection Rules

### Determine Connection Method

1. Check if user provided `host_ip` or `cloud_ip`
2. If no IP provided, check for local `cbs_go` process:
   ```bash
   pgrep -x cbs_go >/dev/null 2>&1
   ```
3. If local `cbs_go` exists, default `host_ip=127.0.0.1`
4. If no IP and no local process, ask user for connection details

### Base URLs

| API | Port | Base URL |
|-----|------|----------|
| Container API | 18182 | `http://{host_ip}:18182` |
| Control API (via host) | 18182 | `http://{host_ip}:18182/android_api/v2/{db_id}` |
| Control API (direct) | 18185 | `http://{cloud_ip}:18185/api` |

## Core Workflow

Always follow: **Observe → Plan → Act → Verify**

### 1. Initial Connection

```bash
# Verify API support
curl -s "http://{base_url}/base/version_info"
```

If successful, the environment supports Control API.

### 2. Capability Discovery

```bash
# Get available actions
curl -X POST "http://{base_url}/base/list_action" \
  -H "Content-Type: application/json" \
  -d '{"detail": false}'
```

### 3. Observation Priority

**Use Screenshot when:**
- Need visual layout/color/icon verification
- Coordinate-based clicking
- Checking for overlays/popups
- Verifying rendered content

**Use Dump Compact when:**
- Text-based UI analysis
- Low-cost page verification
- Preparing for node operations
- Form field identification

### 4. Action Priority

1. **UI Node operations** - `/accessibility/node` for structured interaction
2. **Input commands** - `/input/click`, `/input/swipe`, `/input/text`
3. **App control** - `/activity/start`, `/activity/launch_app`
4. **Shell commands** - `/system/shell` (only when no specialized API)

### 5. Verification

After each action, re-observe to verify the result.

## Container API Quick Reference

### Instance Lifecycle

```bash
# Create instance
POST /container_api/v1/create
{"user_name": "device-001", "bool_start": true}

# List instances (try POST first, fallback to GET)
POST /container_api/v1/get_db
{}

# Batch start/stop
POST /container_api/v1/run
{"db_ids": ["EDGE001", "EDGE002"]}

POST /container_api/v1/stop
{"db_ids": ["EDGE001"]}

# Get instance detail
GET /container_api/v1/get_android_detail/{db_id}
```

### Instance Polling

After starting an instance:
```bash
# Poll ROM status until ready
GET /container_api/v1/rom_status/{db_id}
```

### App Distribution

```bash
# Install APK from URL
POST /android_api/v1/install_apk_from_url_batch
{"url": "https://example.com/app.apk", "db_ids": "EDGE001,EDGE002"}

# Start app on multiple devices
POST /android_api/v1/app_start
{"db_ids": ["EDGE001"], "app": "com.example.app"}
```

## Control API Quick Reference

### Observation

```bash
# Screenshot
GET /screenshot/format  # PNG bytes
GET /screenshot/data_url  # Base64

# UI hierarchy
GET /accessibility/dump_compact

# Current activity
GET /activity/top_activity

# Screen info
GET /display/info
```

### Input

```bash
# Click
POST /input/click
{"x": 540, "y": 960}

# Swipe
POST /input/swipe
{"start_x": 540, "start_y": 1500, "end_x": 540, "end_y": 500, "duration": 300}

# Text input
POST /input/text
{"text": "Hello World"}

# Key event (4=BACK, 3=HOME, 66=ENTER)
POST /input/keyevent
{"key_code": 4}
```

### UI Node Operations

```bash
# Find and click
POST /accessibility/node
{
  "selector": {"text": "Settings", "clickable": true},
  "action": "click"
}

# Wait and click
POST /accessibility/node
{
  "selector": {"resource_id": "com.example:id/btn"},
  "wait_timeout": 5000,
  "action": "click"
}

# Set text
POST /accessibility/node
{
  "selector": {"class_name": "android.widget.EditText"},
  "action": "set_text",
  "action_params": {"text": "Input value"}
}
```

### App Management

```bash
# Launch with permissions
POST /activity/launch_app
{"package_name": "com.example.app", "grant_all_permissions": true}

# Open URL in browser
POST /activity/start_activity
{
  "package_name": "mark.via",
  "action": "android.intent.action.VIEW",
  "data": "https://google.com"
}

# Install from URL
POST /package/install_uri_sync
{"uri": "https://example.com/app.apk"}

# List installed apps
GET /package/list?type=user
```

## Common Scenarios

### Install and Launch Third-Party App

1. Check if already installed:
   ```bash
   GET /package/list?type=user
   ```

2. If not installed, download and install:
   ```bash
   POST /package/install_uri_sync
   {"uri": "https://example.com/app.apk"}
   ```

3. Launch with permissions:
   ```bash
   POST /activity/launch_app
   {"package_name": "com.example.app", "grant_all_permissions": true}
   ```

4. Verify launch:
   ```bash
   GET /activity/top_activity
   ```

### Browser Search

1. Open browser with search URL:
   ```bash
   POST /activity/start_activity
   {
     "package_name": "mark.via",
     "action": "android.intent.action.VIEW",
     "data": "https://www.bing.com/search?q=VMOS+Cloud"
   }
   ```

2. Wait for page load:
   ```bash
   POST /base/sleep
   {"duration": 3000}
   ```

3. Get page content:
   ```bash
   GET /accessibility/dump_compact
   ```

### Automation Flow

```python
# Observe
screenshot = GET /screenshot/format
ui_tree = GET /accessibility/dump_compact

# Plan
# Identify target element from observation

# Act
POST /accessibility/node
{"selector": {"text": "Continue"}, "action": "click"}

# Verify
activity = GET /activity/top_activity
```

## Security Boundaries

### Always Confirm Before:
- Deleting applications
- Clearing app data
- Modifying system settings
- Changing permissions
- Executing shell commands
- Resetting device info
- Deleting instances
- Host shutdown/reset

### Do Not Modify Without Explicit Request:
- Timezone
- Language
- Country
- Google status
- Device information
- Location/sensors

## Error Handling

### Connection Errors
- If `/base/version_info` fails, the environment doesn't support Control API
- Check IP and port configuration
- Verify instance is running

### Action Errors
- If node not found, try different selector
- If click doesn't work, verify coordinates with screenshot
- If app won't start, check if installed

## Browser Preference

When opening URLs, use browsers in this order:
1. `mark.via` - Via browser (preferred)
2. `com.android.chrome` - Chrome

Check available browsers:
```bash
GET /package/list?type=user
# Look for browser packages
```

## References

- [Container API Reference](../docs/api-reference/container-api.md)
- [Control API Reference](../docs/api-reference/control-api.md)
- [Official VMOS Documentation](https://help.vmosedge.com/)
