"""
Example: Generate ECUC Configuration from DBC and LDF files

This example demonstrates:
1. Loading CAN network from DBC file
2. Loading LIN network from LDF file
3. Generating ECUC configuration values
4. Exporting to ARXML format
"""

from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autosar.service import ECUCService
from autosar.generator import ECUCGenerator
from autosar.model import AutosarVersion


def example_generate_ecuc():
    """
    Example: Generate ECUC configuration from network files.
    """
    print("=" * 70)
    print("ECUC Configuration Generator Example")
    print("=" * 70)
    print()
    
    # Create service for AR4.2.2
    print("1. Creating ECUC Service for AUTOSAR AR4.2.2...")
    service = ECUCService(autosar_version=AutosarVersion.AR_4_2_2)
    print("   OK Service created")
    print()
    
    # Note: In real usage, you would load actual DBC/LDF files:
    # service.load_dbc('path/to/network.dbc', network_name='BodyCAN')
    # service.load_ldf('path/to/network.ldf', network_name='DoorLIN')
    
    # For this example, we'll create networks programmatically
    print("2. Creating sample CAN network...")
    from autosar.model import (
        CANDatabase, CANMessage, CANSignal, CANNode, ByteOrder
    )
    
    # Create CAN network
    can_network = CANDatabase(
        name="BodyCAN",
        short_name="BodyCAN",
        baudrate=500000,
        uuid="body-can-uuid-001"
    )
    
    # Create CAN message with signals
    door_status_msg = CANMessage(
        name="DoorStatus",
        short_name="DoorStatus",
        message_id=0x200,
        length=8,
        cycle_time=100,
        uuid="door-status-msg-uuid"
    )
    
    # Add signals
    signals = [
        CANSignal(
            name="DoorLeftFront",
            short_name="DoorLeftFront",
            start_bit=0,
            length=8,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            uuid="door-left-front-uuid"
        ),
        CANSignal(
            name="DoorRightFront",
            short_name="DoorRightFront",
            start_bit=8,
            length=8,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            uuid="door-right-front-uuid"
        ),
        CANSignal(
            name="DoorLeftRear",
            short_name="DoorLeftRear",
            start_bit=16,
            length=8,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            uuid="door-left-rear-uuid"
        ),
        CANSignal(
            name="DoorRightRear",
            short_name="DoorRightRear",
            start_bit=24,
            length=8,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            uuid="door-right-rear-uuid"
        ),
    ]
    
    door_status_msg.signals = signals
    can_network.messages = [door_status_msg]
    
    # Add node
    body_ecu = CANNode(
        name="BodyECU",
        short_name="BodyECU",
        uuid="body-ecu-uuid"
    )
    can_network.nodes = [body_ecu]
    
    # Add network to service
    service.can_networks["BodyCAN"] = can_network
    print(f"   OK Created CAN network with {len(can_network.messages)} messages")
    print(f"   OK Total signals: {sum(len(m.signals) for m in can_network.messages)}")
    print()
    
    # Create LIN network
    print("3. Creating sample LIN network...")
    from autosar.model import (
        LINNetwork, LINFrame, LINSignal, LINNode,
        LINNodeType, FrameType
    )
    
    lin_network = LINNetwork(
        name="DoorLIN",
        short_name="DoorLIN",
        baudrate=19200,
        protocol_version="2.1",
        uuid="door-lin-uuid"
    )
    
    # Create LIN frame
    door_cmd_frame = LINFrame(
        name="DoorCommand",
        short_name="DoorCommand",
        frame_id=0x10,
        length=2,
        frame_type=FrameType.UNCONDITIONAL,
        uuid="door-cmd-frame-uuid"
    )
    
    # Add signal
    lock_cmd = LINSignal(
        name="LockCommand",
        short_name="LockCommand",
        start_bit=0,
        length=8,
        uuid="lock-cmd-uuid"
    )
    
    door_cmd_frame.signals = [lock_cmd]
    lin_network.frames = [door_cmd_frame]
    
    # Add nodes
    master = LINNode(
        name="DoorMaster",
        short_name="DoorMaster",
        node_type=LINNodeType.MASTER,
        uuid="door-master-uuid"
    )
    
    slave = LINNode(
        name="DoorSlave",
        short_name="DoorSlave",
        node_type=LINNodeType.SLAVE,
        uuid="door-slave-uuid"
    )
    
    lin_network.master_node = master
    lin_network.slave_nodes = [slave]
    
    # Add network to service
    service.lin_networks["DoorLIN"] = lin_network
    print(f"   OK Created LIN network with {len(lin_network.frames)} frames")
    print(f"   OK Total signals: {sum(len(f.signals) for f in lin_network.frames)}")
    print()
    
    # Get summary
    print("4. Data Summary:")
    summary = service.get_summary()
    print(f"   - AUTOSAR Version: {summary['autosar_version']}")
    print(f"   - CAN Networks: {summary['can_networks']}")
    print(f"   - LIN Networks: {summary['lin_networks']}")
    print()
    
    for network_name, network_info in summary['networks'].items():
        print(f"   Network: {network_name}")
        print(f"     Type: {network_info['type']}")
        print(f"     Baudrate: {network_info['baudrate']}")
        if network_info['type'] == 'CAN':
            print(f"     Messages: {network_info['messages']}")
        else:
            print(f"     Frames: {network_info['frames']}")
        print(f"     Signals: {network_info['signals']}")
        print(f"     Nodes: {network_info['nodes']}")
        print()
    
    # Validate data
    print("5. Validating data...")
    try:
        service.validate_data()
        print("   OK Validation passed")
    except Exception as e:
        print(f"   ERROR Validation failed: {e}")
        return
    print()
    
    # Generate ECUC project
    print("6. Generating ECUC project...")
    project = service.generate_ecuc_project(
        project_name="BodyECU_Config",
        ecu_instance="BodyECU_Instance_1",
        modules=['CanIf', 'Can', 'LinIf', 'Lin']
    )
    print(f"   OK Project '{project.short_name}' generated")
    print(f"   OK ECU Instance: {project.ecu_instance}")
    print(f"   OK AUTOSAR Version: {project.autosar_version.value}")
    print(f"   OK Modules: {len(project.value_collection.modules)}")
    print()
    
    # List generated modules
    print("7. Generated Modules:")
    for module in project.value_collection.modules:
        print(f"   - {module.short_name}")
        print(f"     Definition: {module.module_def_ref}")
        print(f"     Containers: {len(module.containers)}")
    print()
    
    # Generate ARXML
    print("8. Generating ARXML output...")
    generator = ECUCGenerator()
    
    # Generate to file
    output_path = Path(__file__).parent / "output" / "BodyECU_Config.arxml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    generator.generate(project, str(output_path), pretty_print=True)
    print(f"   OK ARXML generated: {output_path}")
    print(f"   OK File size: {output_path.stat().st_size} bytes")
    print()
    
    # Also generate preview
    print("9. ARXML Preview (first 1000 characters):")
    print("-" * 70)
    arxml_str = generator.generate_to_string(project, pretty_print=True)
    print(arxml_str[:1000])
    if len(arxml_str) > 1000:
        print("...")
        print(f"   (Total length: {len(arxml_str)} characters)")
    print("-" * 70)
    print()
    
    print("=" * 70)
    print("OK Example completed successfully!")
    print("=" * 70)


