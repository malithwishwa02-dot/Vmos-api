# VMOS Container API Reference

The Container API manages VMOS Edge cloud phone instances at the host level. It runs on port `18182` by default.

## Base URL

```
http://{host_ip}:18182
```

## Authentication

See [Authentication Guide](../guides/authentication.md) for HMAC-SHA256 signature details.

---

## Instance Management

### Create Instance

Create new cloud phone instance(s).

**Endpoint:** `POST /container_api/v1/create`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_name` | string | Yes | Display name for the instance |
| `count` | integer | No | Number of instances to create (default: 1) |
| `bool_start` | boolean | No | Start after creation (default: false) |
| `bool_macvlan` | boolean | No | Use macvlan networking |
| `macvlan_network` | string | No | Macvlan network name |
| `macvlan_start_ip` | string | No | Starting IP for macvlan |
| `image_repository` | string | No | Image to use |
| `adiID` | integer | No | ADI template ID |
| `resolution` | string | No | Screen resolution (e.g., "1080x1920") |
| `locale` | string | No | System locale (e.g., "en_US") |
| `timezone` | string | No | System timezone |
| `country` | string | No | Country code |
| `userProp` | object | No | Custom user properties |
| `cert_hash` | string | No | Certificate hash |
| `cert_content` | string | No | Certificate content |

**Example Request:**

```json
{
  "user_name": "test-001",
  "bool_start": false,
  "image_repository": "vcloud_android13_edge_20250925011125",
  "adiID": 1039
}
```

**Response:**

```json
{
  "code": 200,
  "data": {
    "db_ids": ["EDGE0A1B2C3D4E5"]
  },
  "msg": "OK"
}
```

---

### List Instances

Get list of all instances.

**Endpoint:** `POST /container_api/v1/get_db` (preferred) or `GET /container_api/v1/get_db`

**Note:** Try POST first; some hosts require it. Fall back to GET if POST fails.

**Response:**

```json
{
  "code": 200,
  "data": [
    {
      "db_id": "EDGE0A1B2C3D4E5",
      "user_name": "test-001",
      "status": "running",
      "cloud_ip": "192.168.1.101"
    }
  ],
  "msg": "OK"
}
```

---

### List Instance Names

Get simplified list of instance IDs and names.

**Endpoint:** `GET /container_api/v1/list_names`

**Response:**

```json
{
  "code": 200,
  "data": [
    {
      "db_id": "EDGE0A1B2C3D4E5",
      "user_name": "test-001",
      "adb": "192.168.1.100:5555"
    }
  ],
  "msg": "OK"
}
```

---

### Get Instance Detail

Get detailed information about a specific instance.

**Endpoint:** `GET /container_api/v1/get_android_detail/{db_id}`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `db_id` | string | Instance database ID |

**Response:**

```json
{
  "code": 200,
  "data": {
    "db_id": "EDGE0A1B2C3D4E5",
    "user_name": "test-001",
    "status": "running",
    "rom_status": "ready",
    "android_version": "13",
    "resolution": "1080x1920",
    "locale": "en_US",
    "timezone": "America/New_York"
  },
  "msg": "OK"
}
```

---

### Get Screenshot

Get screenshot of an instance.

**Endpoint:** `GET /container_api/v1/screenshots/{db_id}`

**Response:** Image bytes (PNG/JPEG)

---

### Get ADB Command

Get ADB connection command for an instance.

**Endpoint:** `GET /container_api/v1/adb_start/{db_id}`

**Response:**

```json
{
  "code": 200,
  "data": {
    "adb_command": "adb connect 192.168.1.100:5555"
  },
  "msg": "OK"
}
```

---

### Check ROM Status

Check if ROM is ready for an instance.

**Endpoint:** `GET /container_api/v1/rom_status/{db_id}`

**Response:**

```json
{
  "code": 200,
  "data": {
    "status": "ready"
  },
  "msg": "OK"
}
```

---

## Lifecycle Operations

### Start Instances

**Endpoint:** `POST /container_api/v1/run`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5", "EDGE6F7G8H9I0J1"]
}
```

---

### Stop Instances

**Endpoint:** `POST /container_api/v1/stop`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5", "EDGE6F7G8H9I0J1"]
}
```

---

### Reboot Instances

**Endpoint:** `POST /container_api/v1/reboot`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5"]
}
```

---

### Reset Instances

Reset instances to initial state.

**Endpoint:** `POST /container_api/v1/reset`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5"]
}
```

**⚠️ Warning:** This will erase all data on the instance!

---

### Delete Instances

Permanently delete instances.

**Endpoint:** `POST /container_api/v1/delete`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5"]
}
```

**⚠️ Warning:** This action is irreversible!

---

### Rename Instance

**Endpoint:** `GET /container_api/v1/rename/{db_id}/{new_user_name}`

---

### Clone Instance

**Endpoint:** `POST /container_api/v1/clone`

**Request Body:**

```json
{
  "db_id": "EDGE0A1B2C3D4E5",
  "count": 2
}
```

---

### Clone Status

**Endpoint:** `GET /container_api/v1/clone_status`

---

### Replace Device Info (One-Key New Device)

Generate new device fingerprint.

**Endpoint:** `POST /container_api/v1/replace_devinfo`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5"],
  "userProp": {
    "custom_key": "value"
  }
}
```

---

### Upgrade Image

Upgrade instances to a new image.

**Endpoint:** `POST /container_api/v1/upgrade_image`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5"],
  "image_repository": "vcloud_android13_edge_new"
}
```

