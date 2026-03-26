"""
Control API Data Models

This module defines data models for Control API requests and responses.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import base64
import io


class NodeAction(Enum):
    """Available actions for UI node operations."""
    CLICK = "click"
    LONG_CLICK = "long_click"
    SET_TEXT = "set_text"
    CLEAR_TEXT = "clear_text"
    SCROLL_FORWARD = "scroll_forward"
    SCROLL_BACKWARD = "scroll_backward"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    FOCUS = "focus"
    COPY = "copy"
    PASTE = "paste"
    CUT = "cut"


@dataclass
class VersionInfo:
    """
    API version information.
    
    Attributes:
        version_name: Version string (e.g., "2.5.0")
        version_code: Numeric version code
        supported_list: List of supported API paths
    """
    version_name: str
    version_code: int
    supported_list: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "VersionInfo":
        """Create from API response."""
        return cls(
            version_name=data.get("version_name", ""),
            version_code=data.get("version_code", 0),
            supported_list=data.get("supported_list", []),
            raw_data=data,
        )


@dataclass
class DisplayInfo:
    """
    Screen display information.
    
    Attributes:
        width: Screen width in pixels
        height: Screen height in pixels
        density: Screen density
        rotation: Current rotation (0, 90, 180, 270)
    """
    width: int
    height: int
    density: Optional[int] = None
    rotation: int = 0
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "DisplayInfo":
        """Create from API response."""
        return cls(
            width=data.get("width", 0),
            height=data.get("height", 0),
            density=data.get("density"),
            rotation=data.get("rotation", 0),
            raw_data=data,
        )


@dataclass
class TopActivity:
    """
    Current foreground activity information.
    
    Attributes:
        package_name: Package name of the app
        class_name: Activity class name
        activity_name: Full activity name
    """
    package_name: str
    class_name: str
    activity_name: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "TopActivity":
        """Create from API response."""
        return cls(
            package_name=data.get("package_name", ""),
            class_name=data.get("class_name", ""),
            activity_name=data.get("activity_name"),
            raw_data=data,
        )


@dataclass
class UINode:
    """
    UI node from accessibility tree.
    
    Attributes:
        text: Node text content
        content_desc: Content description
        resource_id: Resource ID
        class_name: Widget class name
        package: Package name
        bounds: Bounding rectangle [left, top, right, bottom]
        clickable: Whether the node is clickable
        enabled: Whether the node is enabled
        scrollable: Whether the node is scrollable
        index: Child index
        children: Child nodes
    """
    text: Optional[str] = None
    content_desc: Optional[str] = None
    resource_id: Optional[str] = None
    class_name: Optional[str] = None
    package: Optional[str] = None
    bounds: Optional[List[int]] = None
    clickable: bool = False
    enabled: bool = True
    scrollable: bool = False
    index: int = 0
    children: List["UINode"] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "UINode":
        """Create from API response."""
        children = []
        for child_data in data.get("children", []):
            children.append(cls.from_api_response(child_data))
        
        bounds = data.get("bounds")
        if isinstance(bounds, str):
            # Parse bounds string like "[0,0][1080,1920]"
            import re
            match = re.findall(r'\d+', bounds)
            if len(match) == 4:
                bounds = [int(x) for x in match]
        
        return cls(
            text=data.get("text"),
            content_desc=data.get("content_desc") or data.get("contentDescription"),
            resource_id=data.get("resource_id") or data.get("resourceId"),
            class_name=data.get("class_name") or data.get("className"),
            package=data.get("package"),
            bounds=bounds,
            clickable=data.get("clickable", False),
            enabled=data.get("enabled", True),
            scrollable=data.get("scrollable", False),
            index=data.get("index", 0),
            children=children,
            raw_data=data,
        )

    @property
    def center(self) -> Optional[tuple]:
        """Get center coordinates of the node."""
        if self.bounds and len(self.bounds) == 4:
            x = (self.bounds[0] + self.bounds[2]) // 2
            y = (self.bounds[1] + self.bounds[3]) // 2
            return (x, y)
        return None

    def find(self, **kwargs) -> Optional["UINode"]:
        """
        Find first matching child node.
        
        Args:
            **kwargs: Matching criteria (text, resource_id, class_name, etc.)
            
        Returns:
            First matching UINode or None
        """
        for child in self.children:
            matches = True
            for key, value in kwargs.items():
                node_value = getattr(child, key, None)
                if node_value != value:
                    if key == "text" and value in str(node_value or ""):
                        continue
                    matches = False
                    break
            if matches:
                return child
            # Recursive search
            result = child.find(**kwargs)
            if result:
                return result
        return None

    def find_all(self, **kwargs) -> List["UINode"]:
        """
        Find all matching child nodes.
        
        Args:
            **kwargs: Matching criteria
            
        Returns:
            List of matching UINodes
        """
        results = []
        for child in self.children:
            matches = True
            for key, value in kwargs.items():
                node_value = getattr(child, key, None)
                if node_value != value:
                    if key == "text" and value in str(node_value or ""):
                        continue
                    matches = False
                    break
            if matches:
                results.append(child)
            # Recursive search
            results.extend(child.find_all(**kwargs))
        return results


@dataclass
class Screenshot:
    """
    Screenshot data.
    
    Attributes:
        data: Raw image bytes
        format: Image format (png, jpeg)
        width: Image width
        height: Image height
    """
    data: bytes
    format: str = "png"
    width: Optional[int] = None
    height: Optional[int] = None
    
    @classmethod
    def from_bytes(cls, data: bytes, fmt: str = "png") -> "Screenshot":
        """Create from raw bytes."""
        return cls(data=data, format=fmt)
    
    @classmethod
    def from_base64(cls, b64_string: str, fmt: str = "png") -> "Screenshot":
        """Create from base64 encoded string."""
        # Remove data URL prefix if present
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        data = base64.b64decode(b64_string)
        return cls(data=data, format=fmt)
    
    def save(self, path: str) -> None:
        """
        Save screenshot to file.
        
        Args:
            path: File path to save to
        """
        with open(path, "wb") as f:
            f.write(self.data)
    
    def to_base64(self) -> str:
        """Convert to base64 string."""
        return base64.b64encode(self.data).decode("utf-8")
    
    def to_data_url(self) -> str:
        """Convert to data URL."""
        mime_type = f"image/{self.format}"
        return f"data:{mime_type};base64,{self.to_base64()}"

    def to_pil_image(self):
        """
        Convert to PIL Image object.
        
        Requires: pillow package
        
        Returns:
            PIL.Image object
        """
        try:
            from PIL import Image
            return Image.open(io.BytesIO(self.data))
        except ImportError:
            raise ImportError("PIL/Pillow is required for this operation. Install with: pip install pillow")


@dataclass
class DumpCompact:
    """
    Compact UI hierarchy dump.
    
    Attributes:
        root: Root UI node
        raw_xml: Raw XML string (if available)
    """
    root: Optional[UINode] = None
    raw_xml: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "DumpCompact":
        """Create from API response."""
        root = None
        if "root" in data:
            root = UINode.from_api_response(data["root"])
        elif "hierarchy" in data:
            root = UINode.from_api_response(data["hierarchy"])
        elif isinstance(data, dict) and "children" in data:
            root = UINode.from_api_response(data)
        
        return cls(
            root=root,
            raw_xml=data.get("xml"),
            raw_data=data,
        )

    def find(self, **kwargs) -> Optional[UINode]:
        """Find first matching node in hierarchy."""
        if self.root:
            return self.root.find(**kwargs)
        return None

    def find_all(self, **kwargs) -> List[UINode]:
        """Find all matching nodes in hierarchy."""
        if self.root:
            return self.root.find_all(**kwargs)
        return []


@dataclass
class NodeSelector:
    """
    Selector for finding UI nodes.
    
    Attributes:
        xpath: XPath expression
        text: Exact text match
        content_desc: Content description match
        resource_id: Resource ID match
        class_name: Class name match
        package: Package name match
        clickable: Whether node should be clickable
        enabled: Whether node should be enabled
        scrollable: Whether node should be scrollable
        index: Child index
    """
    xpath: Optional[str] = None
    text: Optional[str] = None
    content_desc: Optional[str] = None
    resource_id: Optional[str] = None
    class_name: Optional[str] = None
    package: Optional[str] = None
    clickable: Optional[bool] = None
    enabled: Optional[bool] = None
    scrollable: Optional[bool] = None
    index: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        result = {}
        if self.xpath:
            result["xpath"] = self.xpath
        if self.text:
            result["text"] = self.text
        if self.content_desc:
            result["content_desc"] = self.content_desc
        if self.resource_id:
            result["resource_id"] = self.resource_id
        if self.class_name:
            result["class_name"] = self.class_name
        if self.package:
            result["package"] = self.package
        if self.clickable is not None:
            result["clickable"] = self.clickable
        if self.enabled is not None:
            result["enabled"] = self.enabled
        if self.scrollable is not None:
            result["scrollable"] = self.scrollable
        if self.index is not None:
            result["index"] = self.index
        return result


@dataclass
class PackageInfo:
    """Information about an installed package."""
    package_name: str
    label: Optional[str] = None
    version_code: Optional[int] = None
    version_name: Optional[str] = None
    is_system: bool = False
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "PackageInfo":
        """Create from API response."""
        return cls(
            package_name=data.get("package_name", ""),
            label=data.get("label"),
            version_code=data.get("version_code"),
            version_name=data.get("version_name"),
            is_system=data.get("is_system", False),
        )


@dataclass
class ActionInfo:
    """Information about an available API action."""
    path: str
    description: Optional[str] = None
    method: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ActionInfo":
        """Create from API response."""
        return cls(
            path=data.get("path", ""),
            description=data.get("description"),
            method=data.get("method"),
            parameters=data.get("parameters", []),
        )
