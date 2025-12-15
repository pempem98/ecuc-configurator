"""
Test suite for AUTOSAR models.

Simple tests to verify model creation and validation.
"""

import pytest
from autosar.model import (
    # CAN
    CANDatabase, CANMessage, CANSignal, CANNode,
    # LIN
    LINNetwork, LINFrame, LINSignal, LINNode, LINNodeType,
    # ECU
    EcuConfiguration, Module, Container, Parameter, ParameterType,
    # AUTOSAR
    ARPackage, Component, PortInterface, DataElement,
    # Types
    ByteOrder, ValueType,
)


class TestCANModels:
    """Test CAN data models."""
    
    def test_can_signal_creation(self):
        """Test creating a CAN signal."""
        signal = CANSignal(
            name="VehicleSpeed",
            short_name="VehicleSpeed",
            start_bit=0,
            length=16,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            value_type=ValueType.UNSIGNED,
            factor=0.01,
            offset=0,
            min_value=0,
            max_value=655.35,
            unit="km/h",
        )
        
        assert signal.name == "VehicleSpeed"
        assert signal.length == 16
        assert signal.decode(10000) == 100.0  # 10000 * 0.01 = 100 km/h
    
    def test_can_message_creation(self):
        """Test creating a CAN message."""
        signal = CANSignal(
            name="EngineSpeed",
            short_name="EngineSpeed",
            start_bit=0,
            length=16,
        )
        
        message = CANMessage(
            name="Powertrain_01",
            short_name="Powertrain_01",
            message_id=0x100,
            dlc=8,
            signals=[signal],
            cycle_time=100,
        )
        
        assert message.message_id == 0x100
        assert message.dlc == 8
        assert len(message.signals) == 1
        assert message.get_signal("EngineSpeed") is not None
    
    def test_can_database(self):
        """Test creating a CAN database."""
        message = CANMessage(
            name="TestMsg",
            short_name="TestMsg",
            message_id=0x123,
            dlc=8,
        )
        
        node = CANNode(
            name="TestECU",
            short_name="TestECU",
            transmitted_messages=["TestMsg"],
        )
        
        db = CANDatabase(
            name="TestDB",
            version="1.0",
            messages=[message],
            nodes=[node],
        )
        
        assert len(db.messages) == 1
        assert len(db.nodes) == 1
        assert db.get_message_by_id(0x123) is not None
        assert db.get_node("TestECU") is not None


class TestLINModels:
    """Test LIN data models."""
    
    def test_lin_signal_creation(self):
        """Test creating a LIN signal."""
        signal = LINSignal(
            name="DoorStatus",
            short_name="DoorStatus",
            start_bit=0,
            length=8,
        )
        
        assert signal.name == "DoorStatus"
        assert signal.length == 8
    
    def test_lin_frame_creation(self):
        """Test creating a LIN frame."""
        signal = LINSignal(
            name="Status",
            short_name="Status",
            start_bit=0,
            length=8,
        )
        
        frame = LINFrame(
            name="StatusFrame",
            short_name="StatusFrame",
            frame_id=0x10,
            length=4,
            signals=[signal],
        )
        
        assert frame.frame_id == 0x10
        assert frame.length == 4
        assert len(frame.signals) == 1
    
    def test_lin_network(self):
        """Test creating a LIN network."""
        master = LINNode(
            name="Master",
            short_name="Master",
            node_type=LINNodeType.MASTER,
        )
        
        slave = LINNode(
            name="Slave1",
            short_name="Slave1",
            node_type=LINNodeType.SLAVE,
        )
        
        network = LINNetwork(
            name="LIN1",
            master_node=master,
            slave_nodes=[slave],
            speed=19.2,
        )
        
        assert network.master_node is not None
        assert len(network.slave_nodes) == 1
        assert network.get_node("Master") is not None


