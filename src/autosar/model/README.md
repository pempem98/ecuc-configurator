# AUTOSAR Model Module

## Tổng quan

Module **Model** định nghĩa các data models và structures được sử dụng trong hệ thống ECUC Configurator. Các model này đại diện cho:

- **CAN Network Elements** - Messages, Signals, Nodes
- **LIN Network Elements** - Frames, Signals, Schedule Tables
- **AUTOSAR Elements** - ECU Configuration, Containers, Parameters
- **Common Elements** - Base classes và shared structures

Tất cả models được implement bằng **Pydantic** để đảm bảo type safety và validation.

## Kiến trúc

```
model/
├── README.md              # File tài liệu này
├── __init__.py            # Package initialization & exports
├── base.py                # Base classes cho tất cả models
├── can_model.py           # CAN network models
├── lin_model.py           # LIN network models
├── autosar_model.py       # AUTOSAR configuration models
├── ecu_model.py           # ECU configuration models
├── parameter_model.py     # Parameter definitions
└── types.py               # Custom types và enums
```

## Các thành phần chính

### 1. Base Models (`base.py`)

Base classes cho tất cả models:

```python
class BaseElement(BaseModel):
    """Base class cho tất cả elements"""
    name: str
    description: Optional[str] = None
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Identifiable(BaseElement):
    """Element có thể reference được"""
    short_name: str
    long_name: Optional[str] = None
```

### 2. CAN Models (`can_model.py`)

Models cho CAN network:

- `CANDatabase` - Toàn bộ CAN database
- `CANMessage` - CAN message definition
- `CANSignal` - CAN signal definition
- `CANNode` - ECU node trong network
- `ValueTable` - Enum values cho signal

### 3. LIN Models (`lin_model.py`)

Models cho LIN network:

- `LINNetwork` - LIN cluster configuration
- `LINFrame` - LIN frame definition
- `LINSignal` - LIN signal definition
- `LINNode` - Master/Slave node
- `ScheduleTable` - LIN schedule table

### 4. AUTOSAR Models (`autosar_model.py`)

Models cho AUTOSAR elements:

- `ARPackage` - AUTOSAR package
- `Component` - Software component
- `PortInterface` - Port interface definition
- `DataElement` - Data element trong interface

### 5. ECU Models (`ecu_model.py`)

Models cho ECU configuration:

- `EcuConfiguration` - Toàn bộ ECU config
- `Module` - BSW module (CanIf, ComM, etc.)
- `Container` - Configuration container
- `Parameter` - Configuration parameter

## Dependencies

```txt
pydantic >= 2.0.0
typing-extensions
python >= 3.8
```

## Sử dụng

### Ví dụ tạo CAN Message

```python
from autosar.model import CANMessage, CANSignal

signal = CANSignal(
    name="VehicleSpeed",
    start_bit=0,
    length=16,
    byte_order="little_endian",
    value_type="unsigned",
    factor=0.01,
    offset=0,
    unit="km/h",
    min_value=0,
    max_value=655.35
)

message = CANMessage(
    name="Powertrain_01",
    message_id=0x100,
    dlc=8,
    cycle_time=100,
    signals=[signal]
)
```

### Ví dụ tạo ECU Configuration

```python
from autosar.model import EcuConfiguration, Module, Container, Parameter

param = Parameter(
    name="CanIfMaxTxDlc",
    type="INTEGER",
    value=8,
    min_value=0,
    max_value=64
)

container = Container(
    name="CanIfInitConfiguration",
    parameters=[param]
)

module = Module(
    name="CanIf",
    version="1.0.0",
    containers=[container]
)

ecu_config = EcuConfiguration(
    name="MyECU",
    modules=[module]
)
```

## Validation

Tất cả models tự động validate:

```python
from autosar.model import CANSignal
from pydantic import ValidationError

try:
    signal = CANSignal(
        name="InvalidSignal",
        start_bit=0,
        length=65  # Invalid: > 64
    )
except ValidationError as e:
    print(e)
```

## Serialization

Models hỗ trợ JSON serialization:

```python
# To dict
data = message.model_dump()

# To JSON string
json_str = message.model_dump_json(indent=2)

# From dict
message = CANMessage.model_validate(data)

# From JSON
message = CANMessage.model_validate_json(json_str)
```

## Best Practices

1. **Immutability**: Sử dụng `frozen=True` cho immutable models
2. **Validation**: Thêm custom validators khi cần
3. **Documentation**: Docstring cho tất cả classes và fields
4. **Type hints**: Luôn sử dụng type hints đầy đủ
5. **Default values**: Cung cấp defaults hợp lý

## Roadmap

- [x] Base model design
- [ ] CAN models implementation
- [ ] LIN models implementation
- [ ] AUTOSAR models implementation
- [ ] ECU models implementation
- [ ] Parameter models implementation
- [ ] Custom types và enums
- [ ] Model validators
- [ ] Unit tests
- [ ] Documentation

---

**Next:** Implement các model classes
