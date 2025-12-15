"""
ECUC Generator - Generates ECUC configuration files in ARXML format.

Supports AUTOSAR AR4.2.2 and AR4.5 formats.
"""

from typing import Optional, TextIO
from pathlib import Path
import logging
from xml.etree import ElementTree as ET
from xml.dom import minidom

from ..model import (
    ECUCProject, ECUCValueCollection, ECUCModuleConfigurationValues,
    ECUCContainerValue, ECUCParameterValue,
    AutosarVersion, ECUCParameterType
)


class GeneratorException(Exception):
    """Base exception for generator errors."""
    pass


class ECUCGenerator:
    """
    Generator for ECUC configuration files.
    
    Generates ARXML files containing ECUC configuration values
    compatible with AUTOSAR AR4.2.2 and AR4.5.
    """
    
    # XML namespaces for different AUTOSAR versions
    NAMESPACES = {
        AutosarVersion.AR_4_2_2: {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '': 'http://autosar.org/schema/r4.0',
            'schemaLocation': 'http://autosar.org/schema/r4.0 AUTOSAR_4-2-2.xsd',
        },
        AutosarVersion.AR_4_5_0: {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '': 'http://autosar.org/schema/r4.0',
            'schemaLocation': 'http://autosar.org/schema/r4.0 AUTOSAR_00050.xsd',
        },
    }
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize ECUC generator.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    def generate(
        self,
        project: ECUCProject,
        output_path: str,
        pretty_print: bool = True
    ) -> None:
        """
        Generate ECUC configuration ARXML file.
        
        Args:
            project: ECUC project to generate
            output_path: Path to output ARXML file
            pretty_print: If True, format XML with indentation
            
        Raises:
            GeneratorException: If generation fails
        """
        try:
            self.logger.info(f"Generating ECUC ARXML: {output_path}")
            
            # Create XML structure
            root = self._create_autosar_root(project.autosar_version)
            
            # Add AR-PACKAGES
            ar_packages = ET.SubElement(root, 'AR-PACKAGES')
            
            # Create main package
            main_package = self._create_package(
                ar_packages,
                project.short_name,
                project.name or project.short_name
            )
            
            # Add ECUC value collection
            self._generate_ecuc_value_collection(
                main_package,
                project.value_collection
            )
            
            # Write to file
            self._write_xml(root, output_path, pretty_print)
            
            self.logger.info(f"ECUC ARXML generated successfully: {output_path}")
            
        except Exception as e:
            raise GeneratorException(f"Failed to generate ECUC ARXML: {e}") from e
    
    def _create_autosar_root(self, version: AutosarVersion) -> ET.Element:
        """Create AUTOSAR root element with proper namespaces."""
        namespaces = self.NAMESPACES[version]
        
        # Create root with namespace
        root = ET.Element('AUTOSAR')
        root.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                 namespaces['schemaLocation'])
        
        # Add schema version
        if version == AutosarVersion.AR_4_2_2:
            schema_version = ET.SubElement(root, 'ADMIN-DATA')
            doc_revisions = ET.SubElement(schema_version, 'DOC-REVISIONS')
            doc_revision = ET.SubElement(doc_revisions, 'DOC-REVISION')
            ET.SubElement(doc_revision, 'REVISION-LABEL').text = '4.2.2'
        
        return root
    
    def _create_package(
        self,
        parent: ET.Element,
        short_name: str,
        long_name: Optional[str] = None
    ) -> ET.Element:
        """Create an AR-PACKAGE element."""
        package = ET.SubElement(parent, 'AR-PACKAGE')
        ET.SubElement(package, 'SHORT-NAME').text = short_name
        
        if long_name:
            long_name_elem = ET.SubElement(package, 'LONG-NAME')
            l4 = ET.SubElement(long_name_elem, 'L-4')
            l4.set('L', 'EN')
            l4.text = long_name
        
        return package
    
    def _generate_ecuc_value_collection(
        self,
        parent: ET.Element,
        collection: ECUCValueCollection
    ) -> None:
        """Generate ECUC-VALUE-COLLECTION element."""
        elements = ET.SubElement(parent, 'ELEMENTS')
        ecuc_value_collection = ET.SubElement(elements, 'ECUC-VALUE-COLLECTION')
        
        # Add SHORT-NAME
        ET.SubElement(ecuc_value_collection, 'SHORT-NAME').text = collection.short_name
        
        # Add UUID if present
        if collection.uuid:
            ET.SubElement(ecuc_value_collection, 'UUID').text = collection.uuid
        
        # Add ECU-EXTRACT-VERSION
        ET.SubElement(ecuc_value_collection, 'ECU-EXTRACT-VERSION').text = \
            collection.ecu_extract_version
        
        # Add modules
        if collection.modules:
            ecuc_values = ET.SubElement(ecuc_value_collection, 'ECUC-VALUES')
            
            for module in collection.modules:
                self._generate_module_configuration(ecuc_values, module)
    
    def _generate_module_configuration(
        self,
        parent: ET.Element,
        module: ECUCModuleConfigurationValues
    ) -> None:
        """Generate ECUC-MODULE-CONFIGURATION-VALUES element."""
        module_config = ET.SubElement(parent, 'ECUC-MODULE-CONFIGURATION-VALUES')
        
        # Add SHORT-NAME
        ET.SubElement(module_config, 'SHORT-NAME').text = module.short_name
        
        # Add UUID
        if module.uuid:
            ET.SubElement(module_config, 'UUID').text = module.uuid
        
        # Add DEFINITION-REF
        definition_ref = ET.SubElement(module_config, 'DEFINITION-REF')
        definition_ref.set('DEST', 'ECUC-MODULE-DEF')
        definition_ref.text = module.module_def_ref
        
        # Add IMPLEMENTATION-CONFIG-VARIANT
        ET.SubElement(module_config, 'IMPLEMENTATION-CONFIG-VARIANT').text = \
            module.implementation_config_variant
        
        # Add containers
        if module.containers:
            containers = ET.SubElement(module_config, 'CONTAINERS')
            
            for container in module.containers:
                self._generate_container(containers, container)
    
    def _generate_container(
        self,
        parent: ET.Element,
        container: ECUCContainerValue
    ) -> None:
        """Generate ECUC-CONTAINER-VALUE element."""
        container_elem = ET.SubElement(parent, 'ECUC-CONTAINER-VALUE')
        
        # Add SHORT-NAME
        ET.SubElement(container_elem, 'SHORT-NAME').text = container.short_name
        
        # Add UUID
        if container.uuid:
            ET.SubElement(container_elem, 'UUID').text = container.uuid
        
        # Add DEFINITION-REF
        definition_ref = ET.SubElement(container_elem, 'DEFINITION-REF')
        definition_ref.set('DEST', 'ECUC-PARAM-CONF-CONTAINER-DEF')
        definition_ref.text = container.definition_ref
        
        # Add parameters
        if container.parameters:
            parameter_values = ET.SubElement(container_elem, 'PARAMETER-VALUES')
            
            for param in container.parameters:
                self._generate_parameter(parameter_values, param)
        
        # Add sub-containers
        if container.sub_containers:
            sub_containers = ET.SubElement(container_elem, 'SUB-CONTAINERS')
            
            for sub_container in container.sub_containers:
                self._generate_container(sub_containers, sub_container)
    
    def _generate_parameter(
        self,
        parent: ET.Element,
        param: ECUCParameterValue
    ) -> None:
        """Generate parameter value element based on type."""
        # Determine element name based on parameter type
        if param.value_type == ECUCParameterType.INTEGER:
            param_elem = ET.SubElement(parent, 'ECUC-NUMERICAL-PARAM-VALUE')
        elif param.value_type == ECUCParameterType.FLOAT:
            param_elem = ET.SubElement(parent, 'ECUC-NUMERICAL-PARAM-VALUE')
        elif param.value_type == ECUCParameterType.BOOLEAN:
            param_elem = ET.SubElement(parent, 'ECUC-NUMERICAL-PARAM-VALUE')
        elif param.value_type == ECUCParameterType.STRING:
            param_elem = ET.SubElement(parent, 'ECUC-TEXTUAL-PARAM-VALUE')
        elif param.value_type == ECUCParameterType.REFERENCE:
            param_elem = ET.SubElement(parent, 'ECUC-REFERENCE-VALUE')
        else:
            param_elem = ET.SubElement(parent, 'ECUC-TEXTUAL-PARAM-VALUE')
        
        # Add SHORT-NAME
        ET.SubElement(param_elem, 'SHORT-NAME').text = param.short_name
        
        # Add UUID
        if param.uuid:
            ET.SubElement(param_elem, 'UUID').text = param.uuid
        
        # Add DEFINITION-REF
        definition_ref = ET.SubElement(param_elem, 'DEFINITION-REF')
        
        if param.value_type == ECUCParameterType.REFERENCE:
            definition_ref.set('DEST', 'ECUC-REFERENCE-DEF')
        else:
            definition_ref.set('DEST', 'ECUC-PARAM-CONF-CONTAINER-DEF')
        
        definition_ref.text = param.definition_ref
        
        # Add value
        if param.value_type == ECUCParameterType.REFERENCE:
            if param.reference_value:
                value_ref = ET.SubElement(param_elem, 'VALUE-REF')
                value_ref.set('DEST', 'ECUC-CONTAINER-VALUE')
                value_ref.text = param.reference_value
        else:
            if param.value is not None:
                value_elem = ET.SubElement(param_elem, 'VALUE')
                
                # Convert value to string
                if param.value_type == ECUCParameterType.BOOLEAN:
                    value_elem.text = 'true' if param.value else 'false'
                else:
                    value_elem.text = str(param.value)
    
    def _write_xml(
        self,
        root: ET.Element,
        output_path: str,
        pretty_print: bool
    ) -> None:
        """Write XML to file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if pretty_print:
            # Use minidom for pretty printing
            xml_str = ET.tostring(root, encoding='unicode')
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
            
            with path.open('wb') as f:
                f.write(pretty_xml)
        else:
            # Write directly
            tree = ET.ElementTree(root)
            tree.write(
                output_path,
                encoding='utf-8',
                xml_declaration=True,
                method='xml'
            )
    
    def generate_to_string(
        self,
        project: ECUCProject,
        pretty_print: bool = True
    ) -> str:
        """
        Generate ECUC configuration as string.
        
        Args:
            project: ECUC project to generate
            pretty_print: If True, format XML with indentation
            
        Returns:
            Generated ARXML as string
            
        Raises:
            GeneratorException: If generation fails
        """
        try:
            self.logger.debug("Generating ECUC ARXML to string")
            
            # Create XML structure
            root = self._create_autosar_root(project.autosar_version)
            ar_packages = ET.SubElement(root, 'AR-PACKAGES')
            
            main_package = self._create_package(
                ar_packages,
                project.short_name,
                project.name or project.short_name
            )
            
            self._generate_ecuc_value_collection(
                main_package,
                project.value_collection
            )
            
            # Convert to string
            if pretty_print:
                xml_str = ET.tostring(root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                return dom.toprettyxml(indent='  ')
            else:
                return ET.tostring(root, encoding='unicode')
            
        except Exception as e:
            raise GeneratorException(
                f"Failed to generate ECUC ARXML string: {e}"
            ) from e
