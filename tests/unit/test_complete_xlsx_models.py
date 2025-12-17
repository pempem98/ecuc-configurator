"""
Unit Tests for Complete XLSX Models.

Tests individual model classes in isolation.
"""

import pytest
from autosar.model import (
    CompleteXLSXSignal,
    CompleteXLSXMessage,
    CompleteXLSXDatabase,
    MessageDirection,
    InvalidationPolicy,
    SignalStatus,
)


class TestCompleteXLSXSignal:
    """Unit tests for CompleteXLSXSignal model."""
    
    def test_signal_creation_minimal(self):
        """Test signal creation with minimal required fields."""
        signal = CompleteXLSXSignal(
            signal_name="TestSignal",
            signal_size=8,
            direction=MessageDirection.RX,
        )
        
        assert signal.signal_name == "TestSignal"
        assert signal.signal_size == 8
        assert signal.direction == MessageDirection.RX
        assert signal.has_sna is False  # Default
    
    def test_signal_creation_complete_rx(self):
        """Test RX signal creation with all fields."""
        signal = CompleteXLSXSignal(
            signal_name="CRC_ADAS_FD_HMI",
            signal_size=8,
            direction=MessageDirection.RX,
            
            # Core fields
            units="bits",
            signal_group="ADAS_Group",
            has_sna=False,
            periodicity=100,
            dbc_comment="CRC signal",
            notes="Test note",
            
            # Legacy names (RX)
            legacy_rx_srd_name="OLD_CRC_RX",
            legacy_impl_name="Impl_CRC",
            
            # Position & timing
            start_bit=191,
            timeout=1000,
            main_function="ComMainFunctionRx_20ms",
            
            # SWC info
            consumer_swc="VehicleManager",
            status=SignalStatus.NEW,
            
            # BSW layer
            data_element_name="COMRX_CRC_ADAS_FD_HMI_FD3",
            data_type="IDTSCRC_ADAS_FD_HMI_FD3",
            type_reference="uint8",
            initial_value="0",
            invalid_value="255",
            invalidation_policy=InvalidationPolicy.DONT_INVALIDATE,
            conversion_function="E=H",
            
            # App layer
            port_name="VeCANR_y_CRC_ADAS_FD_HMI_FD3",
            data_type_scaled="ADTSCRC_ADAS_FD_HMI_FD3",
            mapped_idt="uint8",
            signal_min_value="0",
            signal_max_value="255",
            compu_method_name="IDENTICAL",
            units_scaled="NoUnit",
        )
        
        # Verify all fields
        assert signal.signal_name == "CRC_ADAS_FD_HMI"
        assert signal.signal_size == 8
        assert signal.legacy_rx_srd_name == "OLD_CRC_RX"
        assert signal.data_element_name == "COMRX_CRC_ADAS_FD_HMI_FD3"
        assert signal.port_name == "VeCANR_y_CRC_ADAS_FD_HMI_FD3"
    
    def test_signal_creation_complete_tx(self):
        """Test TX signal creation with TX-specific fields."""
        signal = CompleteXLSXSignal(
            signal_name="Axle_Torque_DrvReqMod",
            signal_size=16,
            direction=MessageDirection.TX,
            signal_group="AXLE_TORQUE_FD_1_Pkt",
            
            # Legacy names (TX)
            legacy_srd_dd_name="OLD_SRD_DD",
            legacy_tx_accessor_name="OLD_TX_ACCESSOR",
            
            # TX-specific SWC info
            producer_swc="PowertrainController",
            pmbd_phase="Phase2",
            pmbd_coe_producer="PT_COE",
        )
        
        assert signal.is_tx is True
        assert signal.is_rx is False
        assert signal.producer_swc == "PowertrainController"
        assert signal.legacy_srd_dd_name == "OLD_SRD_DD"
    
    def test_signal_is_rx_property(self):
        """Test is_rx property."""
        rx_signal = CompleteXLSXSignal(
            signal_name="Test",
            signal_size=8,
            direction=MessageDirection.RX,
        )
        assert rx_signal.is_rx is True
        assert rx_signal.is_tx is False
    
    def test_signal_is_tx_property(self):
        """Test is_tx property."""
        tx_signal = CompleteXLSXSignal(
            signal_name="Test",
            signal_size=8,
            direction=MessageDirection.TX,
        )
        assert tx_signal.is_tx is True
        assert tx_signal.is_rx is False
    
    def test_signal_get_legacy_names_rx(self):
        """Test get_legacy_names for RX signal."""
        signal = CompleteXLSXSignal(
            signal_name="Test",
            signal_size=8,
            direction=MessageDirection.RX,
            legacy_rx_srd_name="OLD_RX_SRD",
            legacy_impl_name="OLD_IMPL",
        )
        
        legacy = signal.get_legacy_names()
        assert len(legacy) == 2
        assert "OLD_RX_SRD" in legacy
        assert "OLD_IMPL" in legacy
    
    def test_signal_get_legacy_names_tx(self):
        """Test get_legacy_names for TX signal."""
        signal = CompleteXLSXSignal(
            signal_name="Test",
            signal_size=8,
            direction=MessageDirection.TX,
            legacy_srd_dd_name="OLD_SRD_DD",
            legacy_tx_accessor_name="OLD_TX_ACC",
        )
        
        legacy = signal.get_legacy_names()
        assert len(legacy) == 2
        assert "OLD_SRD_DD" in legacy
        assert "OLD_TX_ACC" in legacy
    
    def test_signal_to_dict(self):
        """Test to_dict method."""
        signal = CompleteXLSXSignal(
            signal_name="Test",
            signal_size=8,
            direction=MessageDirection.RX,
        )
        
        data = signal.to_dict()
        assert isinstance(data, dict)
        assert data['signal_name'] == "Test"
        assert data['signal_size'] == 8
    
    def test_signal_size_validation(self):
        """Test signal size validation."""
        # Valid sizes
        for size in [1, 8, 16, 32, 64]:
            signal = CompleteXLSXSignal(
                signal_name="Test",
                signal_size=size,
                direction=MessageDirection.RX,
            )
            assert signal.signal_size == size
        
        # Invalid sizes should raise error
        with pytest.raises(ValueError):
            CompleteXLSXSignal(
                signal_name="Test",
                signal_size=0,  # Too small
                direction=MessageDirection.RX,
            )
        
        with pytest.raises(ValueError):
            CompleteXLSXSignal(
                signal_name="Test",
                signal_size=65,  # Too large
                direction=MessageDirection.RX,
            )