def example_ar45():
    """
    Example: Generate ECUC configuration for AR4.5.
    """
    print()
    print("=" * 70)
    print("ECUC Configuration Generator - AR4.5 Example")
    print("=" * 70)
    print()
    
    # Create service for AR4.5
    print("Creating ECUC Service for AUTOSAR AR4.5...")
    service = ECUCService(autosar_version=AutosarVersion.AR_4_5_0)
    
    # Create simple CAN network
    from autosar.model import CANDatabase, CANMessage, CANSignal, ByteOrder
    
    network = CANDatabase(
        name="PowertrainCAN",
        short_name="PowertrainCAN",
        baudrate=500000,
        uuid="powertrain-can-uuid"
    )
    
    msg = CANMessage(
        name="EngineData",
        short_name="EngineData",
        message_id=0x100,
        length=8,
        uuid="engine-data-uuid"
    )
    
    sig = CANSignal(
        name="EngineSpeed",
        short_name="EngineSpeed",
        start_bit=0,
        length=16,
        byte_order=ByteOrder.LITTLE_ENDIAN,
        uuid="engine-speed-uuid"
    )
    
    msg.signals = [sig]
    network.messages = [msg]
    
    service.can_networks["PowertrainCAN"] = network
    print("OK Network created")
    print()
    
    # Generate project
    print("Generating ECUC project...")
    project = service.generate_ecuc_project(
        project_name="PowertrainECU_AR45",
        ecu_instance="PowertrainECU_1",
        modules=['CanIf', 'Can']
    )
    print(f"OK Project generated for AR{project.autosar_version.value}")
    print()
    
    # Generate ARXML
    generator = ECUCGenerator()
    output_path = Path(__file__).parent / "output" / "PowertrainECU_AR45.arxml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    generator.generate(project, str(output_path), pretty_print=True)
    print(f"OK ARXML generated: {output_path}")
    print()


if __name__ == "__main__":
    # Run main example
    example_generate_ecuc()
    
    # Run AR4.5 example
    example_ar45()
