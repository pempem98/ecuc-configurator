"""
Unit tests for XLSX Models.

Tests XLSXDatabase, XLSXMessage, and XLSXSignal models.
"""

import pytest
from pathlib import Path

from autosar.model import (
    XLSXDatabase, XLSXMessage, XLSXSignal,
    MessageDirection,
    create_xlsx_signal, create_xlsx_message, create_xlsx_database
)
from autosar.model.types import ByteOrder, ValueType, SignalType


class TestXLSXSignal:
    """Test suite for XLSXSignal model."""
    
    def test_signal_creation(self):
        """Test creating XLSXSignal with basic fields."""
        signal = XLSXSignal(
            name="TestSignal",
            short_name="TestSignal",
            length=16,
            unit="kph",
        )
        
        assert signal.name == "TestSignal"
        assert signal.length == 16
        assert signal.unit == "kph"
        assert signal.start_bit == 0  # Default
        assert signal.has_sna is False  # Default
    
    def test_signal_with_excel_fields(self):
        """Test XLSXSignal with Excel-specific fields."""
        signal = XLSXSignal(
            name="Speed_Signal",
            short_name="Speed_Signal",
            length=16,
            unit="kph",
            signal_group="SpeedGroup",
            has_sna=True,
            periodicity=100,
            legacy_srd_name="OLD_SPEED",
            legacy_impl_name="legacy_speed_impl",
        )
        
        assert signal.signal_group == "SpeedGroup"
        assert signal.has_sna is True
        assert signal.periodicity == 100
        assert signal.legacy_srd_name == "OLD_SPEED"
        assert signal.legacy_impl_name == "legacy_speed_impl"
    
    def test_signal_group_normalization(self):
        """Test signal group name normalization."""
        # Empty string should become None
        signal1 = XLSXSignal(name="S1", short_name="S1", length=8, signal_group="")
        assert signal1.signal_group is None
        
        # Dash should become None
        signal2 = XLSXSignal(name="S2", short_name="S2", length=8, signal_group="-")
        assert signal2.signal_group is None
        
        # Valid group should be preserved
        signal3 = XLSXSignal(name="S3", short_name="S3", length=8, signal_group="Group1")
        assert signal3.signal_group == "Group1"
    
    def test_to_can_signal(self):
        """Test conversion to CANSignal."""
        xlsx_signal = XLSXSignal(
            name="TestSig",
            short_name="TestSig",
            length=16,
            start_bit=8,
            unit="rpm",
            factor=0.25,
            offset=0.0,
        )
        
        can_signal = xlsx_signal.to_can_signal()
        
        assert can_signal.name == "TestSig"
        assert can_signal.length == 16
        assert can_signal.start_bit == 8
        assert can_signal.unit == "rpm"
        assert can_signal.factor == 0.25


