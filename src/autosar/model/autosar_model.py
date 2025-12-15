"""
AUTOSAR data models.

Defines models for AUTOSAR packages, components, interfaces, and data elements.
"""

from typing import List, Optional, Dict, Any
from pydantic import Field

from .base import Identifiable, Versioned, Referenceable
from .types import ParameterType


class DataElement(Identifiable):
    """
    AUTOSAR Data Element.
    
    Represents a data element in a port interface.
    """
    
    data_type: str = Field(..., description="Data type name")
    is_queued: bool = Field(default=False, description="Is queued data")
    
    # For application data types
    base_type: Optional[str] = Field(None, description="Base type")
    
    # Array properties
    is_array: bool = Field(default=False, description="Is array type")
    array_size: Optional[int] = Field(None, description="Array size")
    
    # Init value
    init_value: Optional[Any] = Field(None, description="Initial value")


class PortInterface(Referenceable, Versioned):
    """
    AUTOSAR Port Interface.
    
    Defines communication interface between software components.
    """
    
    interface_type: str = Field(
        ...,
        description="Interface type (SenderReceiver, ClientServer, etc.)"
    )
    
    data_elements: List[DataElement] = Field(
        default_factory=list,
        description="Data elements in interface"
    )
    
    # For ClientServer interfaces
    operations: List[str] = Field(
        default_factory=list,
        description="Operation names (for ClientServer)"
    )
    
    is_service: bool = Field(
        default=False,
        description="Is service interface"
    )
    
    def get_data_element(self, name: str) -> Optional[DataElement]:
        """Get data element by name."""
        for elem in self.data_elements:
            if elem.name == name:
                return elem
        return None


class Port(Identifiable):
    """
    AUTOSAR Port.
    
    Represents a port (required or provided) of a component.
    """
    
    port_direction: str = Field(
        ...,
        description="Port direction (Required/Provided)"
    )
    interface_ref: str = Field(
        ...,
        description="Reference to port interface"
    )
    
    # Communication properties
    com_spec: Dict[str, Any] = Field(
        default_factory=dict,
        description="Communication specification"
    )


class Component(Referenceable, Versioned):
    """
    AUTOSAR Software Component.
    
    Represents an application or complex driver component.
    """
    
    component_type: str = Field(
        ...,
        description="Component type (ApplicationSWC, SensorActuatorSWC, etc.)"
    )
    
    ports: List[Port] = Field(
        default_factory=list,
        description="Component ports"
    )
    
    # Internal behavior
    runnables: List[str] = Field(
        default_factory=list,
        description="Runnable entity names"
    )
    
    # Requirements
    required_interfaces: List[str] = Field(
        default_factory=list,
        description="Required interface references"
    )
    provided_interfaces: List[str] = Field(
        default_factory=list,
        description="Provided interface references"
    )
    
    def get_port(self, name: str) -> Optional[Port]:
        """Get port by name."""
        for port in self.ports:
            if port.name == name:
                return port
        return None


class ARPackage(Referenceable):
    """
    AUTOSAR Package.
    
    Container for organizing AUTOSAR elements hierarchically.
    """
    
    sub_packages: List['ARPackage'] = Field(
        default_factory=list,
        description="Sub-packages"
    )
    
    # Elements
    components: List[Component] = Field(
        default_factory=list,
        description="Software components"
    )
    interfaces: List[PortInterface] = Field(
        default_factory=list,
        description="Port interfaces"
    )
    
    # Other AUTOSAR elements
    elements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Other package elements"
    )
    
    def get_sub_package(self, name: str) -> Optional['ARPackage']:
        """Get sub-package by name."""
        for pkg in self.sub_packages:
            if pkg.name == name:
                return pkg
        return None
    
    def get_component(self, name: str) -> Optional[Component]:
        """Get component by name."""
        for comp in self.components:
            if comp.name == name:
                return comp
        return None
    
    def get_interface(self, name: str) -> Optional[PortInterface]:
        """Get interface by name."""
        for iface in self.interfaces:
            if iface.name == name:
                return iface
        return None
    
    def get_all_components(self, recursive: bool = False) -> List[Component]:
        """Get all components, optionally recursively."""
        comps = list(self.components)
        if recursive:
            for pkg in self.sub_packages:
                comps.extend(pkg.get_all_components(recursive=True))
        return comps
