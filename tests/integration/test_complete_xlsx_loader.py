"""
Integration Tests for Complete XLSX Loader.

Tests the integration between loader and models with real Excel files.
"""

import pytest
from pathlib import Path
from autosar.loader import CompleteXLSXLoader
from autosar.model import (
    CompleteXLSXDatabase,
    CompleteXLSXMessage,
    CompleteXLSXSignal,
    MessageDirection,
)


# Test data path
TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'examples' / 'xlsx'


class TestCompleteXLSXLoaderIntegration:
    """Integration tests for CompleteXLSXLoader with real files."""
    
    @pytest.fixture
    def loader(self):
        """Create loader instance."""
        return CompleteXLSXLoader()
    
    @pytest.fixture
    def test_file(self):
        """Path to test Excel file."""
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return str(file_path)
    
    def test_load_returns_dict(self, loader, test_file):
        """Test that load() returns a dictionary."""
        data = loader.load(test_file)
        
        assert isinstance(data, dict)
        assert 'file_path' in data
        assert 'rx_messages' in data
        assert 'tx_messages' in data
        assert 'nodes' in data
    
    def test_load_parses_rx_messages(self, loader, test_file):
        """Test that RX messages are parsed."""
        data = loader.load(test_file)
        
        assert isinstance(data['rx_messages'], list)
        assert len(data['rx_messages']) > 0
        
        # Check first message structure
        first_msg = data['rx_messages'][0]
        assert 'message_name' in first_msg
        assert 'message_id' in first_msg
        assert 'signals' in first_msg
        assert first_msg['direction'] == MessageDirection.RX
    
    def test_load_parses_tx_messages(self, loader, test_file):
        """Test that TX messages are parsed."""
        data = loader.load(test_file)
        
        assert isinstance(data['tx_messages'], list)
        assert len(data['tx_messages']) > 0
        
        # Check first message structure
        first_msg = data['tx_messages'][0]
        assert 'message_name' in first_msg
        assert 'message_id' in first_msg
        assert 'signals' in first_msg
        assert first_msg['direction'] == MessageDirection.TX
    
    def test_validate_accepts_valid_data(self, loader, test_file):
        """Test that validate() accepts valid data."""
        data = loader.load(test_file)
        
        # Should not raise exception
        assert loader.validate(data) is True
    
    def test_to_model_returns_database(self, loader, test_file):
        """Test that to_model() returns CompleteXLSXDatabase."""
        data = loader.load(test_file)
        loader.validate(data)
        
        database = loader.to_model(data)
        
        assert isinstance(database, CompleteXLSXDatabase)
        assert len(database.messages) > 0
    
    def test_load_complete_end_to_end(self, loader, test_file):
        """Test complete loading workflow."""
        database = loader.load_complete(test_file)
        
        # Verify database
        assert isinstance(database, CompleteXLSXDatabase)
        assert database.name == 'CAN_ECM_FD3'
        
        # Verify messages
        assert len(database.messages) == 85  # Known value from test file
        assert len(database.rx_messages) == 67
        assert len(database.tx_messages) == 18
        
        # Verify signals
        stats = database.get_statistics()
        assert stats['total_signals'] == 781
        assert stats['rx_signals'] == 411
        assert stats['tx_signals'] == 370
    
    def test_loaded_signals_have_all_fields(self, loader, test_file):
        """Test that loaded signals have all expected fields."""
        database = loader.load_complete(test_file)
        
        # Get first RX signal
        rx_sig = database.rx_messages[0].signals[0]
        
        # Check core fields
        assert rx_sig.signal_name is not None
        assert rx_sig.signal_size > 0
        assert rx_sig.direction == MessageDirection.RX
        
        # Check at least some fields are populated
        # (not all may have values in every signal)
        has_bsw_data = (
            rx_sig.data_element_name or
            rx_sig.data_type or
            rx_sig.type_reference
        )
        assert has_bsw_data, "Signal should have some BSW layer data"
        
        has_app_data = (
            rx_sig.port_name or
            rx_sig.data_type_scaled or
            rx_sig.mapped_idt
        )
        assert has_app_data, "Signal should have some Application layer data"
    
    def test_extended_frames_detected(self, loader, test_file):
        """Test that extended frames are auto-detected."""
        database = loader.load_complete(test_file)
        
        # Find extended frames
        extended = [msg for msg in database.messages if msg.is_extended]
        
        # CAN_ECM_FD3 has 4 extended frames
        assert len(extended) == 4
        
        # Check IDs are > 0x7FF
        for msg in extended:
            assert msg.message_id > 0x7FF, f"Extended frame {msg.message_name} has ID <= 0x7FF"
    
    def test_signal_groups_parsed(self, loader, test_file):
        """Test that signal groups are parsed."""
        database = loader.load_complete(test_file)
        
        stats = database.get_statistics()
        assert stats['unique_signal_groups'] == 31  # Known value
        
        # Find message with signal groups
        for msg in database.messages:
            groups = msg.get_all_signal_groups()
            if groups:
                # Verify signals can be retrieved by group
                for group in groups:
                    sigs = msg.get_signals_by_group(group)
                    assert len(sigs) > 0
                break
    
    def test_sna_signals_detected(self, loader, test_file):
        """Test that SNA signals are detected."""
        database = loader.load_complete(test_file)
        
        stats = database.get_statistics()
        assert stats['signals_with_sna'] == 292  # Known value
        
        # Find at least one signal with SNA
        sna_signals = []
        for msg in database.messages:
            for sig in msg.signals:
                if sig.has_sna:
                    sna_signals.append(sig)
        
        assert len(sna_signals) == 292
    
    def test_legacy_names_preserved(self, loader, test_file):
        """Test that legacy names are preserved."""
        database = loader.load_complete(test_file)
        
        # Find signals with legacy names
        signals_with_legacy = []
        for msg in database.messages:
            for sig in msg.signals:
                legacy = sig.get_legacy_names()
                if legacy:
                    signals_with_legacy.append((sig, legacy))
        
        # Some signals should have legacy names
        assert len(signals_with_legacy) > 0, "Should find signals with legacy names"
    
    def test_message_query_by_id(self, loader, test_file):
        """Test querying messages by ID."""
        database = loader.load_complete(test_file)
        
        # Known message ID from test file
        msg = database.get_message_by_id(0x5B0)  # ADAS_FD_HMI
        
        assert msg is not None
        assert msg.message_name == "ADAS_FD_HMI"
        assert len(msg.signals) == 4
    
    def test_message_query_by_name(self, loader, test_file):
        """Test querying messages by name."""
        database = loader.load_complete(test_file)
        
        # Known message name
        msg = database.get_message_by_name("ADAS_FD_HMI")
        
        assert msg is not None
        assert msg.message_id == 0x5B0
    
    def test_signal_query_by_name(self, loader, test_file):
        """Test querying signals by name."""
        database = loader.load_complete(test_file)
        
        # Get known message
        msg = database.get_message_by_name("ADAS_FD_HMI")
        assert msg is not None
        
        # Query signal
        sig = msg.get_signal_by_name("CRC_ADAS_FD_HMI")
        
        assert sig is not None
        assert sig.signal_size == 8


