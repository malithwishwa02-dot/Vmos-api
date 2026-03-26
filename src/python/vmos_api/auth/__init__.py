"""
VMOS API Authentication Module

Provides HMAC-SHA256 authentication for VMOS API requests.
"""

from .hmac_auth import HMACAuth

__all__ = ["HMACAuth"]