---

## App Management

### Get Installed Apps

**Endpoint:** `GET /android_api/v1/app_get/{db_id}`

---

### Start App (Batch)

**Endpoint:** `POST /android_api/v1/app_start`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5", "EDGE6F7G8H9I0J1"],
  "app": "com.tencent.mm"
}
```

---

### Stop App (Batch)

**Endpoint:** `POST /android_api/v1/app_stop`

**Request Body:**

```json
{
  "db_ids": ["EDGE0A1B2C3D4E5"],
  "app": "com.tencent.mm"
}
```

---

### Install APK from URL (Batch)

**Endpoint:** `POST /android_api/v1/install_apk_from_url_batch`

**Request Body:**

```json
{
  "url": "https://example.com/app.apk",
  "db_ids": "EDGE0A1B2C3D4E5,EDGE6F7G8H9I0J1"
}
```

**Note:** `db_ids` is a comma-separated string, not an array.

---

### Upload File (Batch)

**Endpoint:** `POST /android_api/v1/upload_file_android_batch`

**Content-Type:** `multipart/form-data`

---

### Upload File from URL (Batch)

**Endpoint:** `POST /android_api/v1/upload_file_from_url_batch`

**Request Body:**

```json
{
  "url": "https://example.com/file.zip",
  "db_ids": "EDGE0A1B2C3D4E5",
  "target_path": "/sdcard/Download/"
}
```

---

## Device Control

### Execute Shell Command

**Endpoint:** `POST /android_api/v1/shell/{db_id}`

**Request Body:**

```json
{
  "command": "ls /sdcard"
}
```

---

### Inject GPS Location

**Endpoint:** `POST /android_api/v1/gps_inject/{db_id}`

**Request Body:**

```json
{
  "latitude": 37.7749,
  "longitude": -122.4194
}
```

---

### Set Timezone

**Endpoint:** `POST /android_api/v1/timezone_set/{db_id}`

**Request Body:**

```json
{
  "timezone": "America/New_York"
}
```

---

### Set Country

**Endpoint:** `POST /android_api/v1/country_set/{db_id}`

**Request Body:**

```json
{
  "country": "US"
}
```

---

### Set Language

**Endpoint:** `POST /android_api/v1/language_set/{db_id}`

**Request Body:**

```json
{
  "language": "en"
}
```

---

### Get Locale Info

**Endpoint:** `GET /android_api/v1/get_timezone_locale/{db_id}`

---

## Host Management

### Heartbeat

Check host health status.

**Endpoint:** `GET /v1/heartbeat`

---

### System Info

Get CPU, memory, disk, swap information.

**Endpoint:** `GET /v1/systeminfo`

---

### Hardware Configuration

**Endpoint:** `GET /v1/get_hardware_cfg`

---

### Network Info

**Endpoint:** `GET /v1/net_info`

---

### List Images

**Endpoint:** `GET /v1/get_img_list`

---

### Prune Images

Clean up unused images.

**Endpoint:** `GET /v1/prune_images`

---

### Import Image

**Endpoint:** `POST /v1/import_image`

**Content-Type:** `multipart/form-data`

---

### Enable/Disable Swap

**Endpoint:** `GET /v1/swap/{enable}` where enable is `1` or `0`

---

### Reboot Host

**Endpoint:** `GET /v1/reboot_for_arm`

**⚠️ Warning:** This will restart the entire host system!

---

### Shutdown Host

**Endpoint:** `GET /v1/shutdown`

**⚠️ Warning:** This will power off the host system!

---

### Reset Host

**Endpoint:** `GET /v1/reset`

**⚠️ Warning:** This will erase all data and configurations!

---

### ADI Management

**List ADI Templates:** `GET /v1/get_adi_list`

**Import ADI:** `POST /v1/import_adi` (multipart/form-data)

---

## GMS Control

### Enable GMS (All Instances)

**Endpoint:** `GET /container_api/v1/gms_start`

---

### Disable GMS (All Instances)

**Endpoint:** `GET /container_api/v1/gms_stop`

---

## Storage & Maintenance

### Storage Status

**Endpoint:** `GET /storage/status`

---

### Format SSD

**Endpoint:** `POST /storage/format`

**⚠️ Warning:** This will erase all data on the SSD!

---

### Import Certificate (File)

**Endpoint:** `POST /certificate_manage/file_import_cert`

**Content-Type:** `multipart/form-data`

---

### Import Certificate (Content)

**Endpoint:** `POST /certificate_manage/content_import_cert`

---

### Update CBS

**Endpoint:** `POST /v1/update_cbs`

**Content-Type:** `multipart/form-data`

---

### Update Kernel

**Endpoint:** `POST /v1/update_kernel`

**Content-Type:** `multipart/form-data`

---

## Logs

### Recent Logs

**Endpoint:** `GET /interface_logs/recent`

---

### Log Details

**Endpoint:** `GET /interface_logs/detail`

---

### Log Statistics

**Endpoint:** `GET /interface_logs/stats`

---

## Instance Status Values

| Status | Description |
|--------|-------------|
| `creating` | Instance is being created |
| `starting` | Instance is starting up |
| `running` | Instance is running |
| `stopping` | Instance is stopping |
| `stopped` | Instance is stopped |
| `rebooting` | Instance is rebooting |
| `rebuilding` | Instance is rebuilding |
| `renewing` | Instance is renewing |
| `deleting` | Instance is being deleted |

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Internal Server Error |
