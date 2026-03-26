# Getting Started with VMOS API

This guide will help you get started with the VMOS API SDK to manage and control Android cloud phone instances.

## Prerequisites

- Python 3.8+ or Node.js 16+
- Access to a VMOS Edge host or VMOS Cloud account
- API credentials (access_key and secret_key) if required

## Installation

### Python

```bash
pip install vmos-api
```

Or install from source:

```bash
git clone https://github.com/malithwishwa02-dot/Vmos-api.git
cd Vmos-api/src/python
pip install -e .
```

### TypeScript/Node.js

```bash
npm install vmos-api
```

## Basic Setup

### Python

```python
from vmos_api import VMOSClient

# Connect to VMOS Edge host
client = VMOSClient(
    host_ip="192.168.1.100",  # Your VMOS Edge host IP
    access_key="your_access_key",  # Optional
    secret_key="your_secret_key",  # Optional
)

# Verify connection
try:
    health = client.host.heartbeat()
    print("Connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")
```

### TypeScript

```typescript
import { VMOSClient } from 'vmos-api';

const client = new VMOSClient({
  hostIp: '192.168.1.100',
  accessKey: 'your_access_key',
  secretKey: 'your_secret_key',
});

// Verify connection
const health = await client.host.heartbeat();
console.log('Connected successfully!');
```

## Connection Methods

### Method 1: Host IP (Container API + Control API)

Use this when connecting to a VMOS Edge host machine.

```python
client = VMOSClient(host_ip="192.168.1.100")

# Container API is available
instances = client.container.list_instances()

# Control API requires db_id
control = client.control(db_id="EDGE001")
```

### Method 2: Cloud IP (Direct Control API)

Use this for direct connection to a running cloud phone (LAN mode required).

```python
client = VMOSClient(cloud_ip="192.168.1.101")

# Only Control API is available
control = client.control()
version = control.version_info()
```

### Method 3: Auto-detect Local

The SDK can auto-detect if running on a VMOS Edge host.

```python
# Will auto-detect 127.0.0.1 if cbs_go process is running
client = VMOSClient(auto_detect=True)
```

## Your First Instance

### Step 1: Create an Instance

```python
from vmos_api import VMOSClient

client = VMOSClient(host_ip="192.168.1.100")

# Create a new Android cloud phone
result = client.container.create(
    user_name="my-first-device",
    bool_start=True,  # Start immediately
    image_repository="vcloud_android13_edge",  # Android 13 image
)

print(f"Created instance: {result.db_ids}")
db_id = result.db_ids[0]
```

### Step 2: Wait for Instance to be Ready

```python
import time

# Poll until ROM is ready
while True:
    status = client.container.rom_status(db_id)
    if status.get("status") == "ready":
        print("Instance is ready!")
        break
    print("Waiting for instance...")
    time.sleep(5)
```

### Step 3: Control the Instance

```python
# Get control client for the instance
control = client.control(db_id=db_id)

# Verify API support
version = control.version_info()
print(f"Control API version: {version.version_name}")

# Take a screenshot
screenshot = control.screenshot()
screenshot.save("my_first_screenshot.png")
print("Screenshot saved!")

# Get screen dimensions
display = control.display_info()
print(f"Screen: {display.width}x{display.height}")
```

### Step 4: Interact with the Device

```python
# Click in the center of the screen
center_x = display.width // 2
center_y = display.height // 2
control.click(center_x, center_y)

# Swipe up
control.swipe(
    start_x=center_x,
    start_y=center_y + 300,
    end_x=center_x,
    end_y=center_y - 300,
    duration=300
)

# Input text
control.input_text("Hello VMOS!")

# Press back button
control.press_back()
```

### Step 5: Open an App

```python
# Launch Settings app
control.launch_app(
    package_name="com.android.settings",
    grant_all_permissions=True
)

# Wait for app to load
time.sleep(2)

# Find and click WiFi
control.node(
    selector={"text": "Wi-Fi"},
    wait_timeout=5000,
    action="click"
)

# Verify we're in WiFi settings
activity = control.top_activity()
print(f"Current: {activity.package_name}")
```

### Step 6: Clean Up

```python
# Stop the instance
client.container.stop(db_ids=[db_id])

# Or delete it
# client.container.delete(db_ids=[db_id])
```

## Complete Example

```python
from vmos_api import VMOSClient
import time

def main():
    # Connect to VMOS
    client = VMOSClient(host_ip="192.168.1.100")
    
    # Check host health
    health = client.host.heartbeat()
    print(f"Host status: {health}")
    
    # List existing instances
    instances = client.container.list_instances()
    print(f"Found {len(instances)} instances")
    
    for inst in instances:
        print(f"  - {inst.db_id}: {inst.user_name} ({inst.status})")
    
    # Create a new instance
    result = client.container.create(
        user_name="demo-device",
        bool_start=True,
    )
    db_id = result.db_ids[0]
    print(f"Created: {db_id}")
    
    # Wait for ready
    print("Waiting for instance to be ready...")
    for _ in range(60):
        status = client.container.rom_status(db_id)
        if status.get("status") == "ready":
            break
        time.sleep(2)
    
    # Control the device
    control = client.control(db_id=db_id)
    
    # Take screenshot
    screenshot = control.screenshot()
    screenshot.save(f"{db_id}_screenshot.png")
    
    # Open Chrome
    control.start_activity(
        package_name="com.android.chrome",
        action="android.intent.action.VIEW",
        data="https://www.google.com"
    )
    time.sleep(3)
    
    # Take another screenshot
    control.screenshot().save(f"{db_id}_chrome.png")
    
    # Stop instance
    client.container.stop(db_ids=[db_id])
    print("Done!")

if __name__ == "__main__":
    main()
```

## What's Next?

- [Container API Reference](../api-reference/container-api.md) - Manage instances
- [Control API Reference](../api-reference/control-api.md) - Control devices
- [Authentication Guide](./authentication.md) - Secure your API calls
- [AI Agent Integration](./ai-agent-integration.md) - Use with AI agents
- [Examples](../../examples/) - More code examples

## Troubleshooting

### Connection Refused

```
VMOSConnectionError: Connection failed: [Errno 111] Connection refused
```

- Verify the host IP is correct
- Check that VMOS Edge service is running
- Ensure port 18182 is accessible

### Instance Not Found

```
VMOSInstanceNotFoundError: Instance not found: EDGE001
```

- Verify the db_id is correct
- Check if instance was deleted
- Use `list_instances()` to see available instances

### API Not Supported

```
VMOSAPIError: Unknown error (code: 404)
```

- The endpoint may not be available on this device
- Use `version_info()` to check supported APIs
- Use `list_actions()` to discover available endpoints

### Timeout

```
VMOSTimeoutError: Request timed out
```

- Increase timeout: `VMOSClient(timeout=60.0)`
- Check network connectivity
- Verify instance is running

## Getting Help

- [GitHub Issues](https://github.com/malithwishwa02-dot/Vmos-api/issues)
- [Official VMOS Documentation](https://help.vmosedge.com/)
