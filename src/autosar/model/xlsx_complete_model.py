"""
Complete XLSX models with ALL Excel columns mapped.

This module provides comprehensive models that capture EVERY field
from the customer Excel files (Rx/Tx sheets), not just basic CAN data.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .types import ByteOrder, ValueType


class MessageDirection(str, Enum):
    """Message direction from ECU perspective."""
    RX = "rx"  # Received by ECU
    TX = "tx"  # Transmitted by ECU


class InvalidationPolicy(str, Enum):
    """Signal invalidation policy."""
    KEEP = "Keep"
    REPLACE = "Replace" 
    DONT_INVALIDATE = "Dontinvalidate"
    EXTERNAL = "External"


class SignalStatus(str, Enum):
    """Development status of signal."""
    NEW = "New"
    MODIFIED = "Modified"
    UNCHANGED = "Unchanged"
    DELETED = "Deleted"


# ==================== Column Mapping Classes ====================

class ExcelColumnMapping:
    """
    Base class for Excel column mappings.
    
    Provides bidirectional mapping between:
    - Excel column names (as they appear in row 2)
    - Model field names (Python attribute names)
    - Column indices (0-based, after header rows)
    """
    
    @classmethod
    def get_field_for_column(cls, column_name: str) -> Optional[str]:
        """Get model field name for Excel column name."""
        raise NotImplementedError
    
    @classmethod
    def get_column_for_field(cls, field_name: str) -> Optional[str]:
        """Get Excel column name for model field name."""
        raise NotImplementedError
    
    @classmethod
    def get_all_mappings(cls) -> Dict[str, str]:
        """Get all column -> field mappings."""
        raise NotImplementedError


class RxColumnMapping(ExcelColumnMapping):
    """
    Column mapping for Rx (Receive) sheet.
    
    Maps all 44 columns from customer Excel Rx sheet to model fields.
    """
    
    # Section 1: DBC RX Data (Cols 1-13)
    MESSAGE_NAME = ('CAN Message Name', 'message_name', 0)
    MESSAGE_ID = ('CAN Message ID', 'message_id', 1)
    SIGNAL_NAME = ('CAN Signal Name', 'signal_name', 2)
    LEGACY_RX_SRD_NAME = ('Legacy RX SRD Name', 'legacy_rx_srd_name', 3)
    LEGACY_IMPL_NAME = ('Legacy Implementation name', 'legacy_impl_name', 4)
    SIGNAL_SIZE = ('Signal size [in bits]', 'signal_size', 5)
    UNITS = ('Units', 'units', 6)
    SIGNAL_GROUP = ('CAN Signal Group Name', 'signal_group', 7)
    HAS_SNA = ('Signal has SNA?', 'has_sna', 8)
    PERIODICITY = ('Signal Periodicity [ms]', 'periodicity', 9)
    TIMEOUT = ('Signal Timeout [ms]', 'timeout', 10)
    DBC_COMMENT = ('DBC Comment', 'dbc_comment', 11)
    NOTES = ('Notes', 'notes', 12)
    
    # Section 2: Teams Responsible (Cols 14-17)
    START_BIT = ('Start Bit Position', 'start_bit', 13)
    MAIN_FUNCTION = ('MainFunction', 'main_function', 14)
    CONSUMER_SWC = ('Consumer SWC', 'consumer_swc', 15)
    STATUS = ('Status of Signal', 'status', 16)
    
    # Section 3: Received CAN Signal Raw Data (Cols 18-29)
    DATA_ELEMENT_NAME = ('Data Element Name', 'data_element_name', 17)
    DATA_TYPE = ('Data Type', 'data_type', 18)
    DATA_STRUCT_ELEMENT = ('Data Structure Element Name', 'data_struct_element', 19)
    DATA_CONSTRAINT = ('Data Constraint', 'data_constraint', 20)
    COMPU_METHOD = ('Compu Method', 'compu_method', 21)
    INVALID_VALUE = ('Invalid Value', 'invalid_value', 22)
    TYPE_REFERENCE = ('Type Reference', 'type_reference', 23)
    INVALIDATION_POLICY = ('Invalidation Policy', 'invalidation_policy', 24)
    INITIAL_VALUE = ('Initial Value', 'initial_value', 25)
    INITIAL_VALUE_CONST = ('Initial Value Constant Name', 'initial_value_const', 26)
    TIMEOUT_VALUE = ('Timeout Value', 'timeout_value', 27)
    CONVERSION_FUNCTION = ('Conversion Function', 'conversion_function', 28)
    
    # Section 4: Provided CAN Signal Scaled Data (Cols 30-44)
    LONG_NAME = ('Long Name', 'long_name', 29)
    PORT_NAME = ('Data Element Name/\nPort Name', 'port_name', 30)
    DATA_TYPE_SCALED = ('Data Type_Scaled', 'data_type_scaled', 31)
    DATA_STRUCT_ELEMENT_SCALED = ('Data Structure Element Name_Scaled', 'data_struct_element_scaled', 32)
    STRUCT_ELEMENT_TYPE_REF = ('Structure Element Type Reference', 'struct_element_type_ref', 33)
    MAPPED_IDT = ('Mapped IDT', 'mapped_idt', 34)
    DATA_CONSTRAINT_NAME = ('Data Constraint Name', 'data_constraint_name', 35)
    SIGNAL_MIN_VALUE = ('Signal Min Value', 'signal_min_value', 36)
    SIGNAL_MAX_VALUE = ('Signal Max Value', 'signal_max_value', 37)
    COMPU_METHOD_NAME = ('Compu Method Name', 'compu_method_name', 38)
    UNITS_SCALED = ('Units_Scaled', 'units_scaled', 39)
    INITIAL_VALUE_SCALED = ('Initial Value_Scaled', 'initial_value_scaled', 40)
    INVALID_VALUE_SCALED = ('Invalid Value_Scaled', 'invalid_value_scaled', 41)
    INVALIDATION_POLICY_SCALED = ('Invalidation Policy_Scaled', 'invalidation_policy_scaled', 42)
    DDF_UNIT = ('DDF Unit', 'ddf_unit', 43)
    
    @classmethod
    def get_all_mappings(cls) -> Dict[str, str]:
        """Get all column name -> field name mappings."""
        mappings = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, tuple) and len(attr) == 3:
                excel_col, field_name, _ = attr
                mappings[excel_col] = field_name
        return mappings
    
    @classmethod
    def get_field_for_column(cls, column_name: str) -> Optional[str]:
        """Get model field name for Excel column name."""
        return cls.get_all_mappings().get(column_name)
    
    @classmethod
    def get_column_for_field(cls, field_name: str) -> Optional[str]:
        """Get Excel column name for model field name."""
        mappings = cls.get_all_mappings()
        for excel_col, mapped_field in mappings.items():
            if mapped_field == field_name:
                return excel_col
        return None
    
    @classmethod
    def get_column_index(cls, field_name: str) -> Optional[int]:
        """Get 0-based column index for field name."""
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, tuple) and len(attr) == 3:
                _, mapped_field, col_idx = attr
                if mapped_field == field_name:
                    return col_idx
        return None


class TxColumnMapping(ExcelColumnMapping):
    """
    Column mapping for Tx (Transmit) sheet.
    
    Maps all 43 columns from customer Excel Tx sheet to model fields.
    """
    
    # Section 1: DBC Tx Data (Cols 1-10)
    MESSAGE_NAME = ('CAN Message Name', 'message_name', 0)
    MESSAGE_ID = ('CAN Message ID', 'message_id', 1)
    SIGNAL_NAME = ('CAN Signal Name', 'signal_name', 2)
    SIGNAL_GROUP = ('CAN Signal Group Name', 'signal_group', 3)
    SIGNAL_SIZE = ('Signal Size [ in bits ]', 'signal_size', 4)
    UNITS = ('Units', 'units', 5)
    HAS_SNA = ('Signal has SNA?', 'has_sna', 6)
    PERIODICITY = ('Signal Periodicity [ms]', 'periodicity', 7)
    DBC_COMMENT = ('DBC Comment', 'dbc_comment', 8)
    NOTES = ('Notes', 'notes', 9)
    
    # Section 2: Teams Responsible (Cols 11-18)
    START_BIT = ('Start Bit Position', 'start_bit', 10)
    MAIN_FUNCTION = ('MainFunction', 'main_function', 11)
    LEGACY_SRD_DD_NAME = ('Legacy SRD DD Name', 'legacy_srd_dd_name', 12)
    LEGACY_TX_ACCESSOR = ('Legacy TX Accessor Name', 'legacy_tx_accessor_name', 13)
    PMBD_PHASE = ('PMBD Phase required', 'pmbd_phase', 14)
    PMBD_COE_PRODUCER = ('PMBD COE Producer of Data', 'pmbd_coe_producer', 15)
    PRODUCER_SWC = ('Producer SWC', 'producer_swc', 16)
    STATUS = ('Status of Signal', 'status', 17)
    
    # Section 3: Transmitted Raw Signal Data to the BSW (Cols 19-29)
    DATA_ELEMENT_NAME = ('Data Element Name', 'data_element_name', 18)
    DATA_TYPE = ('Data Type', 'data_type', 19)
    DATA_STRUCT_ELEMENT = ('Data Structure Element Name', 'data_struct_element', 20)
    TYPE_REFERENCE = ('Type Reference', 'type_reference', 21)
    DATA_CONSTRAINT = ('Data Constraint', 'data_constraint', 22)
    COMPU_METHOD = ('Compu Method', 'compu_method', 23)
    INVALID_VALUE = ('Invalid Value', 'invalid_value', 24)
    INITIAL_VALUE = ('Initial Value', 'initial_value', 25)
    INITIAL_VALUE_CONST = ('Initial Value Constant Name', 'initial_value_const', 26)
    INVALIDATION_POLICY = ('Invalidation Policy', 'invalidation_policy', 27)
    CONVERSION_FUNCTION = ('Conversion Function', 'conversion_function', 28)
    
    # Section 4: Provided CAN Signal Values for TX (Cols 30-43)
    LONG_NAME = ('Long Name', 'long_name', 29)
    PORT_NAME = ('Port Name', 'port_name', 30)
    DATA_TYPE_SCALED = ('Data Type_Scaled', 'data_type_scaled', 31)
    DATA_STRUCT_ELEMENT_SCALED = ('Data Structure Element Name_Scaled', 'data_struct_element_scaled', 32)
    STRUCT_ELEMENT_TYPE_REF = ('Structure Element Type Reference', 'struct_element_type_ref', 33)
    MAPPED_IDT = ('Mapped IDT', 'mapped_idt', 34)
    DATA_CONSTRAINT_SCALED = ('Data Constraint_Scaled', 'data_constraint_scaled', 35)
    SIGNAL_MIN_VALUE = ('Signal Min Value', 'signal_min_value', 36)
    SIGNAL_MAX_VALUE = ('Signal Max Value', 'signal_max_value', 37)
    COMPU_METHOD_SCALED = ('Compu Method_Scaled', 'compu_method_scaled', 38)
    UNITS_SCALED = ('Units_Scaled', 'units_scaled', 39)
    INITIAL_VALUE_SCALED = ('Initial Value_Scaled', 'initial_value_scaled', 40)
    INVALID_VALUE_SCALED = ('Invalid Value_Scaled', 'invalid_value_scaled', 41)
    INVALIDATION_POLICY_SCALED = ('Invalidation Policy_Scaled', 'invalidation_policy_scaled', 42)
    
    @classmethod
    def get_all_mappings(cls) -> Dict[str, str]:
        """Get all column name -> field name mappings."""
        mappings = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, tuple) and len(attr) == 3:
                excel_col, field_name, _ = attr
                mappings[excel_col] = field_name
        return mappings
    
    @classmethod
    def get_field_for_column(cls, column_name: str) -> Optional[str]:
        """Get model field name for Excel column name."""
        return cls.get_all_mappings().get(column_name)
    
    @classmethod
    def get_column_for_field(cls, field_name: str) -> Optional[str]:
        """Get Excel column name for model field name."""
        mappings = cls.get_all_mappings()
        for excel_col, mapped_field in mappings.items():
            if mapped_field == field_name:
                return excel_col
        return None
    
    @classmethod
    def get_column_index(cls, field_name: str) -> Optional[int]:
        """Get 0-based column index for field name."""
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, tuple) and len(attr) == 3:
                _, mapped_field, col_idx = attr
                if mapped_field == field_name:
                    return col_idx
        return None


# ==================== Complete Signal Model ====================

class CompleteXLSXSignal(BaseModel):
    """
    Complete XLSX Signal with ALL Excel columns.
    
    This model captures EVERY field from the customer Excel Rx/Tx sheets,
    providing complete traceability and data preservation.
    
    Attributes:
        # Core CAN Signal Data
        signal_name: CAN signal name
        signal_size: Signal size in bits
        units: Engineering units
        
        # Excel-Specific Fields
        signal_group: CAN signal group/packet name
        has_sna: Whether signal has SNA (Signal Not Available)
        periodicity: Signal update period in milliseconds
        dbc_comment: Comment from DBC file
        notes: Additional notes
        
        # Legacy Names (RX only)
        legacy_rx_srd_name: Legacy RX SRD name
        legacy_impl_name: Legacy implementation name
        
        # Legacy Names (TX only)
        legacy_srd_dd_name: Legacy SRD DD name
        legacy_tx_accessor_name: Legacy TX accessor name
        
        # Signal Position & Timing
        start_bit: Start bit position in message
        timeout: Signal timeout in milliseconds (RX only)
        main_function: COM MainFunction name
        
        # Software Component Info
        consumer_swc: Consumer SWC name (RX only)
        producer_swc: Producer SWC name (TX only)
        pmbd_phase: PMBD phase required (TX only)
        pmbd_coe_producer: PMBD COE producer (TX only)
        status: Signal development status
        
        # Raw Data Section (BSW Layer)
        data_element_name: Data element name in BSW
        data_type: Raw data type (uint8, uint16, etc.)
        data_struct_element: Data structure element name
        type_reference: Type reference
        data_constraint: Data constraint
        compu_method: Computation method
        invalid_value: Invalid/SNA value (raw)
        initial_value: Initial value (raw)
        initial_value_const: Initial value constant name
        invalidation_policy: Invalidation policy
        timeout_value: Timeout substitution value (RX only)
        conversion_function: Conversion formula (raw <-> scaled)
        
        # Scaled Data Section (Application Layer)
        long_name: Long descriptive name
        port_name: Port interface name
        data_type_scaled: Scaled data type (ADT)
        data_struct_element_scaled: Scaled structure element
        struct_element_type_ref: Structure element type reference
        mapped_idt: Mapped interface data type
        data_constraint_name: Data constraint name (RX)
        data_constraint_scaled: Data constraint (TX)
        signal_min_value: Minimum physical value
        signal_max_value: Maximum physical value
        compu_method_name: Compu method name (RX)
        compu_method_scaled: Compu method (TX)
        units_scaled: Units for scaled value
        initial_value_scaled: Initial value (scaled)
        invalid_value_scaled: Invalid value (scaled)
        invalidation_policy_scaled: Invalidation policy (scaled)
        ddf_unit: DDF unit (RX only)
        
        # Metadata
        direction: Message direction (RX/TX)
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    
    # ========== Core Fields ==========
    signal_name: str = Field(..., description="CAN signal name")
    signal_size: int = Field(..., ge=1, le=64, description="Signal size in bits")
    units: Optional[str] = Field(None, description="Engineering units")
    
    # ========== Excel-Specific Fields ==========
    signal_group: Optional[str] = Field(None, description="CAN signal group/packet name")
    has_sna: bool = Field(default=False, description="Signal has SNA (Signal Not Available)")
    periodicity: Optional[int] = Field(None, ge=0, description="Signal period in ms")
    dbc_comment: Optional[str] = Field(None, description="DBC comment")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # ========== Legacy Names ==========
    legacy_rx_srd_name: Optional[str] = Field(None, description="Legacy RX SRD name")
    legacy_impl_name: Optional[str] = Field(None, description="Legacy implementation name")
    legacy_srd_dd_name: Optional[str] = Field(None, description="Legacy SRD DD name")
    legacy_tx_accessor_name: Optional[str] = Field(None, description="Legacy TX accessor name")
    
    # ========== Signal Position & Timing ==========
    start_bit: Optional[int] = Field(None, ge=0, description="Start bit position")
    timeout: Optional[int] = Field(None, ge=0, description="Signal timeout in ms (RX)")
    main_function: Optional[str] = Field(None, description="COM MainFunction")
    
    # ========== Software Component Info ==========
    consumer_swc: Optional[str] = Field(None, description="Consumer SWC (RX)")
    producer_swc: Optional[str] = Field(None, description="Producer SWC (TX)")
    pmbd_phase: Optional[str] = Field(None, description="PMBD phase (TX)")
    pmbd_coe_producer: Optional[str] = Field(None, description="PMBD COE producer (TX)")
    status: Optional[SignalStatus] = Field(None, description="Signal status")
    
    # ========== Raw Data Section (BSW) ==========
    data_element_name: Optional[str] = Field(None, description="Data element name (BSW)")
    data_type: Optional[str] = Field(None, description="Raw data type")
    data_struct_element: Optional[str] = Field(None, description="Data structure element")
    type_reference: Optional[str] = Field(None, description="Type reference")
    data_constraint: Optional[str] = Field(None, description="Data constraint")
    compu_method: Optional[str] = Field(None, description="Computation method")
    invalid_value: Optional[str] = Field(None, description="Invalid/SNA value (raw)")
    initial_value: Optional[str] = Field(None, description="Initial value (raw)")
    initial_value_const: Optional[str] = Field(None, description="Initial value constant")
    invalidation_policy: Optional[InvalidationPolicy] = Field(None, description="Invalidation policy")
    timeout_value: Optional[str] = Field(None, description="Timeout value (RX)")
    conversion_function: Optional[str] = Field(None, description="Conversion formula")
    
    # ========== Scaled Data Section (Application) ==========
    long_name: Optional[str] = Field(None, description="Long descriptive name")
    port_name: Optional[str] = Field(None, description="Port interface name")
    data_type_scaled: Optional[str] = Field(None, description="Scaled data type (ADT)")
    data_struct_element_scaled: Optional[str] = Field(None, description="Scaled structure element")
    struct_element_type_ref: Optional[str] = Field(None, description="Structure element type ref")
    mapped_idt: Optional[str] = Field(None, description="Mapped interface data type")
    data_constraint_name: Optional[str] = Field(None, description="Data constraint name (RX)")
    data_constraint_scaled: Optional[str] = Field(None, description="Data constraint (TX)")
    signal_min_value: Optional[str] = Field(None, description="Minimum physical value")
    signal_max_value: Optional[str] = Field(None, description="Maximum physical value")
    compu_method_name: Optional[str] = Field(None, description="Compu method name (RX)")
    compu_method_scaled: Optional[str] = Field(None, description="Compu method (TX)")
    units_scaled: Optional[str] = Field(None, description="Units for scaled value")
    initial_value_scaled: Optional[str] = Field(None, description="Initial value (scaled)")
    invalid_value_scaled: Optional[str] = Field(None, description="Invalid value (scaled)")
    invalidation_policy_scaled: Optional[InvalidationPolicy] = Field(None, description="Invalidation policy (scaled)")
    ddf_unit: Optional[str] = Field(None, description="DDF unit (RX)")
    
    # ========== Metadata ==========
    direction: MessageDirection = Field(..., description="Message direction (RX/TX)")
    
    @property
    def is_rx(self) -> bool:
        """Check if this is an RX signal."""
        return self.direction == MessageDirection.RX
    
    @property
    def is_tx(self) -> bool:
        """Check if this is a TX signal."""
        return self.direction == MessageDirection.TX
    
    def get_legacy_names(self) -> List[str]:
        """Get all legacy names for this signal."""
        names = []
        if self.legacy_rx_srd_name:
            names.append(self.legacy_rx_srd_name)
        if self.legacy_impl_name:
            names.append(self.legacy_impl_name)
        if self.legacy_srd_dd_name:
            names.append(self.legacy_srd_dd_name)
        if self.legacy_tx_accessor_name:
            names.append(self.legacy_tx_accessor_name)
        return names
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields."""
        return self.model_dump(exclude_none=False)


# ==================== Complete Message Model ====================

class CompleteXLSXMessage(BaseModel):
    """
    Complete XLSX Message with ALL signals.
    
    Represents a CAN message with all signals containing complete Excel data.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    
    message_name: str = Field(..., description="CAN message name")
    is_extended: bool = Field(default=False, description="Extended frame (29-bit ID)")
    message_id: int = Field(..., ge=0, description="CAN message ID")
    direction: MessageDirection = Field(..., description="Message direction")
    signals: List[CompleteXLSXSignal] = Field(default_factory=list, description="All signals")
    
    # Message-level aggregated info
    cycle_time: Optional[int] = Field(None, description="Message cycle time in ms")
    dlc: Optional[int] = Field(None, ge=0, le=64, description="Data length code")
    
    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: int, info) -> int:
        """Validate message ID based on frame type."""
        is_extended = info.data.get('is_extended', False)
        if not is_extended and v > 0x7FF:
            raise ValueError(f"Standard frame ID must be <= 0x7FF, got 0x{v:X}")
        if is_extended and v > 0x1FFFFFFF:
            raise ValueError(f"Extended frame ID must be <= 0x1FFFFFFF, got 0x{v:X}")
        return v
    
    @property
    def is_rx(self) -> bool:
        """Check if this is an RX message."""
        return self.direction == MessageDirection.RX
    
    @property
    def is_tx(self) -> bool:
        """Check if this is a TX message."""
        return self.direction == MessageDirection.TX
    
    def get_signal_by_name(self, name: str) -> Optional[CompleteXLSXSignal]:
        """Get signal by name."""
        for sig in self.signals:
            if sig.signal_name == name:
                return sig
        return None
    
    def get_signals_by_group(self, group: str) -> List[CompleteXLSXSignal]:
        """Get all signals in a group."""
        return [sig for sig in self.signals if sig.signal_group == group]
    
    def get_all_signal_groups(self) -> List[str]:
        """Get unique signal groups."""
        groups = set(sig.signal_group for sig in self.signals if sig.signal_group)
        return sorted(groups)


