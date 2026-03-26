"""
HMAC-SHA256 Authentication for VMOS API

This module provides secure authentication using HMAC-SHA256 signatures
for all VMOS API requests.
"""

import hashlib
import hmac
import base64
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlparse


class HMACAuth:
    """
    HMAC-SHA256 Authentication handler for VMOS API.
    
    This class generates properly signed authentication headers for
    VMOS API requests using HMAC-SHA256 signatures.
    
    Example:
        auth = HMACAuth(
            access_key="your_access_key",
            secret_key="your_secret_key"
        )
        
        headers = auth.sign_request(
            method="POST",
            path="/container_api/v1/create",
            body={"user_name": "test-001"}
        )
    """

    def __init__(self, access_key: str, secret_key: str):
        """
        Initialize HMAC authentication.
        
        Args:
            access_key: Your VMOS API access key
            secret_key: Your VMOS API secret key
        """
        self.access_key = access_key
        self.secret_key = secret_key

    def _get_timestamp(self) -> str:
        """Generate ISO 8601 timestamp in UTC."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _hash_body(self, body: Optional[Dict[str, Any]]) -> str:
        """
        Create SHA256 hash of request body.
        
        Args:
            body: Request body dictionary
            
        Returns:
            Base64 encoded SHA256 hash
        """
        if body is None:
            body_string = ""
        else:
            body_string = json.dumps(body, separators=(",", ":"), sort_keys=True)
        
        body_hash = hashlib.sha256(body_string.encode("utf-8")).digest()
        return base64.b64encode(body_hash).decode("utf-8")

    def _create_canonical_string(
        self,
        method: str,
        path: str,
        host: str,
        timestamp: str,
        content_type: str,
        body_hash: str,
    ) -> str:
        """
        Create canonical string for signing.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            host: Target host
            timestamp: ISO 8601 timestamp
            content_type: Content-Type header
            body_hash: Base64 encoded body hash
            
        Returns:
            Canonical string for signing
        """
        canonical_parts = [
            method.upper(),
            path,
            f"content-type:{content_type}",
            f"x-date:{timestamp}",
            f"x-host:{host}",
            body_hash,
        ]
        return "\n".join(canonical_parts)

    def _sign(self, string_to_sign: str) -> str:
        """
        Create HMAC-SHA256 signature.
        
        Args:
            string_to_sign: Canonical string to sign
            
        Returns:
            Base64 encoded signature
        """
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return base64.b64encode(signature).decode("utf-8")

    def sign_request(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        content_type: str = "application/json",
    ) -> Dict[str, str]:
        """
        Generate signed headers for an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Full URL or path of the request
            body: Request body dictionary (for POST/PUT)
            content_type: Content-Type header value
            
        Returns:
            Dictionary of headers including authentication
            
        Example:
            headers = auth.sign_request(
                method="POST",
                url="http://192.168.1.100:18182/container_api/v1/create",
                body={"user_name": "test-001"}
            )
        """
        # Parse URL to extract host and path
        parsed = urlparse(url)
        host = parsed.netloc or parsed.path.split("/")[0]
        path = parsed.path if parsed.path else "/"
        
        # Generate timestamp
        timestamp = self._get_timestamp()
        
        # Hash the body
        body_hash = self._hash_body(body)
        
        # Create canonical string
        canonical_string = self._create_canonical_string(
            method=method,
            path=path,
            host=host,
            timestamp=timestamp,
            content_type=content_type,
            body_hash=body_hash,
        )
        
        # Generate signature
        signature = self._sign(canonical_string)
        
        # Build authorization header
        signed_headers = "content-type;x-date;x-host"
        authorization = (
            f"HMAC-SHA256 "
            f"Credential={self.access_key}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        return {
            "Content-Type": content_type,
            "x-date": timestamp,
            "x-host": host,
            "Authorization": authorization,
        }

    def sign_multipart_request(
        self,
        method: str,
        url: str,
        boundary: str,
    ) -> Dict[str, str]:
        """
        Generate signed headers for a multipart form request.
        
        Args:
            method: HTTP method
            url: Request URL
            boundary: Multipart boundary string
            
        Returns:
            Dictionary of headers including authentication
        """
        content_type = f"multipart/form-data; boundary={boundary}"
        return self.sign_request(
            method=method,
            url=url,
            body=None,
            content_type=content_type,
        )


class NoAuth:
    """No authentication (for local development or unsecured APIs)."""

    def sign_request(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        content_type: str = "application/json",
    ) -> Dict[str, str]:
        """Return basic headers without authentication."""
        return {"Content-Type": content_type}

    def sign_multipart_request(
        self,
        method: str,
        url: str,
        boundary: str,
    ) -> Dict[str, str]:
        """Return multipart headers without authentication."""
        return {"Content-Type": f"multipart/form-data; boundary={boundary}"}
