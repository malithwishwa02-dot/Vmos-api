# AI Agent Integration Guide

This guide explains how to integrate VMOS API with AI agents for automated Android device control.

## Overview

VMOS Titan is a skill package that provides AI agents with comprehensive knowledge to control VMOS cloud phones. It follows the **Observe-Plan-Act-Verify** paradigm.

## Quick Start

### Install the Skill

```bash
npx skills add https://github.com/malithwishwa02-dot/Vmos-api --skill vmos-titan
```

### Skill Capabilities

The VMOS Titan skill provides knowledge for:

1. **Container API** - Instance management (create, start, stop, delete)
2. **Control API** - Device control (input, screenshots, apps)
3. **Connection Methods** - Auto-detect and configure connections
4. **Best Practices** - Error handling, security, optimization

## Workflow: Observe-Plan-Act-Verify

### 1. Observe

First, gather information about the current state:

```python
# Get API version and capabilities
version = control.version_info()
actions = control.list_actions()

# Get screen state
screenshot = control.screenshot()
ui_tree = control.dump_compact()
activity = control.top_activity()
```

**When to use Screenshot:**
- Visual layout verification
- Color/icon identification
- Coordinate-based clicking
- Popup/overlay detection

**When to use Dump Compact:**
- Text-based UI analysis
- Low-cost page verification
- Form field identification
- Preparation for node operations

### 2. Plan

Based on observation, plan the next action:

```python
# Example: Find the target element
ui = control.dump_compact()
target = ui.find(text="Settings")

if target:
    # Plan: Click using node selector (preferred)
    action_plan = {
        "method": "node",
        "selector": {"text": "Settings"},
        "action": "click"
    }
else:
    # Plan: Fall back to coordinate click
    # Need to analyze screenshot for coordinates
    pass
```

### 3. Act

Execute the planned action:

```python
# Preferred: Use node operations
control.node(
    selector={"text": "Settings"},
    action="click"
)

# Alternative: Coordinate click
control.click(x=540, y=960)

# Text input
control.input_text("Hello World")

# Key events
control.press_back()
```

### 4. Verify

Confirm the action produced the expected result:

```python
# Check current activity
activity = control.top_activity()
assert activity.package_name == "com.android.settings"

# Or check UI state
ui = control.dump_compact()
assert ui.find(text="Wi-Fi") is not None
```

## Connection Detection

The agent should auto-detect connection method:

```python
def detect_connection():
    # Check for local VMOS Edge
    import subprocess
    try:
        result = subprocess.run(
            ["pgrep", "-x", "cbs_go"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return {"host_ip": "127.0.0.1", "type": "local"}
    except:
        pass
    
    # Need user to provide IP
    return {"type": "unknown"}
```

## Common Tasks

### Launch App and Navigate

```python
async def launch_and_navigate(control, package_name, target_text):
    # Launch app
    await control.launch_app(package_name, grant_all_permissions=True)
    await asyncio.sleep(2)
    
    # Wait for target element
    node = await control.node(
        selector={"text": target_text},
        wait_timeout=5000
    )
    
    if node:
        # Click the element
        await control.node(
            selector={"text": target_text},
            action="click"
        )
        return True
    return False
```

### Browser Automation

```python
async def search_in_browser(control, query):
    # Open browser with search URL
    await control.start_activity(
        package_name="mark.via",  # Preferred browser
        action="android.intent.action.VIEW",
        data=f"https://www.bing.com/search?q={query}"
    )
    
    await asyncio.sleep(3)
    
    # Get page content
    ui = await control.dump_compact()
    return ui
```

### Install and Run App

```python
async def install_and_run(control, apk_url, package_name):
    # Install APK
    await control.install_uri_sync(uri=apk_url)
    
    # Launch with permissions
    await control.launch_app(
        package_name=package_name,
        grant_all_permissions=True
    )
    
    # Verify launch
    await asyncio.sleep(2)
    activity = await control.top_activity()
    return activity.package_name == package_name
```

## Error Handling

```python
from vmos_api.exceptions import (
    VMOSAPIError,
    VMOSConnectionError,
    VMOSTimeoutError,
)

async def safe_action(control, action_fn):
    try:
        return await action_fn()
    except VMOSConnectionError as e:
        # Connection lost - try to reconnect
        logger.error(f"Connection error: {e}")
        return None
    except VMOSTimeoutError as e:
        # Operation timed out - may need to retry
        logger.warning(f"Timeout: {e}")
        return None
    except VMOSAPIError as e:
        # API error - check error code
        logger.error(f"API error {e.code}: {e.message}")
        return None
```

## Security Guidelines

### Always Confirm Before:
- Deleting applications
- Clearing app data
- Modifying system settings
- Changing permissions
- Executing shell commands
- Resetting device info

### Do Not Modify Without Request:
- Timezone
- Language
- Country
- Google status
- Device information
- Location/sensors

## Best Practices

1. **Start with observation** - Always understand current state first
2. **Use node operations** - Prefer structured UI interaction over coordinates
3. **Verify after action** - Confirm each action produced expected result
4. **Handle errors gracefully** - Implement retry logic and fallbacks
5. **Use appropriate delays** - Allow time for UI to update
6. **Follow security guidelines** - Confirm destructive operations

## MCP Integration

For agents that support Model Context Protocol (MCP):

```json
{
  "mcpServers": {
    "vmos": {
      "command": "vmos-mcp-server",
      "args": ["--host", "192.168.1.100"],
      "env": {
        "VMOS_ACCESS_KEY": "your_key",
        "VMOS_SECRET_KEY": "your_secret"
      }
    }
  }
}
```

See the [official VMOS Edge documentation](https://help.vmosedge.com/zh/sdk/agent-api.html) for MCP details.

## Example: Complete Automation Flow

```python
from vmos_api import VMOSClient

async def automate_device(host_ip, db_id):
    client = VMOSClient(host_ip=host_ip)
    control = client.control(db_id=db_id)
    
    # 1. Observe - Check API support
    version = await control.version_info()
    print(f"API Version: {version.version_name}")
    
    # 2. Observe - Get current state
    activity = await control.top_activity()
    print(f"Current: {activity.package_name}")
    
    # 3. Plan & Act - Go to home screen
    await control.press_home()
    await asyncio.sleep(1)
    
    # 4. Plan & Act - Open Settings
    await control.launch_app("com.android.settings")
    await asyncio.sleep(2)
    
    # 5. Observe - Take screenshot
    screenshot = await control.screenshot()
    screenshot.save("settings_screen.png")
    
    # 6. Plan & Act - Navigate to Wi-Fi
    await control.node(
        selector={"text": "Wi-Fi"},
        wait_timeout=5000,
        action="click"
    )
    
    # 7. Verify - Check we're in Wi-Fi settings
    await asyncio.sleep(1)
    ui = await control.dump_compact()
    wifi_toggle = ui.find(text="Wi-Fi")
    
    if wifi_toggle:
        print("Successfully navigated to Wi-Fi settings!")
    
    # 8. Cleanup - Return home
    await control.press_home()
    
    return True
```

## Resources

- [VMOS Titan Skill](../skills/vmos-titan/SKILL.md)
- [Container API Reference](../api-reference/container-api.md)
- [Control API Reference](../api-reference/control-api.md)
- [Official VMOS Documentation](https://help.vmosedge.com/)
