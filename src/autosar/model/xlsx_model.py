"""
XLSX (Excel) specific data models.

Defines models for Excel-based CAN configuration with customer-specific fields.
These models extend the base CAN models with additional fields from Excel sheets.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from enum import Enum

from .base import BaseElement, Identifiable
from .can_model import CANSignal, CANMessage, CANDatabase
from .types import ByteOrder, ValueType, SignalType


class MessageDirection(str, Enum):
    """Message direction (Rx/Tx from ECU perspective)."""
    RX = "rx"  # Received by ECU
    TX = "tx"  # Transmitted by ECU


class XLSXSignal(Identifiable):
    """
    Excel-specific CAN Signal definition.
    
    Extends base signal with Excel-specific fields like signal groups,
    legacy names, and SNA (Signal Not Available) information.
    """
    
    # Basic signal properties
    length: int = Field(..., ge=1, le=64, description="Signal length in bits")
    start_bit: int = Field(default=0, ge=0, le=63, description="Start bit position (0 if not calculated)")
    
    # Physical properties
    unit: Optional[str] = Field(None, description="Physical unit (e.g., 'km/h', 'kph', '°C')")
    
    # Excel-specific fields
    signal_group: Optional[str] = Field(
        None,
        description="Signal group name for packet grouping"
    )
    has_sna: bool = Field(
        default=False,
        description="Signal has SNA (Signal Not Available) indicator"
    )
    periodicity: Optional[int] = Field(
        None,
        ge=0,
        description="Signal periodicity/cycle time in milliseconds"
    )
    
    # Legacy mapping (for Rx signals)
    legacy_srd_name: Optional[str] = Field(
        None,
        description="Legacy SRD (Software Requirements Document) name"
    )
    legacy_impl_name: Optional[str] = Field(
        None,
        description="Legacy implementation name"
    )
    
    # Additional metadata
    notes: Optional[str] = Field(None, description="Additional notes or comments")
    dbc_comment: Optional[str] = Field(None, description="DBC file comment")
    
    # Technical properties (with defaults)
    byte_order: ByteOrder = Field(
        default=ByteOrder.LITTLE_ENDIAN,
        description="Byte order (endianness)"
    )
    value_type: ValueType = Field(
        default=ValueType.UNSIGNED,
        description="Value type (signed/unsigned/float)"
    )
    signal_type: SignalType = Field(
        default=SignalType.STANDARD,
        description="Signal type"
    )
    
    # Conversion parameters
    factor: float = Field(default=1.0, description="Scaling factor")
    offset: float = Field(default=0.0, description="Value offset")
    minimum: float = Field(default=0.0, description="Minimum value")
    maximum: float = Field(default=0.0, description="Maximum value")
    
    # Network properties
    receivers: List[str] = Field(
        default_factory=list,
        description="List of receiver nodes"
    )
    
    @field_validator('signal_group')
    @classmethod
    def normalize_signal_group(cls, v: Optional[str]) -> Optional[str]:
        """Normalize signal group name."""
        if v is None or v == '' or v == '-':
            return None
        return v.strip()
    
    def to_can_signal(self) -> CANSignal:
        """
        Convert to standard CANSignal model.
        
        Returns:
            CANSignal instance with mapped fields
        """
        return CANSignal(
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            uuid=self.uuid,
            start_bit=self.start_bit,
            length=self.length,
            byte_order=self.byte_order,
            value_type=self.value_type,
            signal_type=self.signal_type,
            factor=self.factor,
            offset=self.offset,
            min_value=self.minimum,
            max_value=self.maximum,
            unit=self.unit or '',
            receivers=self.receivers,
            comment=self.dbc_comment or self.notes or '',
        )


class XLSXMessage(Identifiable):
    """
    Excel-specific CAN Message definition.
    
    Extends base message with Excel-specific metadata and direction information.
    """
    
    # Define is_extended BEFORE message_id for proper validation
    is_extended: bool = Field(
        default=False,
        description="Extended frame format (29-bit ID)"
    )
    message_id: int = Field(
        ...,
        ge=0,
        le=0x1FFFFFFF,
        description="CAN message ID (11-bit standard or 29-bit extended)"
    )
    
    # Message properties
    dlc: int = Field(
        default=8,
        ge=0,
        le=64,
        description="Data Length Code (0-8 for CAN, up to 64 for CAN FD)"
    )
    
    # Direction (Rx/Tx from ECU perspective)
    direction: MessageDirection = Field(
        ...,
        description="Message direction (rx/tx from ECU perspective)"
    )
    
    # Timing
    cycle_time: Optional[int] = Field(
        None,
        ge=0,
        description="Transmission cycle time in milliseconds"
    )
    
    # Signals
    signals: List[XLSXSignal] = Field(
        default_factory=list,
        description="Signals contained in this message"
    )
    
    # Sender/Receivers
    senders: List[str] = Field(
        default_factory=list,
        description="List of sender nodes"
    )
    
    # Metadata
    comment: Optional[str] = Field(None, description="Message comment")
    
    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: int, info) -> int:
        """Validate message ID range based on frame format."""
        is_extended = info.data.get('is_extended', False)
        if not is_extended and v > 0x7FF:
            raise ValueError(
                f"Standard frame ID must be <= 0x7FF, got 0x{v:X}"
            )
        return v
    
    @property
    def is_rx(self) -> bool:
        """Check if this is an RX message."""
        return self.direction == MessageDirection.RX
    
    @property
    def is_tx(self) -> bool:
        """Check if this is a TX message."""
        return self.direction == MessageDirection.TX
    
    def get_signal_by_name(self, name: str) -> Optional[XLSXSignal]:
        """
        Find signal by name.
        
        Args:
            name: Signal name to search for
            
        Returns:
            XLSXSignal if found, None otherwise
        """
        for signal in self.signals:
            if signal.name == name:
                return signal
        return None
    
    def get_signals_by_group(self, group_name: str) -> List[XLSXSignal]:
        """
        Get all signals belonging to a specific group.
        
        Args:
            group_name: Signal group name
            
        Returns:
            List of signals in the group
        """
        return [
            sig for sig in self.signals
            if sig.signal_group == group_name
        ]
    
    def get_signal_groups(self) -> List[str]:
        """
        Get list of unique signal groups in this message.
        
        Returns:
            List of signal group names (excluding None)
        """
        groups = set()
        for sig in self.signals:
            if sig.signal_group:
                groups.add(sig.signal_group)
        return sorted(groups)
    
    def to_can_message(self) -> CANMessage:
        """
        Convert to standard CANMessage model.
        
        Returns:
            CANMessage instance with mapped fields
        """
        # Convert all signals
        can_signals = [sig.to_can_signal() for sig in self.signals]
        
        return CANMessage(
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            uuid=self.uuid,
            is_extended=self.is_extended,
            message_id=self.message_id,
            dlc=self.dlc,
            signals=can_signals,
            cycle_time=self.cycle_time,
            sender=self.senders[0] if self.senders else None,
            comment=self.comment or '',
        )


class XLSXDatabase(Identifiable):
    """
    Excel-based CAN Database.
    
    Container for messages and metadata loaded from Excel files.
    Provides additional methods for filtering and querying Excel-specific data.
    """
    
    version: str = Field(default="1.0", description="Database version")
    
    messages: List[XLSXMessage] = Field(
        default_factory=list,
        description="All messages (Rx and Tx)"
    )
    
    nodes: List[str] = Field(
        default_factory=list,
        description="List of network nodes"
    )
    
    # Metadata
    source_file: Optional[str] = Field(
        None,
        description="Source Excel file path"
    )
    comment: Optional[str] = Field(None, description="Database comment")
    
    @property
    def rx_messages(self) -> List[XLSXMessage]:
        """Get all RX messages."""
        return [msg for msg in self.messages if msg.is_rx]
    
    @property
    def tx_messages(self) -> List[XLSXMessage]:
        """Get all TX messages."""
        return [msg for msg in self.messages if msg.is_tx]
    
    @property
    def standard_messages(self) -> List[XLSXMessage]:
        """Get all standard frame messages (11-bit ID)."""
        return [msg for msg in self.messages if not msg.is_extended]
    
    @property
    def extended_messages(self) -> List[XLSXMessage]:
        """Get all extended frame messages (29-bit ID)."""
        return [msg for msg in self.messages if msg.is_extended]
    
    def get_message_by_id(self, message_id: int) -> Optional[XLSXMessage]:
        """
        Find message by CAN ID.
        
        Args:
            message_id: CAN message ID
            
        Returns:
            XLSXMessage if found, None otherwise
        """
        for msg in self.messages:
            if msg.message_id == message_id:
                return msg
        return None
    
    def get_message_by_name(self, name: str) -> Optional[XLSXMessage]:
        """
        Find message by name.
        
        Args:
            name: Message name
            
        Returns:
            XLSXMessage if found, None otherwise
        """
        for msg in self.messages:
            if msg.name == name:
                return msg
        return None
    
    def get_all_signal_groups(self) -> List[str]:
        """
        Get list of all unique signal groups in database.
        
        Returns:
            Sorted list of signal group names
        """
        groups = set()
        for msg in self.messages:
            groups.update(msg.get_signal_groups())
        return sorted(groups)
    
    def get_messages_with_signal_group(self, group_name: str) -> List[XLSXMessage]:
        """
        Get all messages containing signals from a specific group.
        
        Args:
            group_name: Signal group name
            
        Returns:
            List of messages containing the signal group
        """
        return [
            msg for msg in self.messages
            if group_name in msg.get_signal_groups()
        ]
    
    def get_statistics(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with various statistics
        """
        total_signals = sum(len(msg.signals) for msg in self.messages)
        signals_with_sna = sum(
            1 for msg in self.messages
            for sig in msg.signals
            if sig.has_sna
        )
        
        return {
            'total_messages': len(self.messages),
            'rx_messages': len(self.rx_messages),
            'tx_messages': len(self.tx_messages),
            'standard_frames': len(self.standard_messages),
            'extended_frames': len(self.extended_messages),
            'total_signals': total_signals,
            'signals_with_sna': signals_with_sna,
            'signal_groups': len(self.get_all_signal_groups()),
            'nodes': len(self.nodes),
        }
    
    def to_can_database(self) -> CANDatabase:
        """
        Convert to standard CANDatabase model.
        
        Returns:
            CANDatabase instance with all messages converted
        """
        # Convert all messages
        can_messages = [msg.to_can_message() for msg in self.messages]
        
        return CANDatabase(
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            uuid=self.uuid,
            version=self.version,
            messages=can_messages,
            nodes=[],  # Node details not preserved in basic conversion
            comment=self.comment or '',
        )