class TestXLSXMessage:
    """Test suite for XLSXMessage model."""
    
    def test_message_creation_rx(self):
        """Test creating RX message."""
        message = XLSXMessage(
            name="TestMsg",
            short_name="TestMsg",
            message_id=0x100,
            direction=MessageDirection.RX,
        )
        
        assert message.name == "TestMsg"
        assert message.message_id == 0x100
        assert message.direction == MessageDirection.RX
        assert message.is_rx is True
        assert message.is_tx is False
        assert message.is_extended is False  # Standard frame
    
    def test_message_creation_tx(self):
        """Test creating TX message."""
        message = XLSXMessage(
            name="TestMsg",
            short_name="TestMsg",
            message_id=0x200,
            direction=MessageDirection.TX,
            senders=["ECU"],
        )
        
        assert message.direction == MessageDirection.TX
        assert message.is_rx is False
        assert message.is_tx is True
        assert message.senders == ["ECU"]
    
    def test_extended_frame_detection(self):
        """Test extended frame ID validation."""
        # Standard frame
        msg1 = XLSXMessage(
            name="Std",
            short_name="Std",
            message_id=0x7FF,
            direction=MessageDirection.RX,
        )
        assert msg1.is_extended is False
        
        # Extended frame
        msg2 = XLSXMessage(
            name="Ext",
            short_name="Ext",
            message_id=0x1E394F10,
            is_extended=True,
            direction=MessageDirection.RX,
        )
        assert msg2.is_extended is True
    
    def test_message_with_signals(self):
        """Test message with signals."""
        signals = [
            XLSXSignal(name="Sig1", short_name="Sig1", length=8, signal_group="G1"),
            XLSXSignal(name="Sig2", short_name="Sig2", length=16, signal_group="G1"),
            XLSXSignal(name="Sig3", short_name="Sig3", length=8, signal_group="G2"),
        ]
        
        message = XLSXMessage(
            name="TestMsg",
            short_name="TestMsg",
            message_id=0x100,
            direction=MessageDirection.RX,
            signals=signals,
        )
        
        assert len(message.signals) == 3
        assert len(message.get_signal_groups()) == 2
        assert "G1" in message.get_signal_groups()
        assert "G2" in message.get_signal_groups()
    
    def test_get_signal_by_name(self):
        """Test finding signal by name."""
        signals = [
            XLSXSignal(name="Sig1", short_name="Sig1", length=8),
            XLSXSignal(name="Sig2", short_name="Sig2", length=16),
        ]
        
        message = XLSXMessage(
            name="TestMsg",
            short_name="TestMsg",
            message_id=0x100,
            direction=MessageDirection.RX,
            signals=signals,
        )
        
        found = message.get_signal_by_name("Sig1")
        assert found is not None
        assert found.name == "Sig1"
        
        not_found = message.get_signal_by_name("NonExistent")
        assert not_found is None
    
    def test_get_signals_by_group(self):
        """Test getting signals by group."""
        signals = [
            XLSXSignal(name="Sig1", short_name="Sig1", length=8, signal_group="GroupA"),
            XLSXSignal(name="Sig2", short_name="Sig2", length=16, signal_group="GroupA"),
            XLSXSignal(name="Sig3", short_name="Sig3", length=8, signal_group="GroupB"),
        ]
        
        message = XLSXMessage(
            name="TestMsg",
            short_name="TestMsg",
            message_id=0x100,
            direction=MessageDirection.RX,
            signals=signals,
        )
        
        group_a_signals = message.get_signals_by_group("GroupA")
        assert len(group_a_signals) == 2
        assert all(sig.signal_group == "GroupA" for sig in group_a_signals)