# ==================== Complete Database Model ====================

class CompleteXLSXDatabase(BaseModel):
    """
    Complete XLSX Database with ALL messages and signals.
    
    Container for all CAN messages with complete Excel data preservation.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    
    name: str = Field(default="XLSX_Database", description="Database name")
    messages: List[CompleteXLSXMessage] = Field(default_factory=list, description="All messages")
    nodes: List[str] = Field(default_factory=list, description="Network nodes/ECUs")
    
    @property
    def rx_messages(self) -> List[CompleteXLSXMessage]:
        """Get all RX messages."""
        return [msg for msg in self.messages if msg.is_rx]
    
    @property
    def tx_messages(self) -> List[CompleteXLSXMessage]:
        """Get all TX messages."""
        return [msg for msg in self.messages if msg.is_tx]
    
    def get_message_by_id(self, message_id: int) -> Optional[CompleteXLSXMessage]:
        """Get message by ID."""
        for msg in self.messages:
            if msg.message_id == message_id:
                return msg
        return None
    
    def get_message_by_name(self, name: str) -> Optional[CompleteXLSXMessage]:
        """Get message by name."""
        for msg in self.messages:
            if msg.message_name == name:
                return msg
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        rx_msgs = self.rx_messages
        tx_msgs = self.tx_messages
        
        all_signals = []
        for msg in self.messages:
            all_signals.extend(msg.signals)
        
        return {
            'total_messages': len(self.messages),
            'rx_messages': len(rx_msgs),
            'tx_messages': len(tx_msgs),
            'total_signals': len(all_signals),
            'rx_signals': sum(len(m.signals) for m in rx_msgs),
            'tx_signals': sum(len(m.signals) for m in tx_msgs),
            'signals_with_sna': sum(1 for s in all_signals if s.has_sna),
            'unique_signal_groups': len(set(s.signal_group for s in all_signals if s.signal_group)),
        }


# ==================== Export ====================

__all__ = [
    'MessageDirection',
    'InvalidationPolicy',
    'SignalStatus',
    'ExcelColumnMapping',
    'RxColumnMapping',
    'TxColumnMapping',
    'CompleteXLSXSignal',
    'CompleteXLSXMessage',
    'CompleteXLSXDatabase',
]
