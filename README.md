# VMOS Pro API

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-4.5+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive SDK and toolkit for the VMOS Cloud/Edge Android Virtual Machine API. This repository provides everything you need to programmatically control and manage VMOS cloud phone instances.

## 🌟 Features

- **Container API SDK** - Manage VMOS Edge cloud phone containers (create, start, stop, delete instances)
- **Control API SDK** - Control individual Android cloud phones (input, screenshots, apps, accessibility)
- **HMAC-SHA256 Authentication** - Secure API authentication implementation
- **Multi-language Support** - Python and TypeScript SDKs
- **AI Agent Integration** - VMOS Titan skill knowledge base for AI-powered automation
- **OpenAPI Specification** - Complete API specification for code generation
- **CLI Tool** - Command-line interface for quick testing and automation
- **Comprehensive Documentation** - Detailed API reference and usage guides

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Container API](#container-api)
- [Control API](#control-api)
- [AI Agent Integration](#ai-agent-integration)
- [Examples](#examples)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Python SDK

```bash
pip install vmos-api
```

Or install from source:

```bash
git clone https://github.com/malithwishwa02-dot/Vmos-api.git
cd Vmos-api
pip install -e src/python
```

### TypeScript SDK

```bash
npm install vmos-api
```

Or install from source:

```bash
git clone https://github.com/malithwishwa02-dot/Vmos-api.git
cd Vmos-api/src/typescript
npm install
npm run build
```

## ⚡ Quick Start

### Python

```python
from vmos_api import VMOSClient

# Initialize client
client = VMOSClient(
    host_ip="192.168.1.100",
    access_key="your_access_key",
    secret_key="your_secret_key"
)

# Create a new Android cloud phone instance
instance = client.container.create(
    user_name="my-device-001",
    bool_start=True,
    image_repository="vcloud_android13_edge"
)
print(f"Created instance: {instance.db_id}")

# Get list of all instances
instances = client.container.list_instances()
for inst in instances:
    print(f"Instance: {inst.db_id}, Status: {inst.status}")

# Start controlling the device
control = client.control(db_id=instance.db_id)

# Take a screenshot
screenshot = control.screenshot()
screenshot.save("device_screenshot.png")

# Click on screen
control.click(x=540, y=960)

# Input text
control.input_text("Hello VMOS!")

# Launch an app
control.launch_app("com.android.settings")
```

### TypeScript

```typescript
import { VMOSClient } from 'vmos-api';

// Initialize client
const client = new VMOSClient({
  hostIp: '192.168.1.100',
  accessKey: 'your_access_key',
  secretKey: 'your_secret_key',
});

// Create a new instance
const instance = await client.container.create({
  userName: 'my-device-001',
  boolStart: true,
  imageRepository: 'vcloud_android13_edge',
});
console.log(`Created instance: ${instance.dbId}`);

// Control the device
const control = client.control(instance.dbId);

// Take a screenshot
const screenshot = await control.screenshot();
await screenshot.save('device_screenshot.png');

// Click and input
await control.click(540, 960);
await control.inputText('Hello VMOS!');
```

## 🔌 API Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VMOS Cloud                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │   Container API      │    │       Control API            │  │
│  │   Port: 18182        │    │       Port: 18185            │  │
│  │                      │    │                              │  │
│  │  • Instance Mgmt     │    │  • Input Control             │  │
│  │  • Lifecycle Ops     │    │  • Screenshot                │  │
│  │  • App Distribution  │    │  • UI Accessibility          │  │
│  │  • Batch Operations  │    │  • App Management            │  │
│  │  • Host Management   │    │  • System Settings           │  │
│  └──────────────────────┘    └──────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Connection Methods

| Scenario | Base URL |
|----------|----------|
| With Container API installed | `http://{host_ip}:18182/android_api/v2/{db_id}` |
| Control API only (LAN mode) | `http://{cloud_ip}:18185/api` |

## 🔐 Authentication

VMOS API uses HMAC-SHA256 signature authentication:

```python
from vmos_api.auth import HMACAuth

auth = HMACAuth(
    access_key="your_access_key",
    secret_key="your_secret_key"
)

# Generate signature for request
headers = auth.sign_request(
    method="POST",
    path="/container_api/v1/create",
    body={"user_name": "test-001"}
)
```

### Required Headers

| Header | Description |
|--------|-------------|
| `Content-Type` | `application/json` |
| `x-date` | ISO 8601 timestamp |
| `x-host` | Target host |
| `Authorization` | HMAC-SHA256 signature |

## 📦 Container API

The Container API manages cloud phone instances on the host machine.

### Instance Management

```python
# Create instance
instance = client.container.create(
    user_name="device-001",
    count=1,
    bool_start=False,
    image_repository="vcloud_android13_edge",
    resolution="1080x1920",
    locale="en_US",
    timezone="America/New_York"
)

# List instances
instances = client.container.list_instances()

# Get instance details
detail = client.container.get_detail(db_id="EDGE0A1B2C3D4E5")

# Batch lifecycle operations
client.container.start(db_ids=["EDGE001", "EDGE002"])
client.container.stop(db_ids=["EDGE001", "EDGE002"])
client.container.reboot(db_ids=["EDGE001"])
client.container.delete(db_ids=["EDGE001"])
```

### App Distribution

```python
# Install APK from URL
client.container.install_apk_from_url(
    db_ids=["EDGE001", "EDGE002"],
    url="https://example.com/app.apk"
)

# Upload and install APK file
client.container.install_apk(
    db_ids=["EDGE001"],
    apk_file="./my_app.apk"
)

# Start/Stop app on multiple devices
client.container.app_start(
    db_ids=["EDGE001", "EDGE002"],
    app="com.example.myapp"
)
```

### Host Management

```python
# Get host system info
system_info = client.host.system_info()

# Get available images
images = client.host.list_images()

# Health check
health = client.host.heartbeat()
```

## 🎮 Control API

The Control API provides fine-grained control over individual Android instances.

### Input Control

```python
control = client.control(db_id="EDGE001")

# Click
control.click(x=540, y=960)
control.multi_click(x=540, y=960, times=2, interval=100)

# Swipe
control.swipe(
    start_x=540, start_y=1500,
    end_x=540, end_y=500,
    duration=300
)

# Bezier curve swipe (more natural)
control.scroll_bezier(
    start_x=540, start_y=1500,
    end_x=540, end_y=500,
    duration=500
)

# Text input
control.input_text("Hello World!")

# Key events
control.key_event(key_code=4)  # BACK key
```

### Observation

```python
# Screenshot
screenshot = control.screenshot()
screenshot.save("screen.png")

# Get display info
display = control.display_info()
print(f"Screen: {display.width}x{display.height}")

# Dump UI hierarchy (compact)
ui_tree = control.dump_compact()

# Get top activity
activity = control.top_activity()
print(f"Current: {activity.package_name}/{activity.class_name}")
```

### UI Node Operations

```python
# Find and click a node by text
control.node(
    selector={"text": "Settings", "clickable": True},
    action="click"
)

# Find node by resource ID and wait
control.node(
    selector={"resource_id": "com.example:id/button"},
    wait_timeout=5000,
    action="click"
)

# Input text into a field
control.node(
    selector={"class_name": "android.widget.EditText"},
    action="set_text",
    action_params={"text": "My input"}
)

# Scroll a list
control.node(
    selector={"scrollable": True},
    action="scroll_forward"
)
```

### App Management

```python
# Launch app (with permission grants)
control.launch_app(
    package_name="com.example.app",
    grant_all_permissions=True
)

# Start specific activity
control.start_activity(
    package_name="com.android.chrome",
    action="android.intent.action.VIEW",
    data="https://www.google.com"
)

# Install from URL
control.install_uri_sync(uri="https://example.com/app.apk")

# Get installed apps
apps = control.list_packages(type="user")

# Uninstall app
control.uninstall(package_name="com.example.app")
```

### System Operations

```python
# Execute shell command
result = control.shell(command="ls /sdcard", as_root=False)

# Clipboard operations
control.clipboard_set(text="Copied text")
text = control.clipboard_get()

# System settings
control.settings_put(namespace="system", key="screen_brightness", value="128")
value = control.settings_get(namespace="system", key="screen_brightness")

# Google services
control.set_google_enabled(enabled=True)
control.reset_gaid()
```

## 🤖 AI Agent Integration

This repository includes VMOS Titan - a comprehensive knowledge base for AI agents to control VMOS cloud phones.

### Installing Skills

```bash
npx skills add https://github.com/malithwishwa02-dot/Vmos-api --skill vmos-titan
```

### Usage with AI Agents

The VMOS Titan skill provides structured knowledge for:

- **Connection Discovery** - Auto-detect connection methods
- **Capability Detection** - Query available APIs
- **Observe-Plan-Act-Verify** - Structured automation workflow
- **Error Recovery** - Handle common failure scenarios

See [AI Agent Guide](docs/guides/ai-agent-integration.md) for detailed integration instructions.

## 📚 Examples

### Complete Automation Example

```python
from vmos_api import VMOSClient
import time

client = VMOSClient(host_ip="192.168.1.100")

# Create and start a new device
instance = client.container.create(
    user_name="automation-device",
    bool_start=True,
    image_repository="vcloud_android13_edge"
)

# Wait for device to be ready
while True:
    status = client.container.get_detail(instance.db_id)
    if status.rom_status == "ready":
        break
    time.sleep(2)

# Start controlling
control = client.control(db_id=instance.db_id)

# Verify API support
version = control.version_info()
print(f"API Version: {version.version_name}")

# Take initial screenshot
control.screenshot().save("initial.png")

# Open Settings
control.launch_app("com.android.settings")
time.sleep(2)

# Find and click WiFi
control.node(
    selector={"text": "Wi-Fi"},
    wait_timeout=5000,
    action="click"
)

# Take final screenshot
control.screenshot().save("wifi_settings.png")

# Cleanup
client.container.stop(db_ids=[instance.db_id])
```

### Browser Automation Example

```python
control = client.control(db_id="EDGE001")

# Open browser with URL
control.start_activity(
    package_name="mark.via",  # Via browser preferred
    action="android.intent.action.VIEW",
    data="https://www.google.com/search?q=VMOS+Cloud"
)

time.sleep(3)

# Get page content
ui = control.dump_compact()

# Extract search results
for node in ui.find_all({"class_name": "android.widget.TextView"}):
    print(node.text)
```

More examples in [examples/](examples/).

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Container API Reference](docs/api-reference/container-api.md) | Complete Container API documentation |
| [Control API Reference](docs/api-reference/control-api.md) | Complete Control API documentation |
| [Authentication Guide](docs/guides/authentication.md) | HMAC-SHA256 authentication details |
| [Getting Started](docs/guides/getting-started.md) | Step-by-step setup guide |
| [AI Agent Integration](docs/guides/ai-agent-integration.md) | Using with AI agents |
| [Troubleshooting](docs/guides/troubleshooting.md) | Common issues and solutions |

## 🏗️ Project Structure

```
Vmos-api/
├── src/
│   ├── python/                 # Python SDK
│   │   └── vmos_api/
│   │       ├── auth/           # Authentication
│   │       ├── container/      # Container API client
│   │       └── control/        # Control API client
│   └── typescript/             # TypeScript SDK
│       └── src/
│           ├── auth/           # Authentication
│           ├── container/      # Container API client
│           └── control/        # Control API client
├── docs/
│   ├── api-reference/          # API documentation
│   ├── guides/                 # Usage guides
│   └── examples/               # Example documentation
├── examples/
│   ├── python/                 # Python examples
│   └── typescript/             # TypeScript examples
├── tests/
│   ├── python/                 # Python tests
│   └── typescript/             # TypeScript tests
├── openapi/                    # OpenAPI specifications
├── skills/
│   └── vmos-titan/             # AI agent skill knowledge
└── cli/                        # CLI tool
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/malithwishwa02-dot/Vmos-api.git
cd Vmos-api

# Python development
cd src/python
pip install -e ".[dev]"

# TypeScript development
cd src/typescript
npm install
npm run dev
```

### Running Tests

```bash
# Python tests
cd src/python
pytest

# TypeScript tests
cd src/typescript
npm test
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [VMOS Edge Skills](https://github.com/vmos-dev/vmos-edge-skills) - Official VMOS Edge API skills
- [VMOSCloud](https://www.vmoscloud.com/) - VMOS Cloud service
- [VMOS Documentation](https://help.vmosedge.com/) - Official documentation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/malithwishwa02-dot/Vmos-api/issues)
- **Documentation**: [Online Docs](docs/)
- **Official VMOS Support**: [help.vmosedge.com](https://help.vmosedge.com/)

---

Made with ❤️ for the VMOS community
