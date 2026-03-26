#!/usr/bin/env python3
"""
Device Control Example

This example demonstrates fine-grained control of an Android
cloud phone instance using the Control API.
"""

import time
from vmos_api import VMOSClient


def main():
    # Connect to a running instance
    client = VMOSClient(host_ip="192.168.1.100")
    
    # Get first running instance
    instances = client.container.list_instances()
    running = [i for i in instances if i.status.value == "running"]
    
    if not running:
        print("No running instances found!")
        print("Create and start an instance first.")
        return
    
    db_id = running[0].db_id
    print(f"=== Device Control: {db_id} ===\n")
    
    # Get control client
    control = client.control(db_id=db_id)
    
    # 1. Check API version and capabilities
    print("1. API Information:")
    version = control.version_info()
    print(f"   Version: {version.version_name}")
    print(f"   Supported APIs: {len(version.supported_list)}")
    
    # 2. Get display info
    print("\n2. Display Information:")
    display = control.display_info()
    print(f"   Resolution: {display.width}x{display.height}")
    print(f"   Rotation: {display.rotation}")
    
    center_x = display.width // 2
    center_y = display.height // 2
    
    # 3. Take screenshot
    print("\n3. Taking Screenshot...")
    screenshot = control.screenshot()
    screenshot.save("/tmp/device_screen.png")
    print("   Saved to /tmp/device_screen.png")
    
    # 4. Get UI hierarchy
    print("\n4. UI Hierarchy:")
    ui = control.dump_compact()
    if ui.root:
        print(f"   Root class: {ui.root.class_name}")
        print(f"   Children: {len(ui.root.children)}")
    
    # 5. Get current activity
    print("\n5. Current Activity:")
    activity = control.top_activity()
    print(f"   Package: {activity.package_name}")
    print(f"   Activity: {activity.class_name}")
    
    # 6. Input controls
    print("\n6. Input Controls:")
    
    # Click center
    print("   Clicking center of screen...")
    control.click(center_x, center_y)
    time.sleep(0.5)
    
    # Swipe up
    print("   Swiping up...")
    control.swipe(
        start_x=center_x,
        start_y=center_y + 300,
        end_x=center_x,
        end_y=center_y - 300,
        duration=300
    )
    time.sleep(0.5)
    
    # Press home
    print("   Pressing HOME...")
    control.press_home()
    time.sleep(1)
    
    # 7. Launch Settings app
    print("\n7. Launching Settings...")
    control.launch_app(
        package_name="com.android.settings",
        grant_all_permissions=True
    )
    time.sleep(2)
    
    # Verify
    activity = control.top_activity()
    print(f"   Current: {activity.package_name}")
    
    # 8. Use node selector
    print("\n8. UI Node Operations:")
    
    # Find WiFi text
    node = control.node(
        selector={"text": "Wi-Fi"},
        wait_timeout=3000
    )
    if node:
        print(f"   Found 'Wi-Fi' at: {node.bounds}")
        
        # Click it
        print("   Clicking 'Wi-Fi'...")
        control.node(
            selector={"text": "Wi-Fi"},
            action="click"
        )
        time.sleep(1)
    else:
        print("   'Wi-Fi' not found on screen")
    
    # 9. Take final screenshot
    print("\n9. Final Screenshot:")
    screenshot = control.screenshot()
    screenshot.save("/tmp/device_final.png")
    print("   Saved to /tmp/device_final.png")
    
    # 10. Go back home
    print("\n10. Returning home...")
    control.press_home()
    
    print("\n=== Device Control Complete ===")


if __name__ == "__main__":
    main()
