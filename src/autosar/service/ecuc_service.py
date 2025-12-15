"""
ECUC Service - Main service for handling ECUC configuration generation.

This service:
1. Loads data from various sources (DBC, LDF, XLSX, ARXML)
2. Merges and validates the data
3. Generates ECUC configuration values
4. Supports AUTOSAR AR4.2.2 and AR4.5
"""

from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import logging
from datetime import datetime

from ..model import (
    CANDatabase, LINNetwork, EcuConfiguration,
    ECUCProject, ECUCValueCollection, ECUCModuleConfigurationValues,
    ECUCContainerValue, ECUCParameterValue,
    AutosarVersion, ECUCParameterType
)
from ..loader import DBCLoader, LDFLoader


class ECUCServiceException(Exception):
    """Base exception for ECUC service errors."""
    pass


class DataMergeError(ECUCServiceException):
    """Raised when data merging fails."""
    pass


class ValidationError(ECUCServiceException):
    """Raised when validation fails."""
    pass


class GenerationError(ECUCServiceException):
    """Raised when ECUC generation fails."""
    pass


class ECUCService:
    """
    Service for managing ECUC configuration generation.
    
    Handles loading data from multiple sources, merging, validation,
    and generating ECUC configuration values for AUTOSAR.
    """
    
    def __init__(
        self,
        autosar_version: AutosarVersion = AutosarVersion.AR_4_2_2,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize ECUC service.
        
        Args:
            autosar_version: Target AUTOSAR version
            logger: Optional logger instance
        """
        self.autosar_version = autosar_version
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Data containers
        self.can_networks: Dict[str, CANDatabase] = {}
        self.lin_networks: Dict[str, LINNetwork] = {}
        self.ecu_configs: Dict[str, EcuConfiguration] = {}
        
        # Source tracking
        self.source_files: List[str] = []
        
        # Loaders
        self._dbc_loader = DBCLoader(logger=self.logger)
        self._ldf_loader = LDFLoader(logger=self.logger)
    
    def load_dbc(self, file_path: str, network_name: Optional[str] = None) -> CANDatabase:
        """
        Load CAN network from DBC file.
        
        Args:
            file_path: Path to DBC file
            network_name: Optional network name (defaults to filename)
            
        Returns:
            Loaded CAN network
            
        Raises:
            ECUCServiceException: If loading fails
        """
        try:
            self.logger.info(f"Loading DBC file: {file_path}")
            network = self._dbc_loader.load_and_convert(file_path)
            
            # Use provided name or generate from filename
            if network_name:
                network.name = network_name
                network.short_name = network_name
            elif not network.name:
                network.name = Path(file_path).stem
                network.short_name = Path(file_path).stem
            
            # Store network
            self.can_networks[network.name] = network
            self.source_files.append(str(Path(file_path).resolve()))
            
            self.logger.info(
                f"Loaded CAN network '{network.name}' with "
                f"{len(network.messages)} messages"
            )
            
            return network
            
        except Exception as e:
            raise ECUCServiceException(f"Failed to load DBC file: {e}") from e
    
    def load_ldf(self, file_path: str, network_name: Optional[str] = None) -> LINNetwork:
        """
        Load LIN network from LDF file.
        
        Args:
            file_path: Path to LDF file
            network_name: Optional network name (defaults to filename)
            
        Returns:
            Loaded LIN network
            
        Raises:
            ECUCServiceException: If loading fails
        """
        try:
            self.logger.info(f"Loading LDF file: {file_path}")
            network = self._ldf_loader.load_and_convert(file_path)
            
            # Use provided name or generate from filename
            if network_name:
                network.name = network_name
                network.short_name = network_name
            elif not network.name:
                network.name = Path(file_path).stem
                network.short_name = Path(file_path).stem
            
            # Store network
            self.lin_networks[network.name] = network
            self.source_files.append(str(Path(file_path).resolve()))
            
            self.logger.info(
                f"Loaded LIN network '{network.name}' with "
                f"{len(network.frames)} frames"
            )
            
            return network
            
        except Exception as e:
            raise ECUCServiceException(f"Failed to load LDF file: {e}") from e
    
    def validate_data(self) -> bool:
        """
        Validate loaded data for consistency.
        
        Checks:
        - No duplicate IDs within same network
        - Signal references are valid
        - Frame/message sizes are correct
        
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        self.logger.info("Validating loaded data...")
        
        errors = []
        
        # Validate CAN networks
        for network_name, network in self.can_networks.items():
            self.logger.debug(f"Validating CAN network: {network_name}")
            
            # Check for duplicate message IDs
            message_ids: Set[int] = set()
            for msg in network.messages:
                if msg.message_id in message_ids:
                    errors.append(
                        f"Duplicate CAN message ID {msg.message_id:#x} "
                        f"in network '{network_name}'"
                    )
                message_ids.add(msg.message_id)
                
                # Validate signals fit in message
                for sig in msg.signals:
                    if sig.start_bit + sig.length > msg.length * 8:
                        errors.append(
                            f"Signal '{sig.name}' exceeds message '{msg.name}' "
                            f"size in network '{network_name}'"
                        )
        
        # Validate LIN networks
        for network_name, network in self.lin_networks.items():
            self.logger.debug(f"Validating LIN network: {network_name}")
            
            # Check for duplicate frame IDs
            frame_ids: Set[int] = set()
            for frame in network.frames:
                if frame.frame_id in frame_ids:
                    errors.append(
                        f"Duplicate LIN frame ID {frame.frame_id:#x} "
                        f"in network '{network_name}'"
                    )
                frame_ids.add(frame.frame_id)
                
                # Validate signals fit in frame
                for sig in frame.signals:
                    if sig.start_bit + sig.length > frame.length * 8:
                        errors.append(
                            f"Signal '{sig.name}' exceeds frame '{frame.name}' "
                            f"size in network '{network_name}'"
                        )
        
        if errors:
            error_msg = "Validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            self.logger.error(error_msg)
            raise ValidationError(error_msg)
        
        self.logger.info("Validation passed successfully")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of loaded data.
        
        Returns:
            Dictionary with statistics
        """
        summary = {
            'autosar_version': self.autosar_version.value,
            'source_files': len(self.source_files),
            'can_networks': len(self.can_networks),
            'lin_networks': len(self.lin_networks),
            'ecu_configs': len(self.ecu_configs),
            'networks': {},
        }
        
        # CAN network details
        for name, network in self.can_networks.items():
            summary['networks'][name] = {
                'type': 'CAN',
                'baudrate': network.baudrate,
                'messages': len(network.messages),
                'signals': sum(len(msg.signals) for msg in network.messages),
                'nodes': len(network.nodes),
            }
        
        # LIN network details
        for name, network in self.lin_networks.items():
            summary['networks'][name] = {
                'type': 'LIN',
                'baudrate': network.baudrate,
                'frames': len(network.frames),
                'signals': sum(len(frame.signals) for frame in network.frames),
                'nodes': len(network.nodes),
            }
        
        return summary
    
    def generate_ecuc_project(
        self,
        project_name: str,
        ecu_instance: str,
        modules: Optional[List[str]] = None
    ) -> ECUCProject:
        """
        Generate ECUC project from loaded data.
        
        Args:
            project_name: Name of the project
            ecu_instance: ECU instance name
            modules: List of module names to generate (None = all supported)
            
        Returns:
            Complete ECUC project
            
        Raises:
            GenerationError: If generation fails
        """
        try:
            self.logger.info(f"Generating ECUC project '{project_name}'...")
            
            # Validate data first
            self.validate_data()
            
            # Create value collection
            value_collection = ECUCValueCollection(
                short_name=f"{project_name}_EcucValues",
                name=f"{project_name} ECUC Values",
                autosar_version=self.autosar_version,
                uuid=self._generate_uuid(),
            )
            
            # Determine which modules to generate
            if modules is None:
                modules = []
                if self.can_networks:
                    modules.extend(['CanIf', 'Can', 'CanTp', 'PduR'])
                if self.lin_networks:
                    modules.extend(['LinIf', 'Lin'])
            
            # Generate modules
            for module_name in modules:
                self.logger.info(f"Generating module: {module_name}")
                
                if module_name == 'CanIf':
                    module = self._generate_canif_module()
                elif module_name == 'Can':
                    module = self._generate_can_module()
                elif module_name == 'LinIf':
                    module = self._generate_linif_module()
                elif module_name == 'Lin':
                    module = self._generate_lin_module()
                else:
                    self.logger.warning(f"Module '{module_name}' not yet implemented")
                    continue
                
                value_collection.add_module(module)
            
            # Create project
            project = ECUCProject(
                short_name=project_name,
                name=project_name,
                uuid=self._generate_uuid(),
                autosar_version=self.autosar_version,
                ecu_instance=ecu_instance,
                value_collection=value_collection,
                source_files=self.source_files.copy(),
                metadata={
                    'generated_at': datetime.now().isoformat(),
                    'generator': 'ECUC Configurator Service',
                    'version': '1.0.0',
                }
            )
            
            self.logger.info(
                f"ECUC project generated with {len(value_collection.modules)} modules"
            )
            
            return project
            
        except Exception as e:
            raise GenerationError(f"Failed to generate ECUC project: {e}") from e
    
    def _generate_canif_module(self) -> ECUCModuleConfigurationValues:
        """Generate CanIf module configuration."""
        module = ECUCModuleConfigurationValues(
            short_name="CanIf",
            name="CAN Interface Configuration",
            uuid=self._generate_uuid(),
            module_def_ref="/AUTOSAR/EcucDefs/CanIf",
        )
        
        # Create CanIfInitCfg container
        init_cfg = ECUCContainerValue(
            short_name="CanIfInitCfg",
            name="CAN Interface Initial Configuration",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg",
        )
        
        # Generate configuration for each CAN network
        for network_name, network in self.can_networks.items():
            self.logger.debug(f"Generating CanIf config for network: {network_name}")
            
            # Create CanIfCtrlCfg for each network
            ctrl_cfg = self._generate_canif_ctrl_cfg(network_name, network)
            init_cfg.add_sub_container(ctrl_cfg)
            
            # Generate TX PDU configs
            for msg in network.messages:
                if msg.is_tx():  # If this ECU transmits this message
                    tx_pdu = self._generate_canif_tx_pdu(network_name, msg)
                    init_cfg.add_sub_container(tx_pdu)
            
            # Generate RX PDU configs
            for msg in network.messages:
                if msg.is_rx():  # If this ECU receives this message
                    rx_pdu = self._generate_canif_rx_pdu(network_name, msg)
                    init_cfg.add_sub_container(rx_pdu)
        
        module.add_container(init_cfg)
        return module
    
    def _generate_can_module(self) -> ECUCModuleConfigurationValues:
        """Generate Can module configuration."""
        module = ECUCModuleConfigurationValues(
            short_name="Can",
            name="CAN Driver Configuration",
            uuid=self._generate_uuid(),
            module_def_ref="/AUTOSAR/EcucDefs/Can",
        )
        
        # Create CanGeneral container
        general = ECUCContainerValue(
            short_name="CanGeneral",
            name="CAN General Configuration",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Can/CanGeneral",
        )
        
        # Add general parameters
        general.add_parameter(ECUCParameterValue(
            short_name="CanDevErrorDetect",
            name="Development Error Detection",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Can/CanGeneral/CanDevErrorDetect",
            value_type=ECUCParameterType.BOOLEAN,
            value=True,
        ))
        
        module.add_container(general)
        
        # Create CanConfigSet
        config_set = ECUCContainerValue(
            short_name="CanConfigSet",
            name="CAN Configuration Set",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Can/CanConfigSet",
        )
        
        # Generate controller configs for each network
        for network_name, network in self.can_networks.items():
            ctrl = self._generate_can_controller(network_name, network)
            config_set.add_sub_container(ctrl)
        
        module.add_container(config_set)
        return module
    
    def _generate_linif_module(self) -> ECUCModuleConfigurationValues:
        """Generate LinIf module configuration."""
        module = ECUCModuleConfigurationValues(
            short_name="LinIf",
            name="LIN Interface Configuration",
            uuid=self._generate_uuid(),
            module_def_ref="/AUTOSAR/EcucDefs/LinIf",
        )
        
        # Create LinIfGlobalConfig
        global_cfg = ECUCContainerValue(
            short_name="LinIfGlobalConfig",
            name="LIN Interface Global Configuration",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/LinIf/LinIfGlobalConfig",
        )
        
        # Add global parameters
        global_cfg.add_parameter(ECUCParameterValue(
            short_name="LinIfDevErrorDetect",
            name="Development Error Detection",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/LinIf/LinIfGlobalConfig/LinIfDevErrorDetect",
            value_type=ECUCParameterType.BOOLEAN,
            value=True,
        ))
        
        module.add_container(global_cfg)
        
        # Generate configuration for each LIN network
        for network_name, network in self.lin_networks.items():
            channel = self._generate_linif_channel(network_name, network)
            module.add_container(channel)
        
        return module
    
    def _generate_lin_module(self) -> ECUCModuleConfigurationValues:
        """Generate Lin module configuration."""
        module = ECUCModuleConfigurationValues(
            short_name="Lin",
            name="LIN Driver Configuration",
            uuid=self._generate_uuid(),
            module_def_ref="/AUTOSAR/EcucDefs/Lin",
        )
        
        # Create LinGeneral container
        general = ECUCContainerValue(
            short_name="LinGeneral",
            name="LIN General Configuration",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Lin/LinGeneral",
        )
        
        general.add_parameter(ECUCParameterValue(
            short_name="LinDevErrorDetect",
            name="Development Error Detection",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Lin/LinGeneral/LinDevErrorDetect",
            value_type=ECUCParameterType.BOOLEAN,
            value=True,
        ))
        
        module.add_container(general)
        
        # Generate channel configs
        for network_name, network in self.lin_networks.items():
            channel = self._generate_lin_channel(network_name, network)
            module.add_container(channel)
        
        return module
    
    # Helper methods for generating specific containers
    
    def _generate_canif_ctrl_cfg(
        self,
        network_name: str,
        network: CANDatabase
    ) -> ECUCContainerValue:
        """Generate CanIfCtrlCfg container."""
        container = ECUCContainerValue(
            short_name=f"CanIfCtrlCfg_{network_name}",
            name=f"Controller Config for {network_name}",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfCtrlCfg",
        )
        
        # Add controller ID parameter
        container.add_parameter(ECUCParameterValue(
            short_name="CanIfCtrlId",
            name="Controller ID",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfCtrlCfg/CanIfCtrlId",
            value_type=ECUCParameterType.INTEGER,
            value=0,  # Would need to be determined from ECU config
        ))
        
        return container
    
    def _generate_canif_tx_pdu(
        self,
        network_name: str,
        message
    ) -> ECUCContainerValue:
        """Generate CanIfTxPduCfg container."""
        container = ECUCContainerValue(
            short_name=f"CanIfTxPdu_{network_name}_{message.name}",
            name=f"TX PDU for {message.name}",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfTxPduCfg",
        )
        
        container.add_parameter(ECUCParameterValue(
            short_name="CanIfTxPduId",
            name="TX PDU ID",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfTxPduCfg/CanIfTxPduId",
            value_type=ECUCParameterType.INTEGER,
            value=message.message_id,
        ))
        
        container.add_parameter(ECUCParameterValue(
            short_name="CanIfTxPduCanId",
            name="CAN ID",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfTxPduCfg/CanIfTxPduCanId",
            value_type=ECUCParameterType.INTEGER,
            value=message.message_id,
        ))
        
        return container
    
    def _generate_canif_rx_pdu(
        self,
        network_name: str,
        message
    ) -> ECUCContainerValue:
        """Generate CanIfRxPduCfg container."""
        container = ECUCContainerValue(
            short_name=f"CanIfRxPdu_{network_name}_{message.name}",
            name=f"RX PDU for {message.name}",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfRxPduCfg",
        )
        
        container.add_parameter(ECUCParameterValue(
            short_name="CanIfRxPduId",
            name="RX PDU ID",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfRxPduCfg/CanIfRxPduId",
            value_type=ECUCParameterType.INTEGER,
            value=message.message_id,
        ))
        
        container.add_parameter(ECUCParameterValue(
            short_name="CanIfRxPduCanId",
            name="CAN ID",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/CanIf/CanIfInitCfg/CanIfRxPduCfg/CanIfRxPduCanId",
            value_type=ECUCParameterType.INTEGER,
            value=message.message_id,
        ))
        
        return container
    
    def _generate_can_controller(
        self,
        network_name: str,
        network: CANDatabase
    ) -> ECUCContainerValue:
        """Generate CanController container."""
        container = ECUCContainerValue(
            short_name=f"CanController_{network_name}",
            name=f"CAN Controller for {network_name}",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Can/CanConfigSet/CanController",
        )
        
        container.add_parameter(ECUCParameterValue(
            short_name="CanControllerId",
            name="Controller ID",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Can/CanConfigSet/CanController/CanControllerId",
            value_type=ECUCParameterType.INTEGER,
            value=0,
        ))
        
        container.add_parameter(ECUCParameterValue(
            short_name="CanControllerBaudRate",
            name="Baudrate",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Can/CanConfigSet/CanController/CanControllerBaudRate",
            value_type=ECUCParameterType.INTEGER,
            value=network.baudrate,
        ))
        
        return container
    
    def _generate_linif_channel(
        self,
        network_name: str,
        network: LINNetwork
    ) -> ECUCContainerValue:
        """Generate LinIfChannel container."""
        container = ECUCContainerValue(
            short_name=f"LinIfChannel_{network_name}",
            name=f"LIN Channel for {network_name}",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/LinIf/LinIfChannel",
        )
        
        # Add frames
        for frame in network.frames:
            frame_cfg = ECUCContainerValue(
                short_name=f"LinIfFrame_{frame.name}",
                name=f"Frame {frame.name}",
                uuid=self._generate_uuid(),
                definition_ref="/AUTOSAR/EcucDefs/LinIf/LinIfChannel/LinIfFrame",
            )
            
            frame_cfg.add_parameter(ECUCParameterValue(
                short_name="LinIfFrameType",
                name="Frame Type",
                uuid=self._generate_uuid(),
                definition_ref="/AUTOSAR/EcucDefs/LinIf/LinIfChannel/LinIfFrame/LinIfFrameType",
                value_type=ECUCParameterType.STRING,
                value=frame.frame_type.value if hasattr(frame.frame_type, 'value') else str(frame.frame_type),
            ))
            
            container.add_sub_container(frame_cfg)
        
        return container
    
    def _generate_lin_channel(
        self,
        network_name: str,
        network: LINNetwork
    ) -> ECUCContainerValue:
        """Generate LinChannel container."""
        container = ECUCContainerValue(
            short_name=f"LinChannel_{network_name}",
            name=f"LIN Channel for {network_name}",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Lin/LinChannel",
        )
        
        container.add_parameter(ECUCParameterValue(
            short_name="LinChannelBaudRate",
            name="Baudrate",
            uuid=self._generate_uuid(),
            definition_ref="/AUTOSAR/EcucDefs/Lin/LinChannel/LinChannelBaudRate",
            value_type=ECUCParameterType.INTEGER,
            value=int(network.baudrate),
        ))
        
        return container
    
    def _generate_uuid(self) -> str:
        """Generate a UUID for AUTOSAR elements."""
        import uuid
        return str(uuid.uuid4())
    
    def clear(self) -> None:
        """Clear all loaded data."""
        self.can_networks.clear()
        self.lin_networks.clear()
        self.ecu_configs.clear()
        self.source_files.clear()
        
        # Clear loader caches if they have them
        if hasattr(self._dbc_loader, 'clear_cache'):
            self._dbc_loader.clear_cache()
        if hasattr(self._ldf_loader, 'clear_cache'):
            self._ldf_loader.clear_cache()
        
        self.logger.info("Service data cleared")