class TestCompleteXLSXMessage:
    """Unit tests for CompleteXLSXMessage model."""
    
    def test_message_creation_minimal(self):
        """Test message creation with minimal fields."""
        message = CompleteXLSXMessage(
            message_name="TestMessage",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
        )
        
        assert message.message_name == "TestMessage"
        assert message.message_id == 0x100
        assert message.is_extended is False
        assert message.direction == MessageDirection.RX
        assert len(message.signals) == 0
    
    def test_message_with_signals(self):
        """Test message with signals."""
        sig1 = CompleteXLSXSignal(
            signal_name="Signal1",
            signal_size=8,
            direction=MessageDirection.RX,
        )
        sig2 = CompleteXLSXSignal(
            signal_name="Signal2",
            signal_size=16,
            direction=MessageDirection.RX,
        )
        
        message = CompleteXLSXMessage(
            message_name="TestMessage",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
            signals=[sig1, sig2],
        )
        
        assert len(message.signals) == 2
        assert message.signals[0].signal_name == "Signal1"
        assert message.signals[1].signal_name == "Signal2"
    
    def test_message_standard_frame_validation(self):
        """Test standard frame ID validation."""
        # Valid standard frame ID
        message = CompleteXLSXMessage(
            message_name="Test",
            is_extended=False,
            message_id=0x7FF,
            direction=MessageDirection.RX,
        )
        assert message.message_id == 0x7FF
        
        # Invalid standard frame ID (too large)
        with pytest.raises(ValueError, match="Standard frame"):
            CompleteXLSXMessage(
                message_name="Test",
                is_extended=False,
                message_id=0x800,  # Too large for standard
                direction=MessageDirection.RX,
            )
    
    def test_message_extended_frame_validation(self):
        """Test extended frame ID validation."""
        # Valid extended frame ID
        message = CompleteXLSXMessage(
            message_name="Test",
            is_extended=True,
            message_id=0x1FFFFFFF,
            direction=MessageDirection.RX,
        )
        assert message.message_id == 0x1FFFFFFF
        
        # Invalid extended frame ID (too large)
        with pytest.raises(ValueError, match="Extended frame"):
            CompleteXLSXMessage(
                message_name="Test",
                is_extended=True,
                message_id=0x20000000,  # Too large even for extended
                direction=MessageDirection.RX,
            )
    
    def test_message_is_rx_property(self):
        """Test is_rx property."""
        message = CompleteXLSXMessage(
            message_name="Test",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
        )
        assert message.is_rx is True
        assert message.is_tx is False
    
    def test_message_is_tx_property(self):
        """Test is_tx property."""
        message = CompleteXLSXMessage(
            message_name="Test",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.TX,
        )
        assert message.is_tx is True
        assert message.is_rx is False
    
    def test_message_get_signal_by_name(self):
        """Test get_signal_by_name method."""
        sig1 = CompleteXLSXSignal(
            signal_name="Signal1",
            signal_size=8,
            direction=MessageDirection.RX,
        )
        sig2 = CompleteXLSXSignal(
            signal_name="Signal2",
            signal_size=16,
            direction=MessageDirection.RX,
        )
        
        message = CompleteXLSXMessage(
            message_name="Test",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
            signals=[sig1, sig2],
        )
        
        found = message.get_signal_by_name("Signal1")
        assert found is not None
        assert found.signal_name == "Signal1"
        
        not_found = message.get_signal_by_name("NonExistent")
        assert not_found is None
    
    def test_message_get_signals_by_group(self):
        """Test get_signals_by_group method."""
        sig1 = CompleteXLSXSignal(
            signal_name="Signal1",
            signal_size=8,
            direction=MessageDirection.RX,
            signal_group="GroupA",
        )
        sig2 = CompleteXLSXSignal(
            signal_name="Signal2",
            signal_size=16,
            direction=MessageDirection.RX,
            signal_group="GroupA",
        )
        sig3 = CompleteXLSXSignal(
            signal_name="Signal3",
            signal_size=32,
            direction=MessageDirection.RX,
            signal_group="GroupB",
        )
        
        message = CompleteXLSXMessage(
            message_name="Test",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
            signals=[sig1, sig2, sig3],
        )
        
        group_a = message.get_signals_by_group("GroupA")
        assert len(group_a) == 2
        
        group_b = message.get_signals_by_group("GroupB")
        assert len(group_b) == 1
    
    def test_message_get_all_signal_groups(self):
        """Test get_all_signal_groups method."""
        sig1 = CompleteXLSXSignal(
            signal_name="Signal1",
            signal_size=8,
            direction=MessageDirection.RX,
            signal_group="GroupA",
        )
        sig2 = CompleteXLSXSignal(
            signal_name="Signal2",
            signal_size=16,
            direction=MessageDirection.RX,
            signal_group="GroupB",
        )
        sig3 = CompleteXLSXSignal(
            signal_name="Signal3",
            signal_size=32,
            direction=MessageDirection.RX,
            signal_group="GroupA",
        )
        
        message = CompleteXLSXMessage(
            message_name="Test",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
            signals=[sig1, sig2, sig3],
        )
        
        groups = message.get_all_signal_groups()
        assert len(groups) == 2
        assert "GroupA" in groups
        assert "GroupB" in groups


