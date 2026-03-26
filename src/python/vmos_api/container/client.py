"""
Container API Client

This module provides the client for managing VMOS cloud phone containers
through the Container API.
"""

import json
from typing import Optional, List, Dict, Any, Union
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from ..auth.hmac_auth import HMACAuth, NoAuth
from ..exceptions import (
    VMOSAPIError,
    VMOSConnectionError,
    VMOSTimeoutError,
    VMOSInstanceNotFoundError,
)
from .models import (
    Instance,
    InstanceDetail,
    InstanceStatus,
    CreateInstanceRequest,
    CreateInstanceResponse,
    AppInfo,
)


class ContainerClient:
    """
    Client for VMOS Container API.
    
    Manages cloud phone instances at the host level, including:
    - Instance lifecycle (create, start, stop, reboot, delete)
    - Instance listing and details
    - Batch operations
    - App distribution
    
    Example:
        client = ContainerClient(
            base_url="http://192.168.1.100:18182",
            auth=HMACAuth(access_key, secret_key)
        )
        
        # Create instance
        result = client.create(user_name="my-device")
        
        # List instances
        instances = client.list_instances()
    """

    def __init__(
        self,
        base_url: str,
        auth: Union[HMACAuth, NoAuth],
        timeout: float = 30.0,
    ):
        """
        Initialize Container API client.
        
        Args:
            base_url: Base URL for the Container API
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
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method
            path: API endpoint path
            body: Request body
            
        Returns:
            Parsed JSON response
            
        Raises:
            VMOSAPIError: On API error response
            VMOSConnectionError: On connection failure
            VMOSTimeoutError: On request timeout
        """
        url = f"{self._base_url}{path}"
        headers = self._auth.sign_request(method=method, url=url, body=body)
        
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        
        request = Request(url, data=data, headers=headers, method=method)
        
        try:
            with urlopen(request, timeout=self._timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                
                # Check for API error
                if response_data.get("code") != 200:
                    raise VMOSAPIError(
                        message=response_data.get("msg", "Unknown error"),
                        code=response_data.get("code"),
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
                raise VMOSAPIError(
                    message=str(e),
                    code=e.code,
                    endpoint=path,
                )
        except URLError as e:
            raise VMOSConnectionError(
                message=f"Connection failed: {str(e.reason)}",
            )
        except TimeoutError:
            raise VMOSTimeoutError(
                timeout=self._timeout,
                endpoint=path,
            )

    # ==================== Instance Management ====================

    def create(
        self,
        user_name: str,
        count: int = 1,
        bool_start: bool = False,
        image_repository: Optional[str] = None,
        adi_id: Optional[int] = None,
        resolution: Optional[str] = None,
        locale: Optional[str] = None,
        timezone: Optional[str] = None,
        country: Optional[str] = None,
        user_prop: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> CreateInstanceResponse:
        """
        Create new cloud phone instance(s).
        
        Args:
            user_name: Display name for the instance (required)
            count: Number of instances to create
            bool_start: Whether to start after creation
            image_repository: Image to use
            adi_id: ADI template ID
            resolution: Screen resolution (e.g., "1080x1920")
            locale: System locale (e.g., "en_US")
            timezone: System timezone
            country: Country code
            user_prop: Custom user properties
            **kwargs: Additional parameters
            
        Returns:
            CreateInstanceResponse with created instance IDs
            
        Example:
            result = client.create(
                user_name="test-device",
                bool_start=True,
                image_repository="vcloud_android13_edge"
            )
            print(f"Created: {result.db_ids}")
        """
        request = CreateInstanceRequest(
            user_name=user_name,
            count=count,
            bool_start=bool_start,
            image_repository=image_repository,
            adi_id=adi_id,
            resolution=resolution,
            locale=locale,
            timezone=timezone,
            country=country,
            user_prop=user_prop,
        )
        
        body = request.to_dict()
        body.update(kwargs)
        
        response = self._request("POST", "/container_api/v1/create", body)
        return CreateInstanceResponse.from_api_response(response)

    def list_instances(self) -> List[Instance]:
        """
        Get list of all instances.
        
        Tries POST first, falls back to GET if not supported.
        
        Returns:
            List of Instance objects
            
        Example:
            instances = client.list_instances()
            for inst in instances:
                print(f"{inst.db_id}: {inst.status}")
        """
        try:
            # Try POST first (preferred)
            response = self._request("POST", "/container_api/v1/get_db", {})
        except VMOSAPIError:
            # Fall back to GET
            response = self._request("GET", "/container_api/v1/get_db", None)
        
        instances = []
        data = response.get("data", [])
        if isinstance(data, list):
            for item in data:
                instances.append(Instance.from_api_response(item))
        
        return instances

    def list_names(self) -> List[Dict[str, str]]:
        """
        Get list of all instance IDs and names.
        
        Returns:
            List of dicts with db_id, user_name, and adb info
        """
        response = self._request("GET", "/container_api/v1/list_names", None)
        return response.get("data", [])

    def get_detail(self, db_id: str) -> InstanceDetail:
        """
        Get detailed information about an instance.
        
        Args:
            db_id: Instance database ID
            
        Returns:
            InstanceDetail object
            
        Raises:
            VMOSInstanceNotFoundError: If instance not found
        """
        try:
            response = self._request(
                "GET",
                f"/container_api/v1/get_android_detail/{db_id}",
                None,
            )
            return InstanceDetail.from_api_response(response.get("data", {}))
        except VMOSAPIError as e:
            if e.code == 404:
                raise VMOSInstanceNotFoundError(db_id)
            raise

    def get_screenshot(self, db_id: str) -> bytes:
        """
        Get screenshot of an instance.
        
        Args:
            db_id: Instance database ID
            
        Returns:
            Screenshot image bytes
        """
        url = f"{self._base_url}/container_api/v1/screenshots/{db_id}"
        headers = self._auth.sign_request("GET", url, None)
        
        request = Request(url, headers=headers, method="GET")
        
        with urlopen(request, timeout=self._timeout) as response:
            return response.read()

    def get_adb_command(self, db_id: str) -> str:
        """
        Get ADB connection command for an instance.
        
        Args:
            db_id: Instance database ID
            
        Returns:
            ADB connect command string
        """
        response = self._request(
            "GET",
            f"/container_api/v1/adb_start/{db_id}",
            None,
        )
        return response.get("data", {}).get("adb_command", "")

    def rom_status(self, db_id: str) -> Dict[str, Any]:
        """
        Check if ROM is ready for an instance.
        
        Args:
            db_id: Instance database ID
            
        Returns:
            ROM status information
        """
        response = self._request(
            "GET",
            f"/container_api/v1/rom_status/{db_id}",
            None,
        )
        return response.get("data", {})

    # ==================== Lifecycle Operations ====================

    def start(self, db_ids: List[str]) -> Dict[str, Any]:
        """
        Start instance(s).
        
        Args:
            db_ids: List of instance IDs to start
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/container_api/v1/run",
            {"db_ids": db_ids},
        )

    def stop(self, db_ids: List[str]) -> Dict[str, Any]:
        """
        Stop instance(s).
        
        Args:
            db_ids: List of instance IDs to stop
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/container_api/v1/stop",
            {"db_ids": db_ids},
        )

    def reboot(self, db_ids: List[str]) -> Dict[str, Any]:
        """
        Reboot instance(s).
        
        Args:
            db_ids: List of instance IDs to reboot
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/container_api/v1/reboot",
            {"db_ids": db_ids},
        )

    def reset(self, db_ids: List[str]) -> Dict[str, Any]:
        """
        Reset instance(s) to initial state.
        
        Args:
            db_ids: List of instance IDs to reset
            
        Returns:
            Operation result
            
        Warning:
            This will erase all data on the instance!
        """
        return self._request(
            "POST",
            "/container_api/v1/reset",
            {"db_ids": db_ids},
        )

    def delete(self, db_ids: List[str]) -> Dict[str, Any]:
        """
        Delete instance(s).
        
        Args:
            db_ids: List of instance IDs to delete
            
        Returns:
            Operation result
            
        Warning:
            This will permanently delete the instance(s)!
        """
        return self._request(
            "POST",
            "/container_api/v1/delete",
            {"db_ids": db_ids},
        )

    def rename(self, db_id: str, new_user_name: str) -> Dict[str, Any]:
        """
        Rename an instance.
        
        Args:
            db_id: Instance database ID
            new_user_name: New display name
            
        Returns:
            Operation result
        """
        return self._request(
            "GET",
            f"/container_api/v1/rename/{db_id}/{new_user_name}",
            None,
        )

    def clone(self, db_id: str, count: int = 1) -> Dict[str, Any]:
        """
        Clone an instance.
        
        Args:
            db_id: Source instance ID
            count: Number of clones to create
            
        Returns:
            Operation result with new instance IDs
        """
        return self._request(
            "POST",
            "/container_api/v1/clone",
            {"db_id": db_id, "count": count},
        )

    def clone_status(self) -> Dict[str, Any]:
        """
        Get status of clone operations.
        
        Returns:
            Clone operation status
        """
        response = self._request("GET", "/container_api/v1/clone_status", None)
        return response.get("data", {})

    def replace_devinfo(
        self,
        db_ids: List[str],
        user_prop: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Replace device information (one-key new device).
        
        Args:
            db_ids: List of instance IDs
            user_prop: Optional custom properties
            
        Returns:
            Operation result
        """
        body: Dict[str, Any] = {"db_ids": db_ids}
        if user_prop:
            body["userProp"] = user_prop
        
        return self._request(
            "POST",
            "/container_api/v1/replace_devinfo",
            body,
        )

    def upgrade_image(
        self,
        db_ids: List[str],
        image_repository: str,
    ) -> Dict[str, Any]:
        """
        Upgrade instances to a new image.
        
        Args:
            db_ids: List of instance IDs
            image_repository: Target image
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/container_api/v1/upgrade_image",
            {"db_ids": db_ids, "image_repository": image_repository},
        )

    # ==================== App Management ====================

    def get_apps(self, db_id: str) -> List[AppInfo]:
        """
        Get installed apps on an instance.
        
        Args:
            db_id: Instance database ID
            
        Returns:
            List of AppInfo objects
        """
        response = self._request(
            "GET",
            f"/android_api/v1/app_get/{db_id}",
            None,
        )
        apps = []
        for item in response.get("data", []):
            apps.append(AppInfo.from_api_response(item))
        return apps

    def app_start(self, db_ids: List[str], app: str) -> Dict[str, Any]:
        """
        Start an app on multiple instances.
        
        Args:
            db_ids: List of instance IDs
            app: Package name of the app
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/android_api/v1/app_start",
            {"db_ids": db_ids, "app": app},
        )

    def app_stop(self, db_ids: List[str], app: str) -> Dict[str, Any]:
        """
        Stop an app on multiple instances.
        
        Args:
            db_ids: List of instance IDs
            app: Package name of the app
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            "/android_api/v1/app_stop",
            {"db_ids": db_ids, "app": app},
        )

    def install_apk_from_url(
        self,
        db_ids: Union[List[str], str],
        url: str,
    ) -> Dict[str, Any]:
        """
        Install APK from URL on multiple instances.
        
        Args:
            db_ids: Instance IDs (list or comma-separated string)
            url: URL of the APK file
            
        Returns:
            Operation result
        """
        if isinstance(db_ids, list):
            db_ids_str = ",".join(db_ids)
        else:
            db_ids_str = db_ids
        
        return self._request(
            "POST",
            "/android_api/v1/install_apk_from_url_batch",
            {"db_ids": db_ids_str, "url": url},
        )

    def upload_file_from_url(
        self,
        db_ids: Union[List[str], str],
        url: str,
        target_path: str,
    ) -> Dict[str, Any]:
        """
        Upload file from URL to multiple instances.
        
        Args:
            db_ids: Instance IDs
            url: URL of the file
            target_path: Target path on device
            
        Returns:
            Operation result
        """
        if isinstance(db_ids, list):
            db_ids_str = ",".join(db_ids)
        else:
            db_ids_str = db_ids
        
        return self._request(
            "POST",
            "/android_api/v1/upload_file_from_url_batch",
            {"db_ids": db_ids_str, "url": url, "target_path": target_path},
        )

    # ==================== Device Control ====================

    def shell(self, db_id: str, command: str) -> Dict[str, Any]:
        """
        Execute shell command on an instance.
        
        Args:
            db_id: Instance database ID
            command: Shell command to execute
            
        Returns:
            Command output
        """
        return self._request(
            "POST",
            f"/android_api/v1/shell/{db_id}",
            {"command": command},
        )

    def gps_inject(
        self,
        db_id: str,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Inject GPS location on an instance.
        
        Args:
            db_id: Instance database ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            f"/android_api/v1/gps_inject/{db_id}",
            {"latitude": latitude, "longitude": longitude},
        )

    def set_timezone(self, db_id: str, timezone: str) -> Dict[str, Any]:
        """
        Set timezone on an instance.
        
        Args:
            db_id: Instance database ID
            timezone: Timezone string (e.g., "America/New_York")
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            f"/android_api/v1/timezone_set/{db_id}",
            {"timezone": timezone},
        )

    def set_country(self, db_id: str, country: str) -> Dict[str, Any]:
        """
        Set country on an instance.
        
        Args:
            db_id: Instance database ID
            country: Country code (e.g., "US")
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            f"/android_api/v1/country_set/{db_id}",
            {"country": country},
        )

    def set_language(self, db_id: str, language: str) -> Dict[str, Any]:
        """
        Set language on an instance.
        
        Args:
            db_id: Instance database ID
            language: Language code (e.g., "en")
            
        Returns:
            Operation result
        """
        return self._request(
            "POST",
            f"/android_api/v1/language_set/{db_id}",
            {"language": language},
        )

    def get_locale_info(self, db_id: str) -> Dict[str, Any]:
        """
        Get timezone, country, and language for an instance.
        
        Args:
            db_id: Instance database ID
            
        Returns:
            Locale information
        """
        response = self._request(
            "GET",
            f"/android_api/v1/get_timezone_locale/{db_id}",
            None,
        )
        return response.get("data", {})

    # ==================== GMS Control ====================

    def gms_start(self) -> Dict[str, Any]:
        """
        Enable Google Mobile Services on all instances.
        
        Returns:
            Operation result
        """
        return self._request("GET", "/container_api/v1/gms_start", None)

    def gms_stop(self) -> Dict[str, Any]:
        """
        Disable Google Mobile Services on all instances.
        
        Returns:
            Operation result
        """
        return self._request("GET", "/container_api/v1/gms_stop", None)

    # ==================== Sync Status ====================

    def sync_status(self) -> Dict[str, Any]:
        """
        Synchronize and get current status of all instances.
        
        Returns:
            Status information for all instances
        """
        response = self._request("GET", "/container_api/v1/sync_status", None)
        return response.get("data", {})
