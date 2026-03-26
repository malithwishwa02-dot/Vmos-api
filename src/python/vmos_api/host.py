"""
VMOS Host Management Client

This module provides the client for host-level management operations.
"""

import json
from typing import Dict, Any, Optional, List, Union
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .auth.hmac_auth import HMACAuth, NoAuth
from .exceptions import VMOSAPIError, VMOSConnectionError, VMOSTimeoutError


class HostClient:
    """
    Client for VMOS Host Management API.
    
    Provides system-level operations for the VMOS Edge host machine:
    - Health checks and heartbeat
    - System information
    - Image management
    - Host configuration
    
    Example:
        host = HostClient(
            base_url="http://192.168.1.100:18182",
            auth=HMACAuth(access_key, secret_key)
        )
        
        # Check host health
        health = host.heartbeat()
        
        # Get system info
        info = host.system_info()
    """

    def __init__(
        self,
        base_url: str,
        auth: Union[HMACAuth, NoAuth],
        timeout: float = 30.0,
    ):
        """
        Initialize Host client.
        
        Args:
            base_url: Base URL for the API
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
        """Make an API request."""
        url = f"{self._base_url}{path}"
        headers = self._auth.sign_request(method=method, url=url, body=body)
        
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        
        request = Request(url, data=data, headers=headers, method=method)
        
        try:
            with urlopen(request, timeout=self._timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                
                if response_data.get("code") not in (200, None):
                    if response_data.get("code") != 200:
                        raise VMOSAPIError(
                            message=response_data.get("msg", "Unknown error"),
                            code=response_data.get("code"),
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

    # ==================== Health & Status ====================

    def heartbeat(self) -> Dict[str, Any]:
        """
        Check host heartbeat and Docker/Ping status.
        
        Returns:
            Health status information
            
        Example:
            health = host.heartbeat()
            print(f"Host OK: {health.get('host_ok')}")
        """
        response = self._request("GET", "/v1/heartbeat", None)
        return response.get("data", response)

    def system_info(self) -> Dict[str, Any]:
        """
        Get system information (CPU, memory, disk, swap).
        
        Returns:
            System information dictionary
            
        Example:
            info = host.system_info()
            print(f"CPU Usage: {info.get('cpu_usage')}%")
            print(f"Memory: {info.get('memory_used')} / {info.get('memory_total')}")
        """
        response = self._request("GET", "/v1/systeminfo", None)
        return response.get("data", response)

    def hardware_config(self) -> Dict[str, Any]:
        """
        Get hardware configuration.
        
        Returns:
            Hardware configuration details
        """
        response = self._request("GET", "/v1/get_hardware_cfg", None)
        return response.get("data", response)

    def network_info(self) -> Dict[str, Any]:
        """
        Get host network information.
        
        Returns:
            Network configuration and status
        """
        response = self._request("GET", "/v1/net_info", None)
        return response.get("data", response)

    # ==================== Image Management ====================

    def list_images(self) -> List[Dict[str, Any]]:
        """
        Get list of available images.
        
        Returns:
            List of image information
            
        Example:
            images = host.list_images()
            for img in images:
                print(f"Image: {img.get('name')}")
        """
        response = self._request("GET", "/v1/get_img_list", None)
        return response.get("data", [])

    def prune_images(self) -> Dict[str, Any]:
        """
        Clean up unused images.
        
        Returns:
            Cleanup result
        """
        return self._request("GET", "/v1/prune_images", None)

    # ==================== ADI Management ====================

    def list_adi(self) -> List[Dict[str, Any]]:
        """
        Get list of ADI templates.
        
        Returns:
            List of ADI template information
        """
        response = self._request("GET", "/v1/get_adi_list", None)
        return response.get("data", [])

    # ==================== Swap Management ====================

    def swap_enable(self) -> Dict[str, Any]:
        """
        Enable swap on the host.
        
        Returns:
            Operation result
        """
        return self._request("GET", "/v1/swap/1", None)

    def swap_disable(self) -> Dict[str, Any]:
        """
        Disable swap on the host.
        
        Returns:
            Operation result
        """
        return self._request("GET", "/v1/swap/0", None)

    # ==================== Host Control ====================

    def reboot(self) -> Dict[str, Any]:
        """
        Reboot the host machine.
        
        Returns:
            Operation result
            
        Warning:
            This will restart the entire host system!
        """
        return self._request("GET", "/v1/reboot_for_arm", None)

    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown the host machine.
        
        Returns:
            Operation result
            
        Warning:
            This will power off the host system!
        """
        return self._request("GET", "/v1/shutdown", None)

    def reset(self) -> Dict[str, Any]:
        """
        Reset the host to initial state.
        
        Returns:
            Operation result
            
        Warning:
            This will erase all data and configurations!
        """
        return self._request("GET", "/v1/reset", None)

    # ==================== Storage ====================

    def storage_status(self) -> Dict[str, Any]:
        """
        Get storage status.
        
        Returns:
            Storage information
        """
        response = self._request("GET", "/storage/status", None)
        return response.get("data", response)

    def storage_format(self) -> Dict[str, Any]:
        """
        Format SSD storage.
        
        Returns:
            Operation result
            
        Warning:
            This will erase all data on the SSD!
        """
        return self._request("POST", "/storage/format", {})

    # ==================== Logs ====================

    def recent_logs(self) -> List[Dict[str, Any]]:
        """
        Get recent interface logs.
        
        Returns:
            List of recent log entries
        """
        response = self._request("GET", "/interface_logs/recent", None)
        return response.get("data", [])

    def log_stats(self) -> Dict[str, Any]:
        """
        Get interface success rate statistics.
        
        Returns:
            Statistics information
        """
        response = self._request("GET", "/interface_logs/stats", None)
        return response.get("data", response)
