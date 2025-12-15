"""
Tests for ECUC Service.
"""

import pytest
from pathlib import Path
from autosar.service import (
    ECUCService, ValidationError, GenerationError
)
from autosar.model import (
    AutosarVersion, ECUCProject, CANDatabase, LINNetwork
)


class TestECUCService:
    """Test suite for ECUC Service."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = ECUCService()
        assert service.autosar_version == AutosarVersion.AR_4_2_2
        assert len(service.can_networks) == 0
        assert len(service.lin_networks) == 0
        
        # Test with AR4.5
        service_45 = ECUCService(autosar_version=AutosarVersion.AR_4_5_0)
        assert service_45.autosar_version == AutosarVersion.AR_4_5_0
    
    def test_service_initialization_ar45(self):
        """Test service initialization with AR4.5."""
        service = ECUCService(autosar_version=AutosarVersion.AR_4_5_0)
        assert service.autosar_version == AutosarVersion.AR_4_5_0
    
    def test_get_summary_empty(self):
        """Test summary with no data loaded."""
        service = ECUCService()
        summary = service.get_summary()
        
        assert summary['autosar_version'] == '4.2.2'
        assert summary['can_networks'] == 0
        assert summary['lin_networks'] == 0
        assert summary['source_files'] == 0
        assert len(summary['networks']) == 0
    
    def test_validate_empty_data(self):
        """Test validation with no data."""
        service = ECUCService()
        assert service.validate_data() is True
    
    def test_clear_service(self):
        """Test clearing service data."""
        service = ECUCService()
        
        # Manually add some data
        from autosar.model import CANDatabase, CANMessage
        network = CANDatabase(
            name="TestNetwork",
            short_name="TestNetwork",
            baudrate=500000,
            uuid="test-uuid"
        )
        service.can_networks["TestNetwork"] = network
        service.source_files.append("test.dbc")
        
        assert len(service.can_networks) == 1
        assert len(service.source_files) == 1
        
        # Clear
        service.clear()
        
        assert len(service.can_networks) == 0
        assert len(service.source_files) == 0
    
    def test_generate_ecuc_project_empty(self):
        """Test generating ECUC project with no data."""
        service = ECUCService()
        
        # Should succeed even with no data
        project = service.generate_ecuc_project(
            project_name="TestProject",
            ecu_instance="ECU1",
            modules=[]  # No modules
        )
        
        assert project.short_name == "TestProject"
        assert project.ecu_instance == "ECU1"
        assert project.autosar_version == AutosarVersion.AR_4_2_2
        assert len(project.value_collection.modules) == 0
    
    def test_generate_ecuc_project_metadata(self):
        """Test ECUC project metadata."""
        service = ECUCService()
        
        project = service.generate_ecuc_project(
            project_name="TestProject",
            ecu_instance="ECU1",
            modules=[]
        )
        
        assert 'generated_at' in project.metadata
        assert 'generator' in project.metadata
        assert project.metadata['generator'] == 'ECUC Configurator Service'
    
    def test_validation_duplicate_can_ids(self):
        """Test validation catches duplicate CAN IDs."""
        service = ECUCService()
        
        from autosar.model import CANDatabase, CANMessage, CANSignal
        
        # Create network with duplicate message IDs
        network = CANDatabase(
            name="TestNetwork",
            short_name="TestNetwork",
            baudrate=500000,
            uuid="test-uuid"
        )
        
        msg1 = CANMessage(
            name="Msg1",
            short_name="Msg1",
            message_id=0x100,
            length=8,
            uuid="msg1-uuid"
        )
        
        msg2 = CANMessage(
            name="Msg2",
            short_name="Msg2",
            message_id=0x100,  # Duplicate ID!
            length=8,
            uuid="msg2-uuid"
        )
        
        network.messages = [msg1, msg2]
        service.can_networks["TestNetwork"] = network
        
        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            service.validate_data()
        
        assert "Duplicate CAN message ID" in str(exc_info.value)
    
    def test_validation_signal_exceeds_message(self):
        """Test validation catches signals exceeding message size."""
        from autosar.model import CANDatabase, CANMessage, CANSignal
        from pydantic import ValidationError as PydanticValidationError
        
        # Signal validation happens at model creation time (Pydantic validation)
        # This test verifies that CANSignal itself validates boundaries
        
        # This should raise ValidationError when creating the signal
        with pytest.raises(PydanticValidationError) as exc_info:
            signal = CANSignal(
                name="TooBig",
                short_name="TooBig",
                start_bit=60,  # Start at bit 60
                length=16,  # 16 bits, so ends at bit 76 (exceeds 64-bit message)
                uuid="sig-uuid"
            )
        
        # Verify error message mentions boundary
        assert "beyond message boundary" in str(exc_info.value)
    
    def test_validation_duplicate_lin_ids(self):
        """Test validation catches duplicate LIN frame IDs."""
        service = ECUCService()
        
        from autosar.model import (
            LINNetwork, LINFrame, LINNode, LINNodeType, FrameType
        )
        
        network = LINNetwork(
            name="TestLIN",
            short_name="TestLIN",
            baudrate=19200,
            protocol_version="2.1",
            uuid="lin-uuid"
        )
        
        frame1 = LINFrame(
            name="Frame1",
            short_name="Frame1",
            frame_id=0x10,
            length=2,
            frame_type=FrameType.UNCONDITIONAL,
            uuid="frame1-uuid"
        )
        
        frame2 = LINFrame(
            name="Frame2",
            short_name="Frame2",
            frame_id=0x10,  # Duplicate ID!
            length=2,
            frame_type=FrameType.UNCONDITIONAL,
            uuid="frame2-uuid"
        )
        
        network.frames = [frame1, frame2]
        service.lin_networks["TestLIN"] = network
        
        # Validation should fail
        with pytest.raises(ValidationError) as exc_info:
            service.validate_data()
        
        assert "Duplicate LIN frame ID" in str(exc_info.value)


class TestECUCServiceWithData:
    """Test ECUC service with actual data."""
    
    @pytest.fixture
    def service_with_can(self):
        """Create service with CAN network."""
        service = ECUCService()
        
        from autosar.model import (
            CANDatabase, CANMessage, CANSignal, CANNode
        )
        
        network = CANDatabase(
            name="CAN1",
            short_name="CAN1",
            baudrate=500000,
            uuid="can1-uuid"
        )
        
        # Add messages
        msg1 = CANMessage(
            name="EngineData",
            short_name="EngineData",
            message_id=0x100,
            length=8,
            uuid="msg1-uuid"
        )
        
        sig1 = CANSignal(
            name="EngineSpeed",
            short_name="EngineSpeed",
            start_bit=0,
            length=16,
            uuid="sig1-uuid"
        )
        
        msg1.signals = [sig1]
        network.messages = [msg1]
        
        # Add node
        node = CANNode(
            name="ECU1",
            short_name="ECU1",
            uuid="node1-uuid"
        )
        network.nodes = [node]
        
        service.can_networks["CAN1"] = network
        
        return service
    
    def test_get_summary_with_can(self, service_with_can):
        """Test summary with CAN data."""
        summary = service_with_can.get_summary()
        
        assert summary['can_networks'] == 1
        assert 'CAN1' in summary['networks']
        assert summary['networks']['CAN1']['type'] == 'CAN'
        assert summary['networks']['CAN1']['messages'] == 1
        assert summary['networks']['CAN1']['signals'] == 1
        assert summary['networks']['CAN1']['nodes'] == 1
    
    def test_validate_with_valid_can(self, service_with_can):
        """Test validation with valid CAN data."""
        assert service_with_can.validate_data() is True
    
    def test_generate_canif_module(self, service_with_can):
        """Test generating CanIf module."""
        project = service_with_can.generate_ecuc_project(
            project_name="TestProject",
            ecu_instance="ECU1",
            modules=['CanIf']
        )
        
        assert len(project.value_collection.modules) >= 1
        
        # Find CanIf module
        canif_module = None
        for module in project.value_collection.modules:
            if module.short_name == 'CanIf':
                canif_module = module
                break
        
        assert canif_module is not None
        assert canif_module.module_def_ref == "/AUTOSAR/EcucDefs/CanIf"
    
    def test_generate_multiple_modules(self, service_with_can):
        """Test generating multiple modules."""
        project = service_with_can.generate_ecuc_project(
            project_name="TestProject",
            ecu_instance="ECU1",
            modules=['CanIf', 'Can']
        )
        
        module_names = [m.short_name for m in project.value_collection.modules]
        assert 'CanIf' in module_names
        assert 'Can' in module_names


class TestECUCServiceIntegration:
    """Integration tests for ECUC service."""
    
    def test_full_workflow_can(self):
        """Test complete workflow: create -> validate -> generate."""
        from autosar.model import (
            CANDatabase, CANMessage, CANSignal, CANNode, ByteOrder
        )
        
        service = ECUCService(autosar_version=AutosarVersion.AR_4_2_2)
        
        # Create network
        network = CANDatabase(
            name="BodyCAN",
            short_name="BodyCAN",
            baudrate=500000,
            uuid="body-can-uuid"
        )
        
        # Create message with signals
        door_msg = CANMessage(
            name="DoorStatus",
            short_name="DoorStatus",
            message_id=0x200,
            length=4,
            uuid="door-msg-uuid"
        )
        
        door_left = CANSignal(
            name="DoorLeft",
            short_name="DoorLeft",
            start_bit=0,
            length=8,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            uuid="door-left-uuid"
        )
        
        door_right = CANSignal(
            name="DoorRight",
            short_name="DoorRight",
            start_bit=8,
            length=8,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            uuid="door-right-uuid"
        )
        
        door_msg.signals = [door_left, door_right]
        network.messages = [door_msg]
        
        # Add to service
        service.can_networks["BodyCAN"] = network
        
        # Validate
        assert service.validate_data() is True
        
        # Generate project
        project = service.generate_ecuc_project(
            project_name="BodyECU",
            ecu_instance="BodyECU_Instance",
            modules=['CanIf', 'Can']
        )
        
        # Verify project
        assert project.short_name == "BodyECU"
        assert project.ecu_instance == "BodyECU_Instance"
        assert len(project.value_collection.modules) == 2
