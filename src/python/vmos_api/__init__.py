"""
VMOS Pro API - Python SDK

A comprehensive SDK for the VMOS Cloud/Edge Android Virtual Machine API.
Provides tools to manage and control VMOS cloud phone instances.

Example:
    from vmos_api import VMOSClient
    
    client = VMOSClient(host_ip="192.168.1.100")
    instances = client.container.list_instances()
"""

from .client import VMOSClient
from .auth.hmac_auth import HMACAuth
from .container.client import ContainerClient
from .control.client import ControlClient
from .exceptions import (
    VMOSError,
    VMOSConnectionError,
    VMOSAuthenticationError,
    VMOSAPIError,
    VMOSTimeoutError,
)

__version__ = "1.0.0"
__author__ = "VMOS API Contributors"
__all__ = [
    "VMOSClient",
    "HMACAuth",
    "ContainerClient",
    "ControlClient",
    "VMOSError",
    "VMOSConnectionError",
    "VMOSAuthenticationError",
    "VMOSAPIError",
    "VMOSTimeoutError",
]
