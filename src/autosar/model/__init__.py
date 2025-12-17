"""
AUTOSAR Model Module

Provides data models for CAN, LIN, AUTOSAR, and ECU configuration elements.
"""

from .base import BaseElement, Identifiable
from .types import (
    ByteOrder,
    ValueType,
    SignalType,
    ParameterType,
    ModuleDefType,
    FrameType,
)

# CAN Models
from .can_model import (
    CANDatabase,
    CANMessage,
    CANSignal,
    CANNode,
    ValueTable,
    ValueTableEntry,
)

# XLSX Models
from .xlsx_model import (
    XLSXDatabase,
    XLSXMessage,
    XLSXSignal,
    MessageDirection,
    create_xlsx_signal,
    create_xlsx_message,
    create_xlsx_database,
)

# Complete XLSX Models (with ALL Excel columns)
from .xlsx_complete_model import (
    CompleteXLSXDatabase,
    CompleteXLSXMessage,
    CompleteXLSXSignal,
    RxColumnMapping,
    TxColumnMapping,
    ExcelColumnMapping,
    InvalidationPolicy,
    SignalStatus,
)

# LIN Models
from .lin_model import (
    LINNetwork,
    LINFrame,
    LINSignal,
    LINNode,
    LINNodeType,
    ScheduleTable,
    ScheduleEntry,
)

# AUTOSAR Models
from .autosar_model import (
    ARPackage,
    Component,
    PortInterface,
    DataElement,
)

# ECU Models
from .ecu_model import (
    EcuConfiguration,
    Module,
    Container,
    Parameter,
)

# ECUC Models
from .ecuc_model import (
    AutosarVersion,
    ECUCParameterType,
    ECUCParameterValue,
    ECUCContainerValue,
    ECUCModuleConfigurationValues,
    ECUCValueCollection,
    ECUCProject,
)

__all__ = [
    # Base
    "BaseElement",
    "Identifiable",
    # Types
    "ByteOrder",
    "ValueType",
    "SignalType",
    "ParameterType",
    "ModuleDefType",
    "FrameType",
    # CAN
    "CANDatabase",
    "CANMessage",
    "CANSignal",
    "CANNode",
    "ValueTable",
    "ValueTableEntry",
    # XLSX
    "XLSXDatabase",
    "XLSXMessage",
    "XLSXSignal",
    "MessageDirection",
    "create_xlsx_signal",
    "create_xlsx_message",
    "create_xlsx_database",
    # Complete XLSX (ALL columns)
    "CompleteXLSXDatabase",
    "CompleteXLSXMessage",
    "CompleteXLSXSignal",
    "RxColumnMapping",
    "TxColumnMapping",
    "ExcelColumnMapping",
    "InvalidationPolicy",
    "SignalStatus",
    # LIN
    "LINNetwork",
    "LINFrame",
    "LINSignal",
    "LINNode",
    "LINNodeType",
    "ScheduleTable",
    "ScheduleEntry",
    # AUTOSAR
    "ARPackage",
    "Component",
    "PortInterface",
    "DataElement",
    # ECU
    "EcuConfiguration",
    "Module",
    "Container",
    "Parameter",
    # ECUC
    "AutosarVersion",
    "ECUCParameterType",
    "ECUCParameterValue",
    "ECUCContainerValue",
    "ECUCModuleConfigurationValues",
    "ECUCValueCollection",
    "ECUCProject",
]

__version__ = "0.1.0"