# Helper functions for creating models from parsed data

def create_xlsx_signal(data: dict) -> XLSXSignal:
    """
    Create XLSXSignal from dictionary data.
    
    Args:
        data: Dictionary with signal data from Excel
        
    Returns:
        XLSXSignal instance
    """
    return XLSXSignal(
        name=data['name'],
        short_name=data['name'],
        length=data['length'],
        start_bit=data.get('start_bit', 0),
        unit=data.get('unit'),
        signal_group=data.get('signal_group'),
        has_sna=data.get('has_sna', False),
        periodicity=data.get('periodicity'),
        legacy_srd_name=data.get('legacy_srd_name'),
        legacy_impl_name=data.get('legacy_impl_name'),
        notes=data.get('notes'),
        dbc_comment=data.get('comment'),
        byte_order=data.get('byte_order', ByteOrder.LITTLE_ENDIAN),
        value_type=data.get('value_type', ValueType.UNSIGNED),
        signal_type=data.get('signal_type', SignalType.STANDARD),
        factor=data.get('factor', 1.0),
        offset=data.get('offset', 0.0),
        minimum=data.get('minimum', 0.0),
        maximum=data.get('maximum', 0.0),
        receivers=data.get('receivers', []),
    )


def create_xlsx_message(data: dict) -> XLSXMessage:
    """
    Create XLSXMessage from dictionary data.
    
    Args:
        data: Dictionary with message data from Excel
        
    Returns:
        XLSXMessage instance
    """
    # Convert signals
    signals = [create_xlsx_signal(sig_data) for sig_data in data.get('signals', [])]
    
    # Determine direction
    direction = MessageDirection.RX if data.get('direction') == 'rx' else MessageDirection.TX
    
    return XLSXMessage(
        name=data['name'],
        short_name=data['name'],
        message_id=data['message_id'],
        is_extended=data.get('is_extended', False),
        dlc=data.get('dlc', 8),
        direction=direction,
        cycle_time=data.get('cycle_time'),
        signals=signals,
        senders=data.get('senders', []),
        comment=data.get('comment'),
    )


def create_xlsx_database(data: dict) -> XLSXDatabase:
    """
    Create XLSXDatabase from dictionary data.
    
    Args:
        data: Dictionary with database data from Excel
        
    Returns:
        XLSXDatabase instance
    """
    # Convert messages
    messages = [create_xlsx_message(msg_data) for msg_data in data.get('messages', [])]
    
    # Extract database name from file path
    import os
    name = data.get('name') or os.path.splitext(os.path.basename(data.get('file_path', 'database')))[0]
    
    # Extract node names (handle both dict and string formats)
    nodes_data = data.get('nodes', [])
    if nodes_data and isinstance(nodes_data[0], dict):
        # Convert from dict format to string list
        nodes = [node['name'] for node in nodes_data if 'name' in node]
    else:
        nodes = nodes_data
    
    return XLSXDatabase(
        name=name,
        short_name=name,
        version=data.get('version', '1.0'),
        messages=messages,
        nodes=nodes,
        source_file=data.get('file_path'),
        comment=data.get('comment'),
    )
