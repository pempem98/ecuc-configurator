"""
Custom types and enums for AUTOSAR models.

Defines common enumerations and type aliases used across the model package.
"""

from enum import Enum
from typing import Union, Literal


class ByteOrder(str, Enum):
    """Byte order for multi-byte values."""
    LITTLE_ENDIAN = "little_endian"
    BIG_ENDIAN = "big_endian"
    MOTOROLA = "big_endian"  # Alias
    INTEL = "little_endian"   # Alias


class ValueType(str, Enum):
    """Value type for signals."""
    SIGNED = "signed"
    UNSIGNED = "unsigned"
    FLOAT = "float"
    DOUBLE = "double"


class SignalType(str, Enum):
    """Signal type classification."""
    STANDARD = "standard"
    MULTIPLEXER = "multiplexer"
    MULTIPLEXED = "multiplexed"


class ParameterType(str, Enum):
    """Configuration parameter types."""
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    ENUMERATION = "ENUMERATION"
    REFERENCE = "REFERENCE"


class ModuleDefType(str, Enum):
    """AUTOSAR BSW module types."""
    CAN_IF = "CanIf"
    CAN_TP = "CanTp"
    CAN_SM = "CanSM"
    COM = "Com"
    COM_M = "ComM"
    DCM = "Dcm"
    DEM = "Dem"
    DET = "Det"
    ECUM = "EcuM"
    FEE = "Fee"
    FLS = "Fls"
    LIN_IF = "LinIf"
    LIN_SM = "LinSM"
    MCU = "Mcu"
    NM = "Nm"
    NVM = "NvM"
    OS = "Os"
    PDU_R = "PduR"
    PORT = "Port"
    RTE = "Rte"
    SPI = "Spi"
    WDG = "Wdg"
    WDGM = "WdgM"


class LINNodeType(str, Enum):
    """LIN node types."""
    MASTER = "master"
    SLAVE = "slave"


class FrameType(str, Enum):
    """Frame types for LIN."""
    UNCONDITIONAL = "unconditional"
    EVENT_TRIGGERED = "event_triggered"
    SPORADIC = "sporadic"
    DIAGNOSTIC = "diagnostic"


class Multiplicity(str, Enum):
    """Container/parameter multiplicity."""
    ZERO_OR_ONE = "0..1"
    ONE = "1"
    ZERO_OR_MORE = "0..*"
    ONE_OR_MORE = "1..*"


# Type aliases for common patterns
NumericValue = Union[int, float]
ParameterValue = Union[str, int, float, bool]
ReferenceType = str