class TestXLSXDatabase:
    """Test suite for XLSXDatabase model."""
    
    def test_database_creation(self):
        """Test creating empty database."""
        db = XLSXDatabase(
            name="TestDB",
            short_name="TestDB",
            version="1.0",
        )
        
        assert db.name == "TestDB"
        assert db.version == "1.0"
        assert len(db.messages) == 0
    
    def test_database_with_messages(self):
        """Test database with RX and TX messages."""
        messages = [
            XLSXMessage(
                name="RxMsg1",
                short_name="RxMsg1",
                message_id=0x100,
                direction=MessageDirection.RX,
            ),
            XLSXMessage(
                name="RxMsg2",
                short_name="RxMsg2",
                message_id=0x200,
                direction=MessageDirection.RX,
            ),
            XLSXMessage(
                name="TxMsg1",
                short_name="TxMsg1",
                message_id=0x300,
                direction=MessageDirection.TX,
                senders=["ECU"],
            ),
        ]
        
        db = XLSXDatabase(
            name="TestDB",
            short_name="TestDB",
            messages=messages,
        )
        
        assert len(db.messages) == 3
        assert len(db.rx_messages) == 2
        assert len(db.tx_messages) == 1
    
    def test_database_properties(self):
        """Test database property accessors."""
        messages = [
            XLSXMessage(
                name="StdMsg",
                short_name="StdMsg",
                message_id=0x100,
                direction=MessageDirection.RX,
            ),
            XLSXMessage(
                name="ExtMsg",
                short_name="ExtMsg",
                message_id=0x1E394F10,
                is_extended=True,
                direction=MessageDirection.TX,
            ),
        ]
        
        db = XLSXDatabase(
            name="TestDB",
            short_name="TestDB",
            messages=messages,
        )
        
        assert len(db.standard_messages) == 1
        assert len(db.extended_messages) == 1
    
    def test_get_message_by_id(self):
        """Test finding message by ID."""
        messages = [
            XLSXMessage(
                name="Msg1",
                short_name="Msg1",
                message_id=0x100,
                direction=MessageDirection.RX,
            ),
            XLSXMessage(
                name="Msg2",
                short_name="Msg2",
                message_id=0x200,
                direction=MessageDirection.TX,
            ),
        ]
        
        db = XLSXDatabase(
            name="TestDB",
            short_name="TestDB",
            messages=messages,
        )
        
        found = db.get_message_by_id(0x100)
        assert found is not None
        assert found.name == "Msg1"
        
        not_found = db.get_message_by_id(0x999)
        assert not_found is None
    
    def test_get_message_by_name(self):
        """Test finding message by name."""
        messages = [
            XLSXMessage(
                name="TestMessage",
                short_name="TestMessage",
                message_id=0x100,
                direction=MessageDirection.RX,
            ),
        ]
        
        db = XLSXDatabase(
            name="TestDB",
            short_name="TestDB",
            messages=messages,
        )
        
        found = db.get_message_by_name("TestMessage")
        assert found is not None
        assert found.message_id == 0x100
    
    def test_get_statistics(self):
        """Test database statistics."""
        signals_with_sna = [
            XLSXSignal(name="S1", short_name="S1", length=8, has_sna=True),
            XLSXSignal(name="S2", short_name="S2", length=8, has_sna=False),
        ]
        
        messages = [
            XLSXMessage(
                name="RxMsg",
                short_name="RxMsg",
                message_id=0x100,
                direction=MessageDirection.RX,
                signals=signals_with_sna,
            ),
            XLSXMessage(
                name="TxMsg",
                short_name="TxMsg",
                message_id=0x800,
                is_extended=True,
                direction=MessageDirection.TX,
            ),
        ]
        
        db = XLSXDatabase(
            name="TestDB",
            short_name="TestDB",
            messages=messages,
            nodes=["ECU", "BCM"],
        )
        
        stats = db.get_statistics()
        
        assert stats['total_messages'] == 2
        assert stats['rx_messages'] == 1
        assert stats['tx_messages'] == 1
        assert stats['standard_frames'] == 1
        assert stats['extended_frames'] == 1
        assert stats['total_signals'] == 2
        assert stats['signals_with_sna'] == 1
        assert stats['nodes'] == 2


class TestXLSXHelperFunctions:
    """Test helper functions for creating XLSX models."""
    
    def test_create_xlsx_signal(self):
        """Test create_xlsx_signal helper."""
        data = {
            'name': 'TestSig',
            'length': 16,
            'unit': 'kph',
            'signal_group': 'Group1',
            'has_sna': True,
        }
        
        signal = create_xlsx_signal(data)
        
        assert signal.name == 'TestSig'
        assert signal.length == 16
        assert signal.unit == 'kph'
        assert signal.signal_group == 'Group1'
        assert signal.has_sna is True
    
    def test_create_xlsx_message(self):
        """Test create_xlsx_message helper."""
        data = {
            'name': 'TestMsg',
            'message_id': 0x100,
            'direction': 'rx',
            'dlc': 8,
            'signals': [
                {
                    'name': 'Sig1',
                    'length': 8,
                }
            ],
        }
        
        message = create_xlsx_message(data)
        
        assert message.name == 'TestMsg'
        assert message.message_id == 0x100
        assert message.direction == MessageDirection.RX
        assert len(message.signals) == 1
    
    def test_create_xlsx_database(self):
        """Test create_xlsx_database helper."""
        data = {
            'file_path': '/path/to/CAN_DB.xlsx',
            'version': '2.0',
            'messages': [
                {
                    'name': 'Msg1',
                    'message_id': 0x100,
                    'direction': 'rx',
                    'signals': [],
                }
            ],
            'nodes': [{'name': 'ECU', 'comment': ''}],
        }
        
        database = create_xlsx_database(data)
        
        assert database.name == 'CAN_DB'
        assert database.version == '2.0'
        assert len(database.messages) == 1
        assert database.nodes == ['ECU']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
