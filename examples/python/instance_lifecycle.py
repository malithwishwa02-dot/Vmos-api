#!/usr/bin/env python3
"""
Instance Lifecycle Management Example

This example demonstrates how to manage the lifecycle of 
VMOS cloud phone instances: create, start, stop, and delete.
"""

import time
import sys
from vmos_api import VMOSClient
from vmos_api.exceptions import VMOSAPIError


def wait_for_ready(client: VMOSClient, db_id: str, timeout: int = 120) -> bool:
    """Wait for instance ROM to be ready."""
    print(f"   Waiting for {db_id} to be ready...", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        try:
            status = client.container.rom_status(db_id)
            if status.get("status") == "ready":
                print(" Ready!")
                return True
        except VMOSAPIError:
            pass
        print(".", end="", flush=True)
        time.sleep(3)
    print(" Timeout!")
    return False


def main():
    client = VMOSClient(host_ip="192.168.1.100")
    
    print("=== Instance Lifecycle Management ===\n")

    # 1. List available images
    print("1. Available images:")
    images = client.host.list_images()
    for img in images[:3]:
        print(f"   - {img.get('name', img)}")
    
    # 2. Create instance
    print("\n2. Creating new instance...")
    try:
        result = client.container.create(
            user_name="lifecycle-demo",
            bool_start=False,  # Don't start immediately
            # image_repository="vcloud_android13_edge",  # Specify image
        )
        db_id = result.db_ids[0]
        print(f"   Created: {db_id}")
    except VMOSAPIError as e:
        print(f"   Failed to create: {e}")
        return

    # 3. Start the instance
    print("\n3. Starting instance...")
    try:
        client.container.start(db_ids=[db_id])
        print(f"   Start command sent")
        
        # Wait for ready
        if not wait_for_ready(client, db_id):
            print("   Instance did not become ready in time")
    except VMOSAPIError as e:
        print(f"   Failed to start: {e}")

    # 4. Get instance details
    print("\n4. Instance details:")
    try:
        detail = client.container.get_detail(db_id)
        print(f"   Name: {detail.user_name}")
        print(f"   Status: {detail.status.value}")
        print(f"   Resolution: {detail.resolution}")
        print(f"   Android: {detail.android_version}")
    except VMOSAPIError as e:
        print(f"   Failed to get details: {e}")

    # 5. Reboot the instance
    print("\n5. Rebooting instance...")
    try:
        client.container.reboot(db_ids=[db_id])
        print("   Reboot command sent")
        time.sleep(5)
        wait_for_ready(client, db_id)
    except VMOSAPIError as e:
        print(f"   Failed to reboot: {e}")

    # 6. Stop the instance
    print("\n6. Stopping instance...")
    try:
        client.container.stop(db_ids=[db_id])
        print("   Stop command sent")
        time.sleep(3)
        
        # Verify stopped
        detail = client.container.get_detail(db_id)
        print(f"   Status: {detail.status.value}")
    except VMOSAPIError as e:
        print(f"   Failed to stop: {e}")

    # 7. Delete the instance (optional - uncomment to run)
    # print("\n7. Deleting instance...")
    # confirm = input("   Are you sure? (yes/no): ")
    # if confirm.lower() == "yes":
    #     try:
    #         client.container.delete(db_ids=[db_id])
    #         print("   Instance deleted")
    #     except VMOSAPIError as e:
    #         print(f"   Failed to delete: {e}")
    # else:
    #     print("   Skipped deletion")

    print("\n=== Lifecycle Demo Complete ===")


if __name__ == "__main__":
    main()
