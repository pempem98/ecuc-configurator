"""
Tests for DBC loader.
"""

import pytest
from pathlib import Path
from autosar.loader import DBCLoader, ParserError, ValidationError
from autosar.model import CANDatabase, CANMessage, CANSignal


# Sample DBC content for testing
SAMPLE_DBC_CONTENT = """VERSION ""

NS_ :
    NS_DESC_
    CM_
    BA_DEF_
    BA_
    VAL_
    CAT_DEF_
    CAT_
    FILTER
    BA_DEF_DEF_
    EV_DATA_
    ENVVAR_DATA_
    SGTYPE_
    SGTYPE_VAL_
    BA_DEF_SGTYPE_
    BA_SGTYPE_
    SIG_TYPE_REF_
    VAL_TABLE_
    SIG_GROUP_
    SIG_VALTYPE_
    SIGTYPE_VALTYPE_
    BO_TX_BU_
    BA_DEF_REL_
    BA_REL_
    BA_SGTYPE_REL_
    SG_MUL_VAL_

BS_:

BU_: ECU1 ECU2

BO_ 256 Powertrain_01: 8 ECU1
 SG_ EngineSpeed : 0|16@1+ (0.25,0) [0|16383.75] "rpm" ECU2
 SG_ VehicleSpeed : 16|16@1+ (0.01,0) [0|655.35] "km/h" ECU2
 SG_ EngineTemp : 32|8@1+ (1,-40) [-40|215] "degC" ECU2

BO_ 512 Body_01: 4 ECU2
 SG_ DoorStatus : 0|8@1+ (1,0) [0|255] "" ECU1

CM_ SG_ 256 EngineSpeed "Engine RPM signal";
CM_ SG_ 256 VehicleSpeed "Vehicle speed signal";
CM_ BO_ 256 "Powertrain message";

VAL_ 512 DoorStatus 0 "Closed" 1 "Open" 2 "Error" ;
"""


class TestDBCLoader:
    """Test suite for DBC loader."""
    
    @pytest.fixture
    def temp_dbc_file(self, tmp_path):
        """Create a temporary DBC file for testing."""
        dbc_file = tmp_path / "test.dbc"
        dbc_file.write_text(SAMPLE_DBC_CONTENT)
        return str(dbc_file)
    
    @pytest.fixture
    def loader(self):
        """Create DBC loader instance."""
        return DBCLoader()
    
    def test_loader_creation(self, loader):
        """Test loader can be instantiated."""
        assert loader is not None
        assert isinstance(loader, DBCLoader)
    
    def test_load_dbc_file(self, loader, temp_dbc_file):
        """Test loading a valid DBC file."""
        data = loader.load(temp_dbc_file)
        
        assert 'messages' in data
        assert 'nodes' in data
        assert 'version' in data
        assert len(data['messages']) == 2  # Powertrain_01 and Body_01
        assert len(data['nodes']) == 2  # ECU1 and ECU2
    
    def test_load_nonexistent_file(self, loader):
        """Test loading a non-existent file raises error."""
        with pytest.raises(Exception):  # FileNotFoundError from base
            loader.load("nonexistent_file.dbc")
    
    def test_validate_valid_data(self, loader, temp_dbc_file):
        """Test validation of valid DBC data."""
        data = loader.load(temp_dbc_file)
        assert loader.validate(data) is True
    
    def test_validate_invalid_data(self, loader):
        """Test validation rejects invalid data."""
        invalid_data = {'invalid': 'data'}
        
        with pytest.raises(ValidationError):
            loader.validate(invalid_data)
    
    def test_to_model_conversion(self, loader, temp_dbc_file):
        """Test conversion to CANDatabase model."""
        data = loader.load(temp_dbc_file)
        loader.validate(data)
        
        database = loader.to_model(data)
        
        assert isinstance(database, CANDatabase)
        assert len(database.messages) == 2
        assert len(database.nodes) == 2
        
        # Check first message
        msg = database.messages[0]
        assert isinstance(msg, CANMessage)
        assert msg.message_id == 256
        assert msg.dlc == 8
        assert len(msg.signals) == 3  # EngineSpeed, VehicleSpeed, EngineTemp
        
        # Check signal
        sig = msg.signals[0]
        assert isinstance(sig, CANSignal)
        assert sig.name == "EngineSpeed"
        assert sig.start_bit == 0
        assert sig.length == 16
        assert sig.factor == 0.25
        assert sig.unit == "rpm"
    
    def test_load_and_convert_convenience(self, loader, temp_dbc_file):
        """Test load_and_convert convenience method."""
        database = loader.load_and_convert(temp_dbc_file)
        
        assert isinstance(database, CANDatabase)
        assert len(database.messages) == 2
        assert database.name == "test"  # From filename
    
    def test_message_with_signals(self, loader, temp_dbc_file):
        """Test message contains all signals correctly."""
        database = loader.load_and_convert(temp_dbc_file)
        
        powertrain_msg = database.get_message_by_id(256)
        assert powertrain_msg is not None
        assert powertrain_msg.name == "Powertrain_01"
        
        # Check all signals are present
        signal_names = [s.name for s in powertrain_msg.signals]
        assert "EngineSpeed" in signal_names
        assert "VehicleSpeed" in signal_names
        assert "EngineTemp" in signal_names
    
    def test_value_table_conversion(self, loader, temp_dbc_file):
        """Test value table (enumeration) is converted correctly."""
        database = loader.load_and_convert(temp_dbc_file)
        
        body_msg = database.get_message_by_id(512)
        assert body_msg is not None
        
        door_signal = body_msg.get_signal("DoorStatus")
        assert door_signal is not None
        
        # Check value table exists
        if door_signal.value_table:
            assert len(door_signal.value_table.entries) == 3
            assert door_signal.value_table.get_label(0) == "Closed"
            assert door_signal.value_table.get_label(1) == "Open"
            assert door_signal.value_table.get_label(2) == "Error"
    
    def test_nodes_extraction(self, loader, temp_dbc_file):
        """Test nodes are extracted correctly."""
        database = loader.load_and_convert(temp_dbc_file)
        
        assert database.get_node("ECU1") is not None
        assert database.get_node("ECU2") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