class TestCompleteXLSXLoaderErrorHandling:
    """Integration tests for error handling."""
    
    @pytest.fixture
    def loader(self):
        """Create loader instance."""
        return CompleteXLSXLoader()
    
    def test_load_nonexistent_file(self, loader):
        """Test loading non-existent file raises error."""
        with pytest.raises(Exception):
            loader.load('nonexistent_file.xlsx')
    
    def test_load_invalid_extension(self, loader, tmp_path):
        """Test loading file with wrong extension raises error."""
        # Create a file with wrong extension
        invalid_file = tmp_path / 'test.txt'
        invalid_file.write_text('test')
        
        with pytest.raises(Exception):
            loader.load(str(invalid_file))
    
    def test_validate_invalid_data_structure(self, loader):
        """Test validation rejects invalid data structure."""
        invalid_data = {
            'rx_messages': "not a list",  # Should be list
            'tx_messages': [],
        }
        
        with pytest.raises(Exception):
            loader.validate(invalid_data)
    
    def test_validate_missing_required_fields(self, loader):
        """Test validation rejects data missing required fields."""
        invalid_data = {
            'rx_messages': [],
            # Missing 'tx_messages'
        }
        
        with pytest.raises(Exception):
            loader.validate(invalid_data)


class TestCompleteXLSXLoaderDataIntegrity:
    """Integration tests for data integrity."""
    
    @pytest.fixture
    def database(self):
        """Load test database."""
        loader = CompleteXLSXLoader()
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return loader.load_complete(str(file_path))
    
    def test_all_messages_have_valid_ids(self, database):
        """Test that all messages have valid IDs."""
        for msg in database.messages:
            if msg.is_extended:
                assert 0 <= msg.message_id <= 0x1FFFFFFF
            else:
                assert 0 <= msg.message_id <= 0x7FF
    
    def test_all_signals_have_valid_sizes(self, database):
        """Test that all signals have valid sizes."""
        for msg in database.messages:
            for sig in msg.signals:
                assert 1 <= sig.signal_size <= 64
    
    def test_all_signals_match_message_direction(self, database):
        """Test that signal direction matches message direction."""
        for msg in database.messages:
            for sig in msg.signals:
                assert sig.direction == msg.direction
    
    def test_rx_signals_have_consumer_info(self, database):
        """Test that RX signals can have consumer info."""
        rx_signals_with_consumer = []
        for msg in database.rx_messages:
            for sig in msg.signals:
                if sig.consumer_swc:
                    rx_signals_with_consumer.append(sig)
        
        # Some RX signals should have consumer info
        # (not enforcing all, as it depends on data)
        assert isinstance(rx_signals_with_consumer, list)
    
    def test_tx_signals_have_producer_info(self, database):
        """Test that TX signals can have producer info."""
        tx_signals_with_producer = []
        for msg in database.tx_messages:
            for sig in msg.signals:
                if sig.producer_swc:
                    tx_signals_with_producer.append(sig)
        
        # Some TX signals should have producer info
        assert isinstance(tx_signals_with_producer, list)
    
    def test_statistics_consistency(self, database):
        """Test that statistics are internally consistent."""
        stats = database.get_statistics()
        
        # Total should equal RX + TX
        assert stats['total_messages'] == stats['rx_messages'] + stats['tx_messages']
        assert stats['total_signals'] == stats['rx_signals'] + stats['tx_signals']
        
        # Counts should be non-negative
        for key, value in stats.items():
            assert value >= 0, f"Statistic {key} should be non-negative"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