class TestCompleteXLSXDatabase:
    """Unit tests for CompleteXLSXDatabase model."""
    
    def test_database_creation_empty(self):
        """Test database creation with no messages."""
        database = CompleteXLSXDatabase(
            name="TestDB",
        )
        
        assert database.name == "TestDB"
        assert len(database.messages) == 0
        assert len(database.nodes) == 0
    
    def test_database_with_messages(self):
        """Test database with messages."""
        msg1 = CompleteXLSXMessage(
            message_name="Msg1",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
        )
        msg2 = CompleteXLSXMessage(
            message_name="Msg2",
            message_id=0x200,
            is_extended=False,
            direction=MessageDirection.TX,
        )
        
        database = CompleteXLSXDatabase(
            name="TestDB",
            messages=[msg1, msg2],
            nodes=["ECU1", "ECU2"],
        )
        
        assert len(database.messages) == 2
        assert len(database.nodes) == 2
    
    def test_database_rx_messages_property(self):
        """Test rx_messages property."""
        msg1 = CompleteXLSXMessage(
            message_name="RxMsg",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
        )
        msg2 = CompleteXLSXMessage(
            message_name="TxMsg",
            message_id=0x200,
            is_extended=False,
            direction=MessageDirection.TX,
        )
        
        database = CompleteXLSXDatabase(
            name="TestDB",
            messages=[msg1, msg2],
        )
        
        rx_msgs = database.rx_messages
        assert len(rx_msgs) == 1
        assert rx_msgs[0].message_name == "RxMsg"
    
    def test_database_tx_messages_property(self):
        """Test tx_messages property."""
        msg1 = CompleteXLSXMessage(
            message_name="RxMsg",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
        )
        msg2 = CompleteXLSXMessage(
            message_name="TxMsg",
            message_id=0x200,
            is_extended=False,
            direction=MessageDirection.TX,
        )
        
        database = CompleteXLSXDatabase(
            name="TestDB",
            messages=[msg1, msg2],
        )
        
        tx_msgs = database.tx_messages
        assert len(tx_msgs) == 1
        assert tx_msgs[0].message_name == "TxMsg"
    
    def test_database_get_message_by_id(self):
        """Test get_message_by_id method."""
        msg1 = CompleteXLSXMessage(
            message_name="Msg1",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
        )
        msg2 = CompleteXLSXMessage(
            message_name="Msg2",
            message_id=0x200,
            is_extended=False,
            direction=MessageDirection.TX,
        )
        
        database = CompleteXLSXDatabase(
            name="TestDB",
            messages=[msg1, msg2],
        )
        
        found = database.get_message_by_id(0x100)
        assert found is not None
        assert found.message_name == "Msg1"
        
        not_found = database.get_message_by_id(0x999)
        assert not_found is None
    
    def test_database_get_message_by_name(self):
        """Test get_message_by_name method."""
        msg1 = CompleteXLSXMessage(
            message_name="Msg1",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
        )
        
        database = CompleteXLSXDatabase(
            name="TestDB",
            messages=[msg1],
        )
        
        found = database.get_message_by_name("Msg1")
        assert found is not None
        assert found.message_id == 0x100
        
        not_found = database.get_message_by_name("NonExistent")
        assert not_found is None
    
    def test_database_get_statistics(self):
        """Test get_statistics method."""
        # Create signals
        rx_sig1 = CompleteXLSXSignal(
            signal_name="RxSig1",
            signal_size=8,
            direction=MessageDirection.RX,
            has_sna=True,
            signal_group="GroupA",
        )
        rx_sig2 = CompleteXLSXSignal(
            signal_name="RxSig2",
            signal_size=16,
            direction=MessageDirection.RX,
            has_sna=False,
            signal_group="GroupB",
        )
        tx_sig1 = CompleteXLSXSignal(
            signal_name="TxSig1",
            signal_size=32,
            direction=MessageDirection.TX,
            has_sna=True,
            signal_group="GroupA",
        )
        
        # Create messages
        rx_msg = CompleteXLSXMessage(
            message_name="RxMsg",
            message_id=0x100,
            is_extended=False,
            direction=MessageDirection.RX,
            signals=[rx_sig1, rx_sig2],
        )
        tx_msg = CompleteXLSXMessage(
            message_name="TxMsg",
            message_id=0x200,
            is_extended=False,
            direction=MessageDirection.TX,
            signals=[tx_sig1],
        )
        
        database = CompleteXLSXDatabase(
            name="TestDB",
            messages=[rx_msg, tx_msg],
        )
        
        stats = database.get_statistics()
        
        assert stats['total_messages'] == 2
        assert stats['rx_messages'] == 1
        assert stats['tx_messages'] == 1
        assert stats['total_signals'] == 3
        assert stats['rx_signals'] == 2
        assert stats['tx_signals'] == 1
        assert stats['signals_with_sna'] == 2
        assert stats['unique_signal_groups'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
