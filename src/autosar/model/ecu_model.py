"""
ECU Configuration data models.

Defines models for ECU configuration, modules, containers, and parameters.
"""

from typing import List, Optional, Any, Union
from pydantic import Field, field_validator

from .base import BaseElement, Identifiable, Versioned
from .types import ParameterType, ModuleDefType, Multiplicity, ParameterValue


class Parameter(Identifiable):
    """
    Configuration Parameter.
    
    Represents a single configuration parameter within a container.
    """
    
    parameter_type: ParameterType = Field(
        ...,
        description="Parameter data type"
    )
    value: Optional[ParameterValue] = Field(
        None,
        description="Parameter value"
    )
    default_value: Optional[ParameterValue] = Field(
        None,
        description="Default value"
    )
    
    # Constraints
    min_value: Optional[Union[int, float]] = Field(
        None,
        description="Minimum value (for numeric types)"
    )
    max_value: Optional[Union[int, float]] = Field(
        None,
        description="Maximum value (for numeric types)"
    )
    allowed_values: Optional[List[Any]] = Field(
        None,
        description="List of allowed values (for enumerations)"
    )
    
    # Multiplicity
    multiplicity: Multiplicity = Field(
        default=Multiplicity.ONE,
        description="Parameter multiplicity"
    )
    
    # Reference type (for REFERENCE parameters)
    reference_type: Optional[str] = Field(
        None,
        description="Referenced element type"
    )
    
    # Metadata
    unit: Optional[str] = Field(None, description="Physical unit")
    is_mandatory: bool = Field(default=True, description="Is parameter mandatory")
    is_readonly: bool = Field(default=False, description="Is parameter read-only")
    
    @field_validator('value')
    @classmethod
    def validate_value_type(cls, v, info):
        """Validate value matches parameter type."""
        if v is None:
            return v
        
        param_type = info.data.get('parameter_type')
        if param_type == ParameterType.INTEGER and not isinstance(v, int):
            raise ValueError(f"Value must be integer for INTEGER type, got {type(v)}")
        elif param_type == ParameterType.FLOAT and not isinstance(v, (int, float)):
            raise ValueError(f"Value must be numeric for FLOAT type, got {type(v)}")
        elif param_type == ParameterType.BOOLEAN and not isinstance(v, bool):
            raise ValueError(f"Value must be boolean for BOOLEAN type, got {type(v)}")
        elif param_type == ParameterType.STRING and not isinstance(v, str):
            raise ValueError(f"Value must be string for STRING type, got {type(v)}")
        
        return v


class Container(Identifiable):
    """
    Configuration Container.
    
    Groups related parameters and sub-containers.
    """
    
    parameters: List[Parameter] = Field(
        default_factory=list,
        description="Parameters in this container"
    )
    sub_containers: List['Container'] = Field(
        default_factory=list,
        description="Nested sub-containers"
    )
    
    multiplicity: Multiplicity = Field(
        default=Multiplicity.ONE,
        description="Container multiplicity"
    )
    
    is_mandatory: bool = Field(
        default=True,
        description="Is container mandatory"
    )
    
    def get_parameter(self, name: str) -> Optional[Parameter]:
        """Get parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def get_sub_container(self, name: str) -> Optional['Container']:
        """Get sub-container by name."""
        for container in self.sub_containers:
            if container.name == name:
                return container
        return None
    
    def get_all_parameters(self, recursive: bool = False) -> List[Parameter]:
        """
        Get all parameters.
        
        Args:
            recursive: If True, include parameters from sub-containers
        """
        params = list(self.parameters)
        if recursive:
            for sub in self.sub_containers:
                params.extend(sub.get_all_parameters(recursive=True))
        return params


class Module(Identifiable, Versioned):
    """
    BSW Module Configuration.
    
    Represents an AUTOSAR Basic Software module (e.g., CanIf, Com, EcuM).
    """
    
    module_def: Optional[ModuleDefType] = Field(
        None,
        description="Module definition type"
    )
    
    containers: List[Container] = Field(
        default_factory=list,
        description="Module containers"
    )
    
    # Module metadata
    vendor_id: Optional[int] = Field(None, description="Vendor ID")
    module_id: Optional[int] = Field(None, description="Module ID")
    
    def get_container(self, name: str) -> Optional[Container]:
        """Get container by name."""
        for container in self.containers:
            if container.name == name:
                return container
        return None
    
    def get_parameter(self, container_name: str, param_name: str) -> Optional[Parameter]:
        """Get parameter by container and parameter name."""
        container = self.get_container(container_name)
        if container:
            return container.get_parameter(param_name)
        return None


class EcuConfiguration(Identifiable, Versioned):
    """
    Complete ECU Configuration.
    
    Top-level container for all ECU configuration data.
    """
    
    modules: List[Module] = Field(
        default_factory=list,
        description="BSW modules"
    )
    
    # ECU metadata
    ecu_instance: Optional[str] = Field(
        None,
        description="ECU instance name"
    )
    manufacturer: Optional[str] = Field(
        None,
        description="ECU manufacturer"
    )
    hardware_version: Optional[str] = Field(
        None,
        description="Hardware version"
    )
    software_version: Optional[str] = Field(
        None,
        description="Software version"
    )
    
    def get_module(self, name: str) -> Optional[Module]:
        """Get module by name."""
        for module in self.modules:
            if module.name == name:
                return module
        return None
    
    def get_module_by_def(self, module_def: ModuleDefType) -> Optional[Module]:
        """Get module by definition type."""
        for module in self.modules:
            if module.module_def == module_def:
                return module
        return None
    
    def get_all_parameters(self) -> List[Parameter]:
        """Get all parameters from all modules."""
        params = []
        for module in self.modules:
            for container in module.containers:
                params.extend(container.get_all_parameters(recursive=True))
        return params
