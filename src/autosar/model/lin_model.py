"""
LIN (Local Interconnect Network) data models.

Defines models for LIN network, frames, signals, nodes, and schedule tables.
"""

from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator

from .base import BaseElement, Identifiable
from .types import ByteOrder, ValueType, LINNodeType, FrameType, NumericValue


class LINSignal(Identifiable):
    """
    LIN Signal definition.
    
    Represents a signal within a LIN frame.
    """
    
    start_bit: int = Field(..., ge=0, description="Start bit position in frame")
    length: int = Field(..., ge=1, le=64, description="Signal length in bits")
    
    # Value conversion
    factor: float = Field(default=1.0, description="Scaling factor")
    offset: float = Field(default=0.0, description="Value offset")
    
    min_value: Optional[NumericValue] = Field(None, description="Minimum value")
    max_value: Optional[NumericValue] = Field(None, description="Maximum value")
    
    unit: Optional[str] = Field(None, description="Physical unit")
    initial_value: Optional[NumericValue] = Field(None, description="Initial value")
    
    # Publisher and subscribers
    publisher: Optional[str] = Field(None, description="Publishing node")
    subscribers: List[str] = Field(
        default_factory=list,
        description="Subscribing nodes"
    )


class LINFrame(Identifiable):
    """
    LIN Frame definition.
    
    Represents a LIN frame with its signals.
    """
    
    frame_id: int = Field(..., ge=0, le=0x3F, description="LIN frame ID (0-63)")
    frame_type: FrameType = Field(
        default=FrameType.UNCONDITIONAL,
        description="Frame type"
    )
    length: int = Field(..., ge=1, le=8, description="Frame length in bytes")
    
    signals: List[LINSignal] = Field(
        default_factory=list,
        description="Signals in this frame"
    )
    
    # Publisher node
    publisher: Optional[str] = Field(None, description="Publisher node name")
    
    @field_validator('frame_id')
    @classmethod
    def validate_frame_id(cls, v: int) -> int:
        """Validate LIN frame ID is in valid range."""
        if not (0 <= v <= 0x3F):
            raise ValueError(f"LIN frame ID must be 0-63, got {v}")
        return v


class LINNode(Identifiable):
    """
    LIN Node definition.
    
    Represents a master or slave node in LIN network.
    """
    
    node_type: LINNodeType = Field(..., description="Master or slave node")
    protocol_version: str = Field(default="2.1", description="LIN protocol version")
    
    # Published and subscribed frames
    published_frames: List[str] = Field(
        default_factory=list,
        description="Frame names published by this node"
    )
    subscribed_frames: List[str] = Field(
        default_factory=list,
        description="Frame names subscribed by this node"
    )
    
    # Diagnostic support
    supports_diagnostics: bool = Field(
        default=False,
        description="Node supports diagnostic frames"
    )
    
    # Configuration
    configured_nad: Optional[int] = Field(
        None,
        ge=1,
        le=127,
        description="Configured Node Address (NAD)"
    )
    initial_nad: Optional[int] = Field(
        None,
        ge=1,
        le=127,
        description="Initial NAD"
    )
    supplier_id: Optional[int] = Field(None, description="Supplier ID")
    function_id: Optional[int] = Field(None, description="Function ID")


class ScheduleEntry(BaseElement):
    """Entry in a LIN schedule table."""
    
    frame_name: str = Field(..., description="Name of frame to transmit")
    delay: float = Field(..., ge=0, description="Delay in milliseconds")
    position: int = Field(..., ge=0, description="Position in schedule")


class ScheduleTable(Identifiable):
    """
    LIN Schedule Table.
    
    Defines the transmission schedule for LIN frames.
    """
    
    entries: List[ScheduleEntry] = Field(
        default_factory=list,
        description="Schedule entries"
    )
    
    def get_total_duration(self) -> float:
        """Calculate total schedule duration in milliseconds."""
        return sum(entry.delay for entry in self.entries)
    
    def get_frame_cycle_time(self, frame_name: str) -> Optional[float]:
        """Get cycle time for a specific frame."""
        # In a simple repeating schedule, cycle time = total duration
        if any(entry.frame_name == frame_name for entry in self.entries):
            return self.get_total_duration()
        return None


class LINNetwork(BaseElement):
    """
    Complete LIN Network definition.
    
    Contains all frames, signals, nodes, and schedule tables for a LIN cluster.
    """
    
    protocol_version: str = Field(default="2.1", description="LIN protocol version")
    language_version: str = Field(default="2.1", description="LDF language version")
    speed: float = Field(default=19.2, description="Bus speed in kbps")
    
    @property
    def baudrate(self) -> float:
        """Alias for speed (returns speed in bps for compatibility)."""
        return self.speed * 1000  # Convert kbps to bps
    
    @property
    def nodes(self) -> List[LINNode]:
        """Get all nodes (master + slaves) as a list."""
        result = []
        if self.master_node:
            result.append(self.master_node)
        result.extend(self.slave_nodes)
        return result
    
    # Master node (required for LIN)
    master_node: Optional[LINNode] = Field(None, description="Master node")
    
    # Slave nodes
    slave_nodes: List[LINNode] = Field(
        default_factory=list,
        description="Slave nodes"
    )
    
    # Frames and signals
    frames: List[LINFrame] = Field(
        default_factory=list,
        description="All LIN frames"
    )
    
    # Schedule tables
    schedule_tables: List[ScheduleTable] = Field(
        default_factory=list,
        description="Schedule tables"
    )
    
    # Diagnostic configuration
    diagnostic_nad_min: int = Field(default=0x01, description="Min diagnostic NAD")
    diagnostic_nad_max: int = Field(default=0x7F, description="Max diagnostic NAD")
    
    def get_frame_by_id(self, frame_id: int) -> Optional[LINFrame]:
        """Get frame by ID."""
        for frame in self.frames:
            if frame.frame_id == frame_id:
                return frame
        return None
    
    def get_frame_by_name(self, name: str) -> Optional[LINFrame]:
        """Get frame by name."""
        for frame in self.frames:
            if frame.name == name:
                return frame
        return None
    
    def get_node(self, name: str) -> Optional[LINNode]:
        """Get node by name."""
        if self.master_node and self.master_node.name == name:
            return self.master_node
        for node in self.slave_nodes:
            if node.name == name:
                return node
        return None
    
    def get_schedule_table(self, name: str) -> Optional[ScheduleTable]:
        """Get schedule table by name."""
        for table in self.schedule_tables:
            if table.name == name:
                return table
        return None
    
    def get_all_nodes(self) -> List[LINNode]:
        """Get all nodes (master + slaves)."""
        nodes = []
        if self.master_node:
            nodes.append(self.master_node)
        nodes.extend(self.slave_nodes)
        return nodes
