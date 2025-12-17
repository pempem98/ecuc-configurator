"""
CAN (Controller Area Network) data models.

Defines models for CAN database, messages, signals, and nodes.
"""

from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator, model_validator

from .base import BaseElement, Identifiable
from .types import ByteOrder, ValueType, SignalType, NumericValue


class ValueTableEntry(BaseElement):
    """Single entry in a value table (enum mapping)."""
    
    value: int = Field(..., description="Numeric value")
    label: str = Field(..., description="Human-readable label")


class ValueTable(BaseElement):
    """
    Value table for signal enumeration.
    
    Maps numeric values to human-readable labels.
    """
    
    entries: List[ValueTableEntry] = Field(
        default_factory=list,
        description="Value table entries"
    )
    
    def get_label(self, value: int) -> Optional[str]:
        """Get label for a numeric value."""
        for entry in self.entries:
            if entry.value == value:
                return entry.label
        return None
    
    def get_value(self, label: str) -> Optional[int]:
        """Get numeric value for a label."""
        for entry in self.entries:
            if entry.label == label:
                return entry.value
        return None


class CANSignal(Identifiable):
    """
    CAN Signal definition.
    
    Represents a signal within a CAN message.
    """
    
    start_bit: int = Field(..., ge=0, le=63, description="Start bit position")
    length: int = Field(..., ge=1, le=64, description="Signal length in bits")
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
        description="Signal type (standard/multiplexer/multiplexed)"
    )
    
    # Physical value conversion: physical_value = raw_value * factor + offset
    factor: float = Field(default=1.0, description="Scaling factor")
    offset: float = Field(default=0.0, description="Value offset")
    
    # Physical value range
    min_value: Optional[NumericValue] = Field(None, description="Minimum physical value")
    max_value: Optional[NumericValue] = Field(None, description="Maximum physical value")
    
    unit: Optional[str] = Field(None, description="Physical unit (e.g., 'km/h', '°C')")
    
    # Initial/default value
    initial_value: Optional[NumericValue] = Field(
        None,
        description="Initial value (raw)"
    )
    
    # Multiplexing
    multiplex_indicator: Optional[str] = Field(
        None,
        description="Multiplexer indicator (e.g., 'M', 'm0', 'm1')"
    )
    
    # Value table for enumerations
    value_table: Optional[ValueTable] = Field(
        None,
        description="Value table for enumerated signals"
    )
    
    # Receivers
    receivers: List[str] = Field(
        default_factory=list,
        description="List of receiver node names"
    )
    
    @field_validator('start_bit', 'length')
    @classmethod
    def validate_bit_range(cls, v: int) -> int:
        """Validate bit positions and lengths."""
        if v < 0:
            raise ValueError("Bit position/length must be non-negative")
        return v
    
    @model_validator(mode='after')
    def validate_signal_fits_in_message(self):
        """Validate that signal fits within message boundaries."""
        if self.byte_order == ByteOrder.LITTLE_ENDIAN:
            end_bit = self.start_bit + self.length - 1
        else:  # Big endian (Motorola)
            end_bit = self.start_bit + self.length - 1
        
        if end_bit > 63:
            raise ValueError(
                f"Signal extends beyond message boundary: "
                f"start_bit={self.start_bit}, length={self.length}"
            )
        return self
    
    def decode(self, raw_value: int) -> float:
        """Convert raw value to physical value."""
        return raw_value * self.factor + self.offset
    
    def encode(self, physical_value: float) -> int:
        """Convert physical value to raw value."""
        return int((physical_value - self.offset) / self.factor)


class CANMessage(Identifiable):
    """
    CAN Message definition.
    
    Represents a CAN frame with its signals.
    """
    
    # Define is_extended BEFORE message_id so validator can access it
    is_extended: bool = Field(
        default=False,
        description="Extended frame format (29-bit ID)"
    )
    message_id: int = Field(
        ...,
        ge=0,
        le=0x1FFFFFFF,
        description="CAN message ID (11-bit or 29-bit)"
    )
    dlc: int = Field(..., ge=0, le=8, description="Data Length Code (0-8 bytes)")
    
    def __init__(self, **data):
        # Allow 'length' as alias for 'dlc'
        if 'length' in data and 'dlc' not in data:
            data['dlc'] = data.pop('length')
        super().__init__(**data)
    
    @property
    def length(self) -> int:
        """Alias for dlc (returns DLC value)."""
        return self.dlc
    
    signals: List[CANSignal] = Field(
        default_factory=list,
        description="Signals in this message"
    )
    
    # Transmission properties
    cycle_time: Optional[int] = Field(
        None,
        ge=0,
        description="Transmission cycle time in milliseconds"
    )
    is_event_triggered: bool = Field(
        default=False,
        description="Event-triggered transmission"
    )
    
    # Sender
    sender: Optional[str] = Field(None, description="Sender node name")
    
    # Attributes
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
    
    def get_signal(self, name: str) -> Optional[CANSignal]:
        """Get signal by name."""
        for signal in self.signals:
            if signal.name == name or signal.short_name == name:
                return signal
        return None
    
    def is_tx(self) -> bool:
        """
        Check if this message is transmitted by the current ECU.
        
        Note: This is a simplified implementation. In real usage,
        you would need to know the current ECU context.
        For now, returns True if sender is set.
        """
        return self.sender is not None
    
    def is_rx(self) -> bool:
        """
        Check if this message is received by the current ECU.
        
        Note: This is a simplified implementation. In real usage,
        you would need to know the current ECU context and receivers.
        For now, returns True (assuming all messages can be received).
        """
        return True


class CANNode(Identifiable):
    """
    CAN Node (ECU) definition.
    
    Represents an ECU node in the CAN network.
    """
    
    transmitted_messages: List[str] = Field(
        default_factory=list,
        description="List of transmitted message names"
    )
    received_messages: List[str] = Field(
        default_factory=list,
        description="List of received message names"
    )
    
    # Node attributes
    comment: Optional[str] = Field(None, description="Node comment")
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom attributes"
    )


class CANDatabase(BaseElement):
    """
    Complete CAN Database.
    
    Contains all messages, signals, and nodes for a CAN network.
    """
    
    version: str = Field(default="1.0", description="Database version")
    protocol: str = Field(default="CAN", description="Protocol type")
    baudrate: Optional[int] = Field(None, description="CAN baudrate in bps")
    
    messages: List[CANMessage] = Field(
        default_factory=list,
        description="All CAN messages"
    )
    nodes: List[CANNode] = Field(
        default_factory=list,
        description="All CAN nodes"
    )
    value_tables: List[ValueTable] = Field(
        default_factory=list,
        description="Shared value tables"
    )
    
    # Attributes
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Database-level attributes"
    )
    
    def get_message_by_id(self, message_id: int) -> Optional[CANMessage]:
        """Get message by CAN ID."""
        for message in self.messages:
            if message.message_id == message_id:
                return message
        return None
    
    def get_message_by_name(self, name: str) -> Optional[CANMessage]:
        """Get message by name."""
        for message in self.messages:
            if message.name == name:
                return message
        return None
    
    def get_node(self, name: str) -> Optional[CANNode]:
        """Get node by name."""
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def get_value_table(self, name: str) -> Optional[ValueTable]:
        """Get value table by name."""
        for vt in self.value_tables:
            if vt.name == name:
                return vt
        return None
