"""
Container API Data Models

This module defines data models for Container API requests and responses.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class InstanceStatus(Enum):
    """Possible states for a cloud phone instance."""
    CREATING = "creating"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    REBOOTING = "rebooting"
    REBUILDING = "rebuilding"
    RENEWING = "renewing"
    DELETING = "deleting"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, status: str) -> "InstanceStatus":
        """Convert string to InstanceStatus enum."""
        try:
            return cls(status.lower())
        except ValueError:
            return cls.UNKNOWN


@dataclass
class Instance:
    """
    Represents a VMOS cloud phone instance.
    
    Attributes:
        db_id: Unique database identifier for the instance
        user_name: Display name of the instance
        status: Current status of the instance
        adb_address: ADB connection address
        cloud_ip: Cloud device IP address (if available)
        image_repository: Image used for the instance
        resolution: Screen resolution
        created_at: Creation timestamp
    """
    db_id: str
    user_name: str
    status: InstanceStatus = InstanceStatus.UNKNOWN
    adb_address: Optional[str] = None
    cloud_ip: Optional[str] = None
    image_repository: Optional[str] = None
    resolution: Optional[str] = None
    created_at: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Instance":
        """Create Instance from API response data."""
        return cls(
            db_id=data.get("db_id", ""),
            user_name=data.get("user_name", ""),
            status=InstanceStatus.from_string(data.get("status", "")),
            adb_address=data.get("adb_address"),
            cloud_ip=data.get("cloud_ip"),
            image_repository=data.get("image_repository"),
            resolution=data.get("resolution"),
            created_at=data.get("created_at"),
            raw_data=data,
        )


@dataclass
class InstanceDetail:
    """
    Detailed information about a VMOS cloud phone instance.
    
    Attributes:
        db_id: Unique database identifier
        user_name: Display name
        status: Current status
        rom_status: ROM initialization status
        android_version: Android version
        cpu_cores: Number of CPU cores
        memory_mb: Memory in MB
        storage_gb: Storage in GB
        adb_port: ADB port number
        screen_port: Screen streaming port
        resolution: Screen resolution
        locale: System locale
        timezone: System timezone
        country: System country code
        gms_enabled: Whether Google Mobile Services are enabled
    """
    db_id: str
    user_name: str
    status: InstanceStatus = InstanceStatus.UNKNOWN
    rom_status: Optional[str] = None
    android_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_mb: Optional[int] = None
    storage_gb: Optional[float] = None
    adb_port: Optional[int] = None
    screen_port: Optional[int] = None
    resolution: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    gms_enabled: Optional[bool] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "InstanceDetail":
        """Create InstanceDetail from API response data."""
        return cls(
            db_id=data.get("db_id", ""),
            user_name=data.get("user_name", ""),
            status=InstanceStatus.from_string(data.get("status", "")),
            rom_status=data.get("rom_status"),
            android_version=data.get("android_version"),
            cpu_cores=data.get("cpu_cores"),
            memory_mb=data.get("memory_mb"),
            storage_gb=data.get("storage_gb"),
            adb_port=data.get("adb_port"),
            screen_port=data.get("screen_port"),
            resolution=data.get("resolution"),
            locale=data.get("locale"),
            timezone=data.get("timezone"),
            country=data.get("country"),
            gms_enabled=data.get("gms_enabled"),
            raw_data=data,
        )


@dataclass
class CreateInstanceRequest:
    """
    Request parameters for creating a new instance.
    
    Attributes:
        user_name: Required - Display name for the instance
        count: Number of instances to create (default: 1)
        bool_start: Whether to start instance after creation
        bool_macvlan: Whether to use macvlan networking
        macvlan_network: Macvlan network name
        macvlan_start_ip: Starting IP for macvlan
        image_repository: Image to use for the instance
        adi_id: ADI template ID
        resolution: Screen resolution (e.g., "1080x1920")
        locale: System locale (e.g., "en_US")
        timezone: System timezone (e.g., "America/New_York")
        country: Country code (e.g., "US")
        user_prop: Custom user properties
        cert_hash: Certificate hash
        cert_content: Certificate content
    """
    user_name: str
    count: int = 1
    bool_start: bool = False
    bool_macvlan: bool = False
    macvlan_network: Optional[str] = None
    macvlan_start_ip: Optional[str] = None
    image_repository: Optional[str] = None
    adi_id: Optional[int] = None
    resolution: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    user_prop: Optional[Dict[str, Any]] = None
    cert_hash: Optional[str] = None
    cert_content: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        data: Dict[str, Any] = {"user_name": self.user_name}
        
        if self.count != 1:
            data["count"] = self.count
        if self.bool_start:
            data["bool_start"] = self.bool_start
        if self.bool_macvlan:
            data["bool_macvlan"] = self.bool_macvlan
        if self.macvlan_network:
            data["macvlan_network"] = self.macvlan_network
        if self.macvlan_start_ip:
            data["macvlan_start_ip"] = self.macvlan_start_ip
        if self.image_repository:
            data["image_repository"] = self.image_repository
        if self.adi_id is not None:
            data["adiID"] = self.adi_id
        if self.resolution:
            data["resolution"] = self.resolution
        if self.locale:
            data["locale"] = self.locale
        if self.timezone:
            data["timezone"] = self.timezone
        if self.country:
            data["country"] = self.country
        if self.user_prop:
            data["userProp"] = self.user_prop
        if self.cert_hash:
            data["cert_hash"] = self.cert_hash
        if self.cert_content:
            data["cert_content"] = self.cert_content
            
        return data


@dataclass
class CreateInstanceResponse:
    """
    Response from creating a new instance.
    
    Attributes:
        success: Whether creation was successful
        db_ids: List of created instance IDs
        message: Response message
    """
    success: bool
    db_ids: List[str] = field(default_factory=list)
    message: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "CreateInstanceResponse":
        """Create response from API data."""
        return cls(
            success=data.get("code") == 200,
            db_ids=data.get("data", {}).get("db_ids", []),
            message=data.get("msg"),
        )


@dataclass
class AppInfo:
    """Information about an installed application."""
    package_name: str
    app_name: Optional[str] = None
    version_code: Optional[int] = None
    version_name: Optional[str] = None
    is_system: bool = False
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "AppInfo":
        """Create AppInfo from API response."""
        return cls(
            package_name=data.get("package_name", ""),
            app_name=data.get("app_name"),
            version_code=data.get("version_code"),
            version_name=data.get("version_name"),
            is_system=data.get("is_system", False),
        )
