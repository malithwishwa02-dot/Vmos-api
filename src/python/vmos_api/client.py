"""
VMOS API Main Client

This module provides the main entry point for interacting with the VMOS API.
"""

import subprocess
from typing import Optional, Union
from .auth.hmac_auth import HMACAuth, NoAuth
from .container.client import ContainerClient
from .control.client import ControlClient
from .host import HostClient
from .exceptions import VMOSConnectionError


class VMOSClient:
    """
    Main VMOS API client.
    
    Provides access to both Container API and Control API through a unified
    interface. Handles connection management and authentication.
    
    Example:
        # With authentication
        client = VMOSClient(
            host_ip="192.168.1.100",
            access_key="your_access_key",
            secret_key="your_secret_key"
        )
        
        # Without authentication (local development)
        client = VMOSClient(host_ip="127.0.0.1")
        
        # Access Container API
        instances = client.container.list_instances()
        
        # Access Control API for a specific device
        control = client.control(db_id="EDGE001")
        control.click(540, 960)
    """

    def __init__(
        self,
        host_ip: Optional[str] = None,
        cloud_ip: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        container_port: int = 18182,
        control_port: int = 18185,
        timeout: float = 30.0,
        auto_detect: bool = True,
    ):
        """
        Initialize VMOS client.
        
        Args:
            host_ip: Host machine IP address (for Container API)
            cloud_ip: Cloud device IP address (for direct Control API)
            access_key: API access key for HMAC authentication
            secret_key: API secret key for HMAC authentication
            container_port: Container API port (default: 18182)
            control_port: Control API port (default: 18185)
            timeout: Request timeout in seconds
            auto_detect: Automatically detect local cbs_go process
        """
        self._host_ip = host_ip
        self._cloud_ip = cloud_ip
        self._container_port = container_port
        self._control_port = control_port
        self._timeout = timeout
        
        # Setup authentication
        if access_key and secret_key:
            self._auth: Union[HMACAuth, NoAuth] = HMACAuth(access_key, secret_key)
        else:
            self._auth = NoAuth()
        
        # Auto-detect local installation
        if auto_detect and not host_ip and not cloud_ip:
            self._host_ip = self._detect_local_host()
        
        # Initialize sub-clients
        self._container_client: Optional[ContainerClient] = None
        self._host_client: Optional[HostClient] = None
        self._control_clients: dict = {}

    def _detect_local_host(self) -> Optional[str]:
        """
        Detect if running on VMOS Edge host machine.
        
        Checks for the presence of the cbs_go process to determine
        if we're running locally on a VMOS Edge host.
        
        Returns:
            "127.0.0.1" if local, None otherwise
        """
        try:
            result = subprocess.run(
                ["pgrep", "-x", "cbs_go"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                return "127.0.0.1"
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None

    @property
    def host_ip(self) -> Optional[str]:
        """Get the host IP address."""
        return self._host_ip

    @property
    def cloud_ip(self) -> Optional[str]:
        """Get the cloud device IP address."""
        return self._cloud_ip

    @property
    def container_base_url(self) -> str:
        """Get the Container API base URL."""
        if not self._host_ip:
            raise VMOSConnectionError(
                "No host_ip configured. Please provide host_ip or ensure "
                "you're running on a VMOS Edge host machine."
            )
        return f"http://{self._host_ip}:{self._container_port}"

    @property
    def container(self) -> ContainerClient:
        """
        Access the Container API client.
        
        The Container API manages cloud phone instances at the host level,
        including creating, starting, stopping, and deleting instances.
        
        Returns:
            ContainerClient instance
            
        Example:
            # List all instances
            instances = client.container.list_instances()
            
            # Create a new instance
            instance = client.container.create(user_name="my-device")
        """
        if self._container_client is None:
            self._container_client = ContainerClient(
                base_url=self.container_base_url,
                auth=self._auth,
                timeout=self._timeout,
            )
        return self._container_client

    @property
    def host(self) -> HostClient:
        """
        Access the Host management client.
        
        The Host API provides system-level operations like health checks,
        image management, and host configuration.
        
        Returns:
            HostClient instance
            
        Example:
            # Check host health
            health = client.host.heartbeat()
            
            # Get system info
            info = client.host.system_info()
        """
        if self._host_client is None:
            self._host_client = HostClient(
                base_url=self.container_base_url,
                auth=self._auth,
                timeout=self._timeout,
            )
        return self._host_client

    def control(self, db_id: Optional[str] = None) -> ControlClient:
        """
        Access the Control API client for a specific device.
        
        The Control API provides fine-grained control over individual
        Android instances, including input, screenshots, and app management.
        
        Args:
            db_id: Device database ID (required when using host_ip routing)
            
        Returns:
            ControlClient instance for the specified device
            
        Example:
            control = client.control(db_id="EDGE001")
            
            # Take a screenshot
            screenshot = control.screenshot()
            
            # Click on screen
            control.click(540, 960)
            
            # Input text
            control.input_text("Hello!")
        """
        # Determine base URL based on configuration
        if self._host_ip and db_id:
            # Host-routed control API
            base_url = f"http://{self._host_ip}:{self._container_port}/android_api/v2/{db_id}"
        elif self._cloud_ip:
            # Direct cloud IP control API
            base_url = f"http://{self._cloud_ip}:{self._control_port}/api"
        else:
            raise VMOSConnectionError(
                "Cannot determine Control API endpoint. Please provide either "
                "host_ip with db_id, or cloud_ip."
            )
        
        # Cache control clients by base URL
        if base_url not in self._control_clients:
            self._control_clients[base_url] = ControlClient(
                base_url=base_url,
                auth=self._auth,
                timeout=self._timeout,
            )
        
        return self._control_clients[base_url]

    def verify_connection(self) -> bool:
        """
        Verify connection to VMOS API.
        
        Returns:
            True if connection is successful
            
        Raises:
            VMOSConnectionError: If connection fails
        """
        try:
            # Try host heartbeat if host_ip is configured
            if self._host_ip:
                self.host.heartbeat()
                return True
        except Exception as e:
            raise VMOSConnectionError(
                f"Failed to verify connection: {str(e)}",
                host=self._host_ip,
                port=self._container_port,
            )
        return False

    def close(self) -> None:
        """Close all connections and cleanup resources."""
        self._container_client = None
        self._host_client = None
        self._control_clients.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
