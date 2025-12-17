"""
Unit tests for XLSX Loader.

Tests the XLSXLoader class for loading Excel CAN configuration files.
"""

import pytest
from pathlib import Path

from autosar.loader import XLSXLoader
from autosar.loader.base_loader import ParserError, ValidationError, ConversionError
from autosar.model import CANDatabase, CANMessage, CANSignal


class TestXLSXLoader:
    """Test suite for XLSXLoader."""
    
    @pytest.fixture
    def loader(self):
        """Create XLSXLoader instance."""
        return XLSXLoader()
    
    @pytest.fixture
    def sample_xlsx_file(self):
        """Get path to sample XLSX file."""
        # Adjust path based on test execution location
        test_dir = Path(__file__).parent
        xlsx_path = test_dir.parent / "examples" / "xlsx" / "CAN_ECM_FD3.xlsx"
        return str(xlsx_path)
    
    def test_loader_creation(self, loader):
        """Test XLSXLoader instance creation."""
        assert loader is not None
        assert isinstance(loader, XLSXLoader)
    
    def test_load_file_not_found(self, loader):
        """Test loading non-existent file raises error."""
        with pytest.raises(Exception):  # FileNotFoundError or similar
            loader.load("nonexistent_file.xlsx")
    
    def test_load_invalid_extension(self, loader):
        """Test loading file with invalid extension."""
        with pytest.raises(Exception):
            loader.load("test.txt")
    
    def test_load_sample_file(self, loader, sample_xlsx_file):
        """Test loading a real XLSX file."""
        if not Path(sample_xlsx_file).exists():
            pytest.skip(f"Sample file not found: {sample_xlsx_file}")
        
        # Load the file
        data = loader.load(sample_xlsx_file)
        
        # Verify structure
        assert 'messages' in data
        assert 'nodes' in data
        assert 'version' in data
        assert 'file_path' in data
        assert 'rx_count' in data
        assert 'tx_count' in data
        
        # Check data types
        assert isinstance(data['messages'], list)
        assert isinstance(data['nodes'], list)
        assert isinstance(data['rx_count'], int)
        assert isinstance(data['tx_count'], int)
        
        # Should have some messages
        assert len(data['messages']) > 0
        
        print(f"\nLoaded {len(data['messages'])} messages:")
        print(f"  - RX: {data['rx_count']}")
        print(f"  - TX: {data['tx_count']}")
        print(f"  - Nodes: {len(data['nodes'])}")
    
    def test_validate_sample_data(self, loader, sample_xlsx_file):
        """Test validation of loaded data."""
        if not Path(sample_xlsx_file).exists():
            pytest.skip(f"Sample file not found: {sample_xlsx_file}")
        
        data = loader.load(sample_xlsx_file)
        
        # Validate should pass
        assert loader.validate(data) is True
    
    def test_validate_missing_key(self, loader):
        """Test validation fails with missing keys."""
        invalid_data = {'messages': []}  # Missing 'nodes' and 'version'
        
        with pytest.raises(ValidationError):
            loader.validate(invalid_data)
    
    def test_validate_invalid_messages_type(self, loader):
        """Test validation fails when messages is not a list."""
        invalid_data = {
            'messages': 'not a list',
            'nodes': [],
            'version': '1.0'
        }
        
        with pytest.raises(ValidationError):
            loader.validate(invalid_data)
    
    def test_to_model(self, loader, sample_xlsx_file):
        """Test conversion to CANDatabase model."""
        if not Path(sample_xlsx_file).exists():
            pytest.skip(f"Sample file not found: {sample_xlsx_file}")
        
        # Load and validate
        data = loader.load(sample_xlsx_file)
        loader.validate(data)
        
        # Convert to model
        database = loader.to_model(data)
        
        # Verify model
        assert isinstance(database, CANDatabase)
        assert database.name is not None
        assert len(database.messages) > 0
        
        # Check first message
        first_msg = database.messages[0]
        assert isinstance(first_msg, CANMessage)
        assert first_msg.name is not None
        assert first_msg.message_id >= 0
        
        # Check signals
        assert len(first_msg.signals) > 0
        first_signal = first_msg.signals[0]
        assert isinstance(first_signal, CANSignal)
        assert first_signal.name is not None
        
        print(f"\nConverted to model:")
        print(f"  Database: {database.name}")
        print(f"  Messages: {len(database.messages)}")
        print(f"  First message: {first_msg.name} (ID: 0x{first_msg.message_id:X})")
        print(f"  Signals in first message: {len(first_msg.signals)}")
    
    def test_parse_message_id_formats(self, loader):
        """Test parsing various message ID formats."""
        # Test hex with 'h' suffix
        assert loader._parse_message_id('5B0h') == 0x5B0
        assert loader._parse_message_id('CCh') == 0xCC
        
        # Test hex with 0x prefix
        assert loader._parse_message_id('0x5B0') == 0x5B0
        assert loader._parse_message_id('0xCC') == 0xCC
        
        # Test plain hex
        assert loader._parse_message_id('5B0') == 0x5B0
        assert loader._parse_message_id('CC') == 0xCC
        
        # Test integer
        assert loader._parse_message_id(1456) == 1456
        assert loader._parse_message_id(204) == 204
        
        # Test hex string (parser tries hex first, then decimal)
        assert loader._parse_message_id('1456') == 0x1456  # Parsed as hex = 5206
        
    def test_parse_yes_no(self, loader):
        """Test parsing Yes/No values."""
        # Test various Yes formats
        assert loader._parse_yes_no('Yes') is True
        assert loader._parse_yes_no('YES') is True
        assert loader._parse_yes_no('yes') is True
        assert loader._parse_yes_no('Y') is True
        assert loader._parse_yes_no('y') is True
        assert loader._parse_yes_no('True') is True
        assert loader._parse_yes_no('1') is True
        assert loader._parse_yes_no(True) is True
        
        # Test various No formats
        assert loader._parse_yes_no('No') is False
        assert loader._parse_yes_no('NO') is False
        assert loader._parse_yes_no('no') is False
        assert loader._parse_yes_no('N') is False
        assert loader._parse_yes_no('False') is False
        assert loader._parse_yes_no('0') is False
        assert loader._parse_yes_no(False) is False
        assert loader._parse_yes_no(None) is False
    
    def test_parse_cycle_time(self, loader):
        """Test parsing cycle time values."""
        assert loader._parse_cycle_time(100) == 100
        assert loader._parse_cycle_time('100') == 100
        assert loader._parse_cycle_time(10.5) == 10
        assert loader._parse_cycle_time(None) is None
        assert loader._parse_cycle_time('invalid') is None
    
    def test_full_load_flow(self, loader, sample_xlsx_file):
        """Test complete load -> validate -> to_model flow."""
        if not Path(sample_xlsx_file).exists():
            pytest.skip(f"Sample file not found: {sample_xlsx_file}")
        
        # Step 1: Load
        data = loader.load(sample_xlsx_file)
        assert data is not None
        
        # Step 2: Validate
        is_valid = loader.validate(data)
        assert is_valid is True
        
        # Step 3: Convert to model
        database = loader.to_model(data)
        assert database is not None
        assert isinstance(database, CANDatabase)
        
        # Verify all messages have signals
        for msg in database.messages:
            assert len(msg.signals) > 0, f"Message {msg.name} has no signals"
        
        print(f"\n✅ Full load flow successful!")
        print(f"   Loaded database: {database.name}")
        print(f"   Total messages: {len(database.messages)}")
        total_signals = sum(len(msg.signals) for msg in database.messages)
        print(f"   Total signals: {total_signals}")


class TestXLSXLoaderEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def loader(self):
        """Create XLSXLoader instance."""
        return XLSXLoader()
    
    def test_empty_data_conversion(self, loader):
        """Test converting empty but valid data."""
        data = {
            'version': '1.0',
            'messages': [],
            'nodes': [],
            'file_path': 'test.xlsx',
            'rx_count': 0,
            'tx_count': 0,
        }
        
        # Should validate
        assert loader.validate(data) is True
        
        # Should convert successfully
        database = loader.to_model(data)
        assert isinstance(database, CANDatabase)
        assert len(database.messages) == 0
    
    def test_message_without_signals(self, loader):
        """Test message with no signals."""
        data = {
            'version': '1.0',
            'messages': [{
                'name': 'TestMessage',
                'message_id': 0x100,
                'is_extended': False,
                'dlc': 8,
                'cycle_time': None,
                'senders': [],
                'comment': 'Test',
                'signals': [],  # No signals
                'direction': 'rx',
            }],
            'nodes': [],
            'file_path': 'test.xlsx',
        }
        
        # Should validate
        assert loader.validate(data) is True
        
        # Should convert
        database = loader.to_model(data)
        assert len(database.messages) == 1
        assert len(database.messages[0].signals) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
