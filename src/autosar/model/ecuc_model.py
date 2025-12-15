"""
ECUC (ECU Configuration) data models.

Defines models for AUTOSAR ECUC configuration values and parameters.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import Field, field_validator

from .base import Identifiable, Referenceable


class AutosarVersion(str, Enum):
    """Supported AUTOSAR versions."""
    AR_4_2_2 = "4.2.2"
    AR_4_5_0 = "4.5.0"


class ECUCParameterType(str, Enum):
    """ECUC parameter value types."""
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    REFERENCE = "REFERENCE"
    ENUMERATION = "ENUMERATION"


class ECUCParameterValue(Identifiable):
    """
    ECUC Parameter Value.
    
    Represents a single parameter value in ECUC configuration.
    """
    
    definition_ref: str = Field(
        ...,
        description="Reference to parameter definition"
    )
    
    value_type: ECUCParameterType = Field(
        ...,
        description="Type of parameter value"
    )
    
    value: Optional[Union[int, float, bool, str]] = Field(
        None,
        description="The actual value"
    )
    
    reference_value: Optional[str] = Field(
        None,
        description="Reference value (for REFERENCE type)"
    )
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: Any, info) -> Any:
        """Validate value matches type."""
        if v is None:
            return v
        
        value_type = info.data.get('value_type')
        
        if value_type == ECUCParameterType.INTEGER and not isinstance(v, int):
            raise ValueError(f"INTEGER parameter must be int, got {type(v)}")
        elif value_type == ECUCParameterType.FLOAT and not isinstance(v, (int, float)):
            raise ValueError(f"FLOAT parameter must be numeric, got {type(v)}")
        elif value_type == ECUCParameterType.BOOLEAN and not isinstance(v, bool):
            raise ValueError(f"BOOLEAN parameter must be bool, got {type(v)}")
        elif value_type == ECUCParameterType.STRING and not isinstance(v, str):
            raise ValueError(f"STRING parameter must be str, got {type(v)}")
        
        return v


class ECUCContainerValue(Referenceable):
    """
    ECUC Container Value.
    
    Represents a container holding parameter values and sub-containers.
    """
    
    definition_ref: str = Field(
        ...,
        description="Reference to container definition"
    )
    
    parameters: List[ECUCParameterValue] = Field(
        default_factory=list,
        description="Parameter values in this container"
    )
    
    sub_containers: List['ECUCContainerValue'] = Field(
        default_factory=list,
        description="Sub-containers"
    )
    
    def add_parameter(self, param: ECUCParameterValue) -> None:
        """Add a parameter value."""
        self.parameters.append(param)
    
    def add_sub_container(self, container: 'ECUCContainerValue') -> None:
        """Add a sub-container."""
        self.sub_containers.append(container)
    
    def get_parameter(self, name: str) -> Optional[ECUCParameterValue]:
        """Get parameter by name."""
        for param in self.parameters:
            if param.short_name == name:
                return param
        return None
    
    def get_sub_container(self, name: str) -> Optional['ECUCContainerValue']:
        """Get sub-container by name."""
        for container in self.sub_containers:
            if container.short_name == name:
                return container
        return None


class ECUCModuleConfigurationValues(Referenceable):
    """
    ECUC Module Configuration Values.
    
    Represents configuration for a specific BSW module (e.g., CanIf, LinIf).
    """
    
    module_def_ref: str = Field(
        ...,
        description="Reference to module definition"
    )
    
    implementation_config_variant: str = Field(
        default="VariantPostBuild",
        description="Configuration variant (VariantPreCompile, VariantLinkTime, VariantPostBuild)"
    )
    
    containers: List[ECUCContainerValue] = Field(
        default_factory=list,
        description="Top-level containers"
    )
    
    def add_container(self, container: ECUCContainerValue) -> None:
        """Add a top-level container."""
        self.containers.append(container)
    
    def get_container(self, name: str) -> Optional[ECUCContainerValue]:
        """Get container by name."""
        for container in self.containers:
            if container.short_name == name:
                return container
        return None


class ECUCValueCollection(Referenceable):
    """
    ECUC Value Collection.
    
    Top-level container for all ECUC configuration values.
    """
    
    autosar_version: AutosarVersion = Field(
        default=AutosarVersion.AR_4_2_2,
        description="Target AUTOSAR version"
    )
    
    ecu_extract_version: str = Field(
        default="1.0.0",
        description="ECU extract version"
    )
    
    modules: List[ECUCModuleConfigurationValues] = Field(
        default_factory=list,
        description="Module configurations"
    )
    
    def add_module(self, module: ECUCModuleConfigurationValues) -> None:
        """Add a module configuration."""
        self.modules.append(module)
    
    def get_module(self, name: str) -> Optional[ECUCModuleConfigurationValues]:
        """Get module by name."""
        for module in self.modules:
            if module.short_name == name:
                return module
        return None
    
    def get_module_by_def_ref(self, def_ref: str) -> Optional[ECUCModuleConfigurationValues]:
        """Get module by definition reference."""
        for module in self.modules:
            if module.module_def_ref == def_ref:
                return module
        return None


class ECUCProject(Referenceable):
    """
    ECUC Project.
    
    Represents a complete ECUC project with all configurations.
    """
    
    autosar_version: AutosarVersion = Field(
        ...,
        description="AUTOSAR version"
    )
    
    ecu_instance: str = Field(
        ...,
        description="ECU instance name"
    )
    
    value_collection: ECUCValueCollection = Field(
        ...,
        description="ECUC value collection"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    # Source information
    source_files: List[str] = Field(
        default_factory=list,
        description="Source files used to generate this configuration"
    )
    
    def add_source_file(self, file_path: str) -> None:
        """Add a source file reference."""
        if file_path not in self.source_files:
            self.source_files.append(file_path)
