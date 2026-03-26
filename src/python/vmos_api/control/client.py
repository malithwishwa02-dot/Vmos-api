"""
Control API Client

This module provides the client for controlling individual VMOS Android instances
through the Control API.
"""

import json
from typing import Optional, List, Dict, Any, Union
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from ..auth.hmac_auth import HMACAuth, NoAuth
from ..exceptions import VMOSAPIError, VMOSConnectionError, VMOSTimeoutError
from .models import (
    VersionInfo,
    DisplayInfo,
    TopActivity,
    UINode,
    Screenshot,
    DumpCompact,
    NodeSelector,
    NodeAction,
    PackageInfo,
    ActionInfo,
)


class ControlClient:
    """
    Client for VMOS Control API.
    
    Provides fine-grained control over individual Android instances:
    - Input control (click, swipe, text)
    - Observation (screenshot, UI dump)
    - UI node operations
    - App management
    - System operations
    
    Example:
        control = ControlClient(
            base_url="http://192.168.1.100:18182/android_api/v2/EDGE001",
            auth=HMACAuth(access_key, secret_key)
        )
        
        # Take screenshot
        screenshot = control.screenshot()
        screenshot.save("screen.png")
        
        # Click on screen
        control.click(540, 960)
        
        # Input text
        control.input_text("Hello!")
    """

    def __init__(
        self,
        base_url: str,
        auth: Union[HMACAuth, NoAuth],
        timeout: float = 30.0,
    ):
        """
        Initialize Control API client.
        
        Args:
            base_url: Base URL for the Control API (including db_id if host-routed)
            auth: Authentication handler
            timeout: Request timeout in seconds
        """
        self._base_url = base_url.rstrip("/")
        self._auth = auth
        self._timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], bytes]:
        """
        Make an API request.
        
        Args:
            method: HTTP method
            path: API endpoint path
            body: Request body
            raw_response: If True, return raw bytes instead of JSON
            
        Returns:
            Parsed JSON response or raw bytes
        """
        url = f"{self._base_url}{path}"
        headers = self._auth.sign_request(method=method, url=url, body=body)
        
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        
        request = Request(url, data=data, headers=headers, method=method)
        
        try:
            with urlopen(request, timeout=self._timeout) as response:
                response_bytes = response.read()
                
                if raw_response:
                    return response_bytes
                
                response_data = json.loads(response_bytes.decode("utf-8"))
                
                # Check for API error
                code = response_data.get("code")
                if code is not None and code != 200:
                    raise VMOSAPIError(
                        message=response_data.get("msg", "Unknown error"),
                        code=code,
                        request_id=response_data.get("request_id"),
                        endpoint=path,
                    )
                
                return response_data
                
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_data = json.loads(error_body)
                raise VMOSAPIError(
                    message=error_data.get("msg", str(e)),
                    code=e.code,
                    endpoint=path,
                )
            except json.JSONDecodeError:
                raise VMOSAPIError(message=str(e), code=e.code, endpoint=path)
        except URLError as e:
            raise VMOSConnectionError(message=f"Connection failed: {str(e.reason)}")
        except TimeoutError:
            raise VMOSTimeoutError(timeout=self._timeout, endpoint=path)

    # ==================== Base / Discovery ====================

    def version_info(self) -> VersionInfo:
        """
        Get API version information.
        
        Use this to verify API support and discover available endpoints.
        
        Returns:
            VersionInfo object
            
        Example:
            version = control.version_info()
            print(f"Version: {version.version_name}")
            print(f"Supported: {version.supported_list}")
        """
        response = self._request("GET", "/base/version_info", None)
        return VersionInfo.from_api_response(response.get("data", response))

    def list_actions(
        self,
        paths: Optional[List[str]] = None,
        detail: bool = False,
    ) -> List[ActionInfo]:
        """
        Get list of available API actions.
        
        Args:
            paths: Specific paths to query (optional)
            detail: Include detailed parameter info
            
        Returns:
            List of ActionInfo objects
        """
        body: Dict[str, Any] = {"detail": detail}
        if paths:
            body["paths"] = paths
        
        response = self._request("POST", "/base/list_action", body)
        actions = []
        for item in response.get("data", []):
            actions.append(ActionInfo.from_api_response(item))
        return actions

    def sleep(self, duration_ms: int) -> Dict[str, Any]:
        """
        Pause execution for specified duration.
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            Operation result
        """
        return self._request("POST", "/base/sleep", {"duration": duration_ms})

    # ==================== Observation ====================

    def display_info(self) -> DisplayInfo:
        """
        Get screen display information.
        
        Returns:
            DisplayInfo object with screen dimensions
            
        Example:
            display = control.display_info()
            print(f"Screen: {display.width}x{display.height}")
        """
        response = self._request("GET", "/display/info", None)
        return DisplayInfo.from_api_response(response.get("data", response))

    def screenshot(self, format: str = "png") -> Screenshot:
        """
        Capture screenshot of the device screen.
        
        Args:
            format: Image format (png, jpeg)
            
        Returns:
            Screenshot object
            
        Example:
            screenshot = control.screenshot()
            screenshot.save("screen.png")
        """
        # Try different screenshot endpoints
        try:
            if format == "png":
                response = self._request("GET", "/screenshot/format", None, raw_response=True)
                return Screenshot.from_bytes(response, "png")
            else:
                response = self._request("GET", "/screenshot/raw", None, raw_response=True)
                return Screenshot.from_bytes(response, format)
        except VMOSAPIError:
            # Fallback to data_url endpoint
            response = self._request("GET", "/screenshot/data_url", None)
            data_url = response.get("data", {}).get("data_url", "")
            return Screenshot.from_base64(data_url, format)

    def screenshot_data_url(self) -> str:
        """
        Get screenshot as data URL.
        
        Returns:
            Base64 data URL string
        """
        response = self._request("GET", "/screenshot/data_url", None)
        return response.get("data", {}).get("data_url", "")

    def dump_compact(self) -> DumpCompact:
        """
        Get compact UI hierarchy dump.
        
        Use this for efficient text-based UI analysis.
        
        Returns:
            DumpCompact object with UI tree
            
        Example:
            ui = control.dump_compact()
            button = ui.find(text="Submit")
            if button:
                print(f"Button at: {button.center}")
        """
        response = self._request("GET", "/accessibility/dump_compact", None)
        return DumpCompact.from_api_response(response.get("data", response))

    def top_activity(self) -> TopActivity:
        """
        Get the current foreground activity.
        
        Returns:
            TopActivity object
            
        Example:
            activity = control.top_activity()
            print(f"Current: {activity.package_name}/{activity.class_name}")
        """
        response = self._request("GET", "/activity/top_activity", None)
        return TopActivity.from_api_response(response.get("data", response))

    # ==================== UI Node Operations ====================

    def node(
        self,
        selector: Union[NodeSelector, Dict[str, Any]],
        wait_timeout: int = 0,
        wait_interval: int = 500,
        action: Optional[Union[NodeAction, str]] = None,
        action_params: Optional[Dict[str, Any]] = None,
    ) -> Optional[UINode]:
        """
        Find and optionally interact with a UI node.
        
        Args:
            selector: Node selector (NodeSelector or dict)
            wait_timeout: Timeout in ms to wait for node
            wait_interval: Polling interval in ms
            action: Action to perform on found node
            action_params: Parameters for the action
            
        Returns:
            UINode if found, None otherwise
            
        Example:
            # Find and click
            control.node(
                selector={"text": "Settings"},
                action="click"
            )
            
            # Wait and click
            control.node(
                selector={"resource_id": "com.example:id/btn"},
                wait_timeout=5000,
                action="click"
            )
            
            # Input text
            control.node(
                selector={"class_name": "android.widget.EditText"},
                action="set_text",
                action_params={"text": "Hello"}
            )
        """
        if isinstance(selector, NodeSelector):
            selector_dict = selector.to_dict()
        else:
            selector_dict = selector
        
        body: Dict[str, Any] = {"selector": selector_dict}
        
        if wait_timeout > 0:
            body["wait_timeout"] = wait_timeout
            body["wait_interval"] = wait_interval
        
        if action:
            if isinstance(action, NodeAction):
                body["action"] = action.value
            else:
                body["action"] = action
        
        if action_params:
            body["action_params"] = action_params
        
        response = self._request("POST", "/accessibility/node", body)
        data = response.get("data")
        if data:
            return UINode.from_api_response(data)
        return None

    # ==================== Input Control ====================

    def click(self, x: int, y: int) -> Dict[str, Any]:
        """
        Perform a click at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Operation result
            
        Example:
            control.click(540, 960)
        """
        return self._request("POST", "/input/click", {"x": x, "y": y})

    def multi_click(
        self,
        x: int,
        y: int,
        times: int = 2,
        interval: int = 100,
    ) -> Dict[str, Any]:
        """
        Perform multiple clicks at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            times: Number of clicks
            interval: Interval between clicks in ms
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/input/multi_click",
            {"x": x, "y": y, "times": times, "interval": interval},
        )

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: int = 300,
        up_delay: int = 0,
    ) -> Dict[str, Any]:
        """
        Perform a linear swipe gesture.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Swipe duration in ms
            up_delay: Delay before lifting finger
            
        Returns:
            Operation result
            
        Example:
            # Swipe up
            control.swipe(540, 1500, 540, 500, duration=300)
        """
        return self._request(
            "POST",
            "/input/swipe",
            {
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration,
                "up_delay": up_delay,
            },
        )

    def scroll_bezier(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: int = 500,
        up_delay: int = 0,
        clear_fling: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform a bezier curve swipe (more natural).
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Swipe duration in ms
            up_delay: Delay before lifting finger
            clear_fling: Whether to clear fling momentum
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/input/scroll_bezier",
            {
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y,
                "duration": duration,
                "up_delay": up_delay,
                "clear_fling": clear_fling,
            },
        )

    def input_text(self, text: str) -> Dict[str, Any]:
        """
        Input text at current focus.
        
        Args:
            text: Text to input
            
        Returns:
            Operation result
            
        Example:
            control.input_text("Hello World!")
        """
        return self._request("POST", "/input/text", {"text": text})

    def key_event(
        self,
        key_code: Optional[int] = None,
        key_codes: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Send key event(s).
        
        Common key codes:
        - 3: HOME
        - 4: BACK
        - 24: VOLUME_UP
        - 25: VOLUME_DOWN
        - 26: POWER
        - 66: ENTER
        - 67: DEL (backspace)
        
        Args:
            key_code: Single key code
            key_codes: List of key codes
            
        Returns:
            Operation result
        """
        body: Dict[str, Any] = {}
        if key_code is not None:
            body["key_code"] = key_code
        if key_codes is not None:
            body["key_codes"] = key_codes
        
        return self._request("POST", "/input/keyevent", body)

    def press_back(self) -> Dict[str, Any]:
        """Press the BACK button."""
        return self.key_event(key_code=4)

    def press_home(self) -> Dict[str, Any]:
        """Press the HOME button."""
        return self.key_event(key_code=3)

    def press_enter(self) -> Dict[str, Any]:
        """Press the ENTER key."""
        return self.key_event(key_code=66)

    # ==================== Activity & Package ====================

    def start_app(self, package_name: str) -> Dict[str, Any]:
        """
        Start an application.
        
        Args:
            package_name: Package name of the app
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/activity/start",
            {"package_name": package_name},
        )

    def launch_app(
        self,
        package_name: str,
        grant_all_permissions: bool = False,
    ) -> Dict[str, Any]:
        """
        Launch an application with optional permission grants.
        
        Use this for first-time launches that need permissions.
        
        Args:
            package_name: Package name of the app
            grant_all_permissions: Whether to auto-grant permissions
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/activity/launch_app",
            {
                "package_name": package_name,
                "grant_all_permissions": grant_all_permissions,
            },
        )

    def start_activity(
        self,
        package_name: str,
        class_name: Optional[str] = None,
        action: Optional[str] = None,
        data: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Start a specific activity with intent.
        
        Args:
            package_name: Package name
            class_name: Activity class name
            action: Intent action
            data: Intent data URI
            extras: Intent extras
            
        Returns:
            Operation result
            
        Example:
            # Open URL in browser
            control.start_activity(
                package_name="mark.via",
                action="android.intent.action.VIEW",
                data="https://www.google.com"
            )
        """
        body: Dict[str, Any] = {"package_name": package_name}
        if class_name:
            body["class_name"] = class_name
        if action:
            body["action"] = action
        if data:
            body["data"] = data
        if extras:
            body["extras"] = extras
        
        return self._request("POST", "/activity/start_activity", body)

    def stop_app(self, package_name: str) -> Dict[str, Any]:
        """
        Stop an application.
        
        Args:
            package_name: Package name of the app
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/activity/stop",
            {"package_name": package_name},
        )

    def list_packages(self, type: str = "user") -> List[PackageInfo]:
        """
        Get list of installed packages.
        
        Args:
            type: Package type filter ("user" or "system")
            
        Returns:
            List of PackageInfo objects
        """
        response = self._request("GET", f"/package/list?type={type}", None)
        packages = []
        for item in response.get("data", []):
            packages.append(PackageInfo.from_api_response(item))
        return packages

    def install_sync(self, apk_path: str) -> Dict[str, Any]:
        """
        Install APK from local path (synchronous).
        
        Args:
            apk_path: Path to APK file
            
        Returns:
            Operation result with package_name
        """
        return self._request(
            "POST",
            "/package/install_sync",
            {"path": apk_path},
        )

    def install_uri_sync(self, uri: str) -> Dict[str, Any]:
        """
        Install APK from URI (synchronous).
        
        Args:
            uri: URI of the APK file
            
        Returns:
            Operation result with package_name
        """
        return self._request(
            "POST",
            "/package/install_uri_sync",
            {"uri": uri},
        )

    def uninstall(
        self,
        package_name: str,
        keep_data: bool = False,
    ) -> Dict[str, Any]:
        """
        Uninstall an application.
        
        Args:
            package_name: Package name to uninstall
            keep_data: Whether to keep app data
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/package/uninstall",
            {"package_name": package_name, "keep_data": keep_data},
        )

    # ==================== System Operations ====================

    def shell(self, command: str, as_root: bool = False) -> Dict[str, Any]:
        """
        Execute shell command.
        
        Args:
            command: Shell command to execute
            as_root: Whether to run as root
            
        Returns:
            Command output
            
        Note:
            Use specialized APIs when available instead of shell.
        """
        return self._request(
            "POST",
            "/system/shell",
            {"command": command, "as_root": as_root},
        )

    def settings_get(self, namespace: str, key: str) -> Dict[str, Any]:
        """
        Get Android system setting.
        
        Args:
            namespace: Settings namespace (system, secure, global)
            key: Setting key
            
        Returns:
            Setting value
        """
        return self._request(
            "POST",
            "/system/settings_get",
            {"namespace": namespace, "key": key},
        )

    def settings_put(
        self,
        namespace: str,
        key: str,
        value: str,
    ) -> Dict[str, Any]:
        """
        Set Android system setting.
        
        Args:
            namespace: Settings namespace (system, secure, global)
            key: Setting key
            value: Setting value
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/system/settings_put",
            {"namespace": namespace, "key": key, "value": value},
        )

    # ==================== Clipboard ====================

    def clipboard_set(self, text: str) -> Dict[str, Any]:
        """
        Set clipboard content.
        
        Args:
            text: Text to copy to clipboard
            
        Returns:
            Operation result
        """
        return self._request("POST", "/clipboard/set", {"text": text})

    def clipboard_get(self) -> str:
        """
        Get clipboard content.
        
        Returns:
            Clipboard text
        """
        response = self._request("GET", "/clipboard/get", None)
        return response.get("data", {}).get("text", "")

    def clipboard_list(self) -> List[str]:
        """
        Get clipboard history.
        
        Returns:
            List of clipboard entries
        """
        response = self._request("GET", "/clipboard/list", None)
        return response.get("data", [])

    def clipboard_clear(self) -> Dict[str, Any]:
        """
        Clear clipboard.
        
        Returns:
            Operation result
        """
        return self._request("POST", "/clipboard/clear", {})

    # ==================== Google Services ====================

    def set_google_enabled(self, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable Google Mobile Services.
        
        Args:
            enabled: Whether to enable GMS
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/google/set_enabled",
            {"enabled": enabled},
        )

    def get_google_enabled(self) -> bool:
        """
        Check if Google Mobile Services is enabled.
        
        Returns:
            True if enabled
        """
        response = self._request("GET", "/google/get_enabled", None)
        return response.get("data", {}).get("enabled", False)

    def reset_gaid(self) -> Dict[str, Any]:
        """
        Reset Google Advertising ID.
        
        Returns:
            Operation result
        """
        return self._request("POST", "/google/reset_gaid", {})

    # ==================== Convenience Methods ====================

    def swipe_up(self, distance: int = 500, duration: int = 300) -> Dict[str, Any]:
        """Swipe up from center of screen."""
        display = self.display_info()
        center_x = display.width // 2
        center_y = display.height // 2
        return self.swipe(
            center_x, center_y + distance // 2,
            center_x, center_y - distance // 2,
            duration,
        )

    def swipe_down(self, distance: int = 500, duration: int = 300) -> Dict[str, Any]:
        """Swipe down from center of screen."""
        display = self.display_info()
        center_x = display.width // 2
        center_y = display.height // 2
        return self.swipe(
            center_x, center_y - distance // 2,
            center_x, center_y + distance // 2,
            duration,
        )

    def swipe_left(self, distance: int = 300, duration: int = 300) -> Dict[str, Any]:
        """Swipe left from center of screen."""
        display = self.display_info()
        center_x = display.width // 2
        center_y = display.height // 2
        return self.swipe(
            center_x + distance // 2, center_y,
            center_x - distance // 2, center_y,
            duration,
        )

    def swipe_right(self, distance: int = 300, duration: int = 300) -> Dict[str, Any]:
        """Swipe right from center of screen."""
        display = self.display_info()
        center_x = display.width // 2
        center_y = display.height // 2
        return self.swipe(
            center_x - distance // 2, center_y,
            center_x + distance // 2, center_y,
            duration,
        )

    def open_url(
        self,
        url: str,
        browser: str = "mark.via",
    ) -> Dict[str, Any]:
        """
        Open URL in browser.
        
        Args:
            url: URL to open
            browser: Browser package (default: Via)
            
        Returns:
            Operation result
        """
        return self.start_activity(
            package_name=browser,
            action="android.intent.action.VIEW",
            data=url,
        )

    def find_and_click(
        self,
        text: Optional[str] = None,
        resource_id: Optional[str] = None,
        timeout: int = 5000,
    ) -> bool:
        """
        Find a UI element and click it.
        
        Args:
            text: Text to find
            resource_id: Resource ID to find
            timeout: Wait timeout in ms
            
        Returns:
            True if found and clicked
        """
        selector: Dict[str, Any] = {}
        if text:
            selector["text"] = text
        if resource_id:
            selector["resource_id"] = resource_id
        
        node = self.node(
            selector=selector,
            wait_timeout=timeout,
            action="click",
        )
        return node is not None

    def wait_for_text(self, text: str, timeout: int = 10000) -> bool:
        """
        Wait for text to appear on screen.
        
        Args:
            text: Text to wait for
            timeout: Timeout in ms
            
        Returns:
            True if found
        """
        node = self.node(
            selector={"text": text},
            wait_timeout=timeout,
        )
        return node is not None
