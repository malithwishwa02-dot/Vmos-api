#!/usr/bin/env python3
"""
Basic VMOS API Usage Example

This example demonstrates the basic usage of the VMOS API SDK
for managing and controlling Android cloud phone instances.
"""

import time
from vmos_api import VMOSClient


def main():
    # Initialize client
    # Replace with your actual host IP and credentials
    client = VMOSClient(
        host_ip="192.168.1.100",
        # access_key="your_access_key",  # Optional
        # secret_key="your_secret_key",  # Optional
    )

    print("=== VMOS API Basic Example ===\n")

    # Check host health
    print("1. Checking host health...")
    try:
        health = client.host.heartbeat()
        print(f"   Host is healthy: {health}")
    except Exception as e:
        print(f"   Failed to connect: {e}")
        return

    # Get system info
    print("\n2. Getting system info...")
    system_info = client.host.system_info()
    print(f"   CPU: {system_info.get('cpu_usage', 'N/A')}%")
    print(f"   Memory: {system_info.get('memory_used', 'N/A')}")

    # List existing instances
    print("\n3. Listing instances...")
    instances = client.container.list_instances()
    print(f"   Found {len(instances)} instances:")
    for inst in instances[:5]:  # Show first 5
        print(f"   - {inst.db_id}: {inst.user_name} ({inst.status.value})")

    # Create a new instance (optional - uncomment to run)
    # print("\n4. Creating new instance...")
    # result = client.container.create(
    #     user_name="demo-device",
    #     bool_start=True,
    # )
    # print(f"   Created: {result.db_ids}")

    # If there are running instances, control one
    running = [i for i in instances if i.status.value == "running"]
    if running:
        print(f"\n4. Controlling instance: {running[0].db_id}")
        db_id = running[0].db_id
        
        control = client.control(db_id=db_id)
        
        # Get version info
        version = control.version_info()
        print(f"   API Version: {version.version_name}")
        
        # Get display info
        display = control.display_info()
        print(f"   Screen: {display.width}x{display.height}")
        
        # Get current activity
        activity = control.top_activity()
        print(f"   Current app: {activity.package_name}")
        
        # Take screenshot
        print("   Taking screenshot...")
        screenshot = control.screenshot()
        filename = f"/tmp/{db_id}_screenshot.png"
        screenshot.save(filename)
        print(f"   Saved to: {filename}")
    else:
        print("\n4. No running instances to control")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
