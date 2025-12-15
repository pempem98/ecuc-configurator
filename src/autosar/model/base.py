"""
Base models for all AUTOSAR elements.

Provides common base classes and mixins used across all model types.
"""

from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class BaseElement(BaseModel):
    """
    Base class for all model elements.
    
    Provides common fields like name, description, UUID, and metadata.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )
    
    name: str = Field(..., min_length=1, description="Element name")
    description: Optional[str] = Field(None, description="Element description")
    uuid: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', uuid='{self.uuid}')"


class Identifiable(BaseElement):
    """
    Base class for identifiable AUTOSAR elements.
    
    Adds short_name and long_name for AUTOSAR compatibility.
    """
    
    short_name: str = Field(..., min_length=1, description="AUTOSAR short name")
    long_name: Optional[str] = Field(None, description="AUTOSAR long name")
    category: Optional[str] = Field(None, description="Element category")
    
    def __init__(self, **data):
        # If name is not provided but short_name is, use short_name as name
        if 'name' not in data and 'short_name' in data:
            data['name'] = data['short_name']
        # If short_name is not provided but name is, use name as short_name
        elif 'short_name' not in data and 'name' in data:
            data['short_name'] = data['name']
        super().__init__(**data)


class Referenceable(Identifiable):
    """
    Base class for elements that can be referenced by other elements.
    
    Adds reference path support.
    """
    
    reference_path: Optional[str] = Field(
        None,
        description="Absolute reference path (e.g., /Package/Element)"
    )
    
    def get_reference(self) -> str:
        """Get the reference path for this element."""
        if self.reference_path:
            return self.reference_path
        return f"/{self.short_name}"


class Versioned(BaseModel):
    """Mixin for versioned elements."""
    
    version: str = Field(default="1.0.0", description="Version string")
    revision: Optional[int] = Field(None, description="Revision number")


class Timestamped(BaseModel):
    """Mixin for timestamped elements."""
    
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    modified_at: Optional[str] = Field(None, description="Last modification timestamp")
    created_by: Optional[str] = Field(None, description="Creator name")
    modified_by: Optional[str] = Field(None, description="Last modifier name")
