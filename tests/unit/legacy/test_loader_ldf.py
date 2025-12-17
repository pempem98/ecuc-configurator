"""
Tests for LDF loader.
"""

import pytest
from pathlib import Path
from autosar.loader import LDFLoader, ParserError, ValidationError
from autosar.model import LINNetwork, LINFrame, LINSignal, LINNode, LINNodeType


# Sample LDF content for testing
SAMPLE_LDF_CONTENT = """
LIN_description_file;
LIN_protocol_version = "2.1";
LIN_language_version = "2.1";
LIN_speed = 19.2 kbps;

Nodes {
  Master: ECU_Master, 5 ms, 0.1 ms ;
  Slaves: Door_Slave, Window_Slave ;
}

Signals {
  DoorStatus: 8, 0, ECU_Master, Door_Slave ;
  WindowPosition: 16, 0, Window_Slave, ECU_Master ;
  LockCommand: 1, 0, ECU_Master, Door_Slave, Window_Slave ;
}

Frames {
  DoorFrame: 0x10, Door_Slave, 2 {
    DoorStatus, 0 ;
  }
  WindowFrame: 0x11, Window_Slave, 4 {
    WindowPosition, 0 ;
    LockCommand, 16 ;
  }
  MasterFrame: 0x3C, ECU_Master, 1 {
    LockCommand, 0 ;
  }
}

Schedule_tables {
  NormalSchedule {
    DoorFrame delay 10 ms ;
    WindowFrame delay 20 ms ;
    MasterFrame delay 10 ms ;
  }
  FastSchedule {
    DoorFrame delay 5 ms ;
    WindowFrame delay 5 ms ;
  }
}
"""


class TestLDFLoader:
    """Test suite for LDF loader."""
    
    @pytest.fixture
    def temp_ldf_file(self, tmp_path):
        """Create a temporary LDF file for testing."""
        ldf_file = tmp_path / "test.ldf"
        ldf_file.write_text(SAMPLE_LDF_CONTENT)
        return str(ldf_file)
    
    @pytest.fixture
    def loader(self):
        """Create LDF loader instance."""
        return LDFLoader()
    
    def test_loader_creation(self, loader):
        """Test loader can be instantiated."""
        assert loader is not None
        assert isinstance(loader, LDFLoader)
    
    def test_load_ldf_file(self, loader, temp_ldf_file):
        """Test loading a valid LDF file."""
        data = loader.load(temp_ldf_file)
        
        assert 'header' in data
        assert 'nodes' in data
        assert 'signals' in data
        assert 'frames' in data
        assert 'schedule_tables' in data
        
        # Check header
        assert data['header']['protocol_version'] == '2.1'
        assert data['header']['speed'] == 19.2
        
        # Check nodes
        assert len(data['nodes']) == 3  # 1 master + 2 slaves
        
        # Check signals
        assert len(data['signals']) == 3
        
        # Check frames
        assert len(data['frames']) == 3
        
        # Check schedule tables
        assert len(data['schedule_tables']) == 2
    
    def test_load_nonexistent_file(self, loader):
        """Test loading a non-existent file raises error."""
        with pytest.raises(Exception):
            loader.load("nonexistent_file.ldf")
    
    def test_validate_valid_data(self, loader, temp_ldf_file):
        """Test validation of valid LDF data."""
        data = loader.load(temp_ldf_file)
        assert loader.validate(data) is True
    
    def test_validate_invalid_data(self, loader):
        """Test validation rejects invalid data."""
        invalid_data = {'invalid': 'data'}
        
        with pytest.raises(ValidationError):
            loader.validate(invalid_data)
    
    def test_validate_no_master_node(self, loader, temp_ldf_file):
        """Test validation rejects data without master node."""
        data = loader.load(temp_ldf_file)
        # Remove master node
        data['nodes'] = [n for n in data['nodes'] if n['type'] != 'master']
        
        with pytest.raises(ValidationError):
            loader.validate(data)
    
    def test_to_model_conversion(self, loader, temp_ldf_file):
        """Test conversion to LINNetwork model."""
        data = loader.load(temp_ldf_file)
        loader.validate(data)
        
        network = loader.to_model(data)
        
        assert isinstance(network, LINNetwork)
        assert network.protocol_version == '2.1'
        assert network.speed == 19.2
        
        # Check master node
        assert network.master_node is not None
        assert network.master_node.name == 'ECU_Master'
        assert network.master_node.node_type == LINNodeType.MASTER
        
        # Check slave nodes
        assert len(network.slave_nodes) == 2
        slave_names = [n.name for n in network.slave_nodes]
        assert 'Door_Slave' in slave_names
        assert 'Window_Slave' in slave_names
        
        # Check frames
        assert len(network.frames) == 3
        
        # Check schedule tables
        assert len(network.schedule_tables) == 2
    
    def test_load_and_convert_convenience(self, loader, temp_ldf_file):
        """Test load_and_convert convenience method."""
        network = loader.load_and_convert(temp_ldf_file)
        
        assert isinstance(network, LINNetwork)
        assert network.name == "test"  # From filename
        assert network.master_node is not None
        assert len(network.slave_nodes) == 2
    
    def test_frames_with_signals(self, loader, temp_ldf_file):
        """Test frames contain signals correctly."""
        network = loader.load_and_convert(temp_ldf_file)
        
        door_frame = network.get_frame_by_id(0x10)
        assert door_frame is not None
        assert door_frame.name == 'DoorFrame'
        assert len(door_frame.signals) == 1
        assert door_frame.signals[0].name == 'DoorStatus'
        
        window_frame = network.get_frame_by_id(0x11)
        assert window_frame is not None
        assert len(window_frame.signals) == 2
    
    def test_schedule_table_structure(self, loader, temp_ldf_file):
        """Test schedule table is parsed correctly."""
        network = loader.load_and_convert(temp_ldf_file)
        
        normal_schedule = network.get_schedule_table('NormalSchedule')
        assert normal_schedule is not None
        assert len(normal_schedule.entries) == 3
        
        # Check entries
        assert normal_schedule.entries[0].frame_name == 'DoorFrame'
        assert normal_schedule.entries[0].delay == 10
        assert normal_schedule.entries[1].frame_name == 'WindowFrame'
        assert normal_schedule.entries[1].delay == 20
        
        # Check total duration
        total_duration = normal_schedule.get_total_duration()
        assert total_duration == 40  # 10 + 20 + 10
    
    def test_node_types(self, loader, temp_ldf_file):
        """Test node types are correctly identified."""
        network = loader.load_and_convert(temp_ldf_file)
        
        all_nodes = network.get_all_nodes()
        assert len(all_nodes) == 3
        
        # Check master
        master = network.get_node('ECU_Master')
        assert master is not None
        assert master.node_type == LINNodeType.MASTER
        
        # Check slaves
        door_slave = network.get_node('Door_Slave')
        assert door_slave is not None
        assert door_slave.node_type == LINNodeType.SLAVE
        
        window_slave = network.get_node('Window_Slave')
        assert window_slave is not None
        assert window_slave.node_type == LINNodeType.SLAVE
    
    def test_frame_id_parsing(self, loader, temp_ldf_file):
        """Test frame IDs are parsed correctly (hex and decimal)."""
        network = loader.load_and_convert(temp_ldf_file)
        
        # Frame IDs in LDF are hex (0x10, 0x11, 0x3C)
        assert network.get_frame_by_id(0x10) is not None
        assert network.get_frame_by_id(0x11) is not None
        assert network.get_frame_by_id(0x3C) is not None
        assert network.get_frame_by_id(16) is not None  # 0x10 in decimal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