class TestECUModels:
    """Test ECU configuration models."""
    
    def test_parameter_creation(self):
        """Test creating a parameter."""
        param = Parameter(
            name="MaxBufferSize",
            short_name="MaxBufferSize",
            parameter_type=ParameterType.INTEGER,
            value=1024,
            min_value=0,
            max_value=4096,
        )
        
        assert param.name == "MaxBufferSize"
        assert param.value == 1024
    
    def test_container_creation(self):
        """Test creating a container."""
        param = Parameter(
            name="Param1",
            short_name="Param1",
            parameter_type=ParameterType.STRING,
            value="test",
        )
        
        container = Container(
            name="TestContainer",
            short_name="TestContainer",
            parameters=[param],
        )
        
        assert container.name == "TestContainer"
        assert len(container.parameters) == 1
        assert container.get_parameter("Param1") is not None
    
    def test_module_creation(self):
        """Test creating a module."""
        container = Container(
            name="Config",
            short_name="Config",
        )
        
        module = Module(
            name="CanIf",
            short_name="CanIf",
            version="1.0.0",
            containers=[container],
        )
        
        assert module.name == "CanIf"
        assert len(module.containers) == 1
    
    def test_ecu_configuration(self):
        """Test creating ECU configuration."""
        module = Module(
            name="TestModule",
            short_name="TestModule",
            version="1.0.0",
        )
        
        ecu = EcuConfiguration(
            name="TestECU",
            short_name="TestECU",
            version="1.0.0",
            modules=[module],
        )
        
        assert ecu.name == "TestECU"
        assert len(ecu.modules) == 1


class TestAUTOSARModels:
    """Test AUTOSAR models."""
    
    def test_data_element_creation(self):
        """Test creating a data element."""
        elem = DataElement(
            name="Speed",
            short_name="Speed",
            data_type="uint16",
        )
        
        assert elem.name == "Speed"
        assert elem.data_type == "uint16"
    
    def test_port_interface_creation(self):
        """Test creating a port interface."""
        elem = DataElement(
            name="Value",
            short_name="Value",
            data_type="uint32",
        )
        
        interface = PortInterface(
            name="TestInterface",
            short_name="TestInterface",
            interface_type="SenderReceiver",
            data_elements=[elem],
        )
        
        assert interface.interface_type == "SenderReceiver"
        assert len(interface.data_elements) == 1
    
    def test_component_creation(self):
        """Test creating a component."""
        component = Component(
            name="TestSWC",
            short_name="TestSWC",
            component_type="ApplicationSWC",
            version="1.0.0",
        )
        
        assert component.component_type == "ApplicationSWC"
    
    def test_ar_package(self):
        """Test creating an AUTOSAR package."""
        component = Component(
            name="SWC1",
            short_name="SWC1",
            component_type="ApplicationSWC",
        )
        
        package = ARPackage(
            name="Components",
            short_name="Components",
            components=[component],
        )
        
        assert package.name == "Components"
        assert len(package.components) == 1
        assert package.get_component("SWC1") is not None


class TestModelValidation:
    """Test model validation."""
    
    def test_signal_bit_range_validation(self):
        """Test signal bit range is validated."""
        with pytest.raises(ValueError):
            CANSignal(
                name="Invalid",
                short_name="Invalid",
                start_bit=0,
                length=65,  # Too long!
            )
    
    def test_message_id_validation(self):
        """Test CAN message ID validation."""
        # Valid standard ID
        msg = CANMessage(
            name="Test",
            short_name="Test",
            message_id=0x7FF,
            dlc=8,
            is_extended=False,
        )
        assert msg.message_id == 0x7FF
        
        # Invalid standard ID (too large)
        with pytest.raises(ValueError):
            CANMessage(
                name="Test",
                short_name="Test",
                message_id=0x800,  # > 0x7FF
                dlc=8,
                is_extended=False,
            )
    
    def test_parameter_type_validation(self):
        """Test parameter type validation."""
        # Valid integer parameter
        param = Parameter(
            name="Test",
            short_name="Test",
            parameter_type=ParameterType.INTEGER,
            value=42,
        )
        assert param.value == 42
        
        # Invalid: string value for integer type
        with pytest.raises(ValueError):
            Parameter(
                name="Test",
                short_name="Test",
                parameter_type=ParameterType.INTEGER,
                value="not_an_int",
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
