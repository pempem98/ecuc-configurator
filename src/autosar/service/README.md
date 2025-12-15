# AUTOSAR Service Layer

## Overview

Service layer cung cấp business logic để xử lý dữ liệu từ các loader, validate, merge và generate ECUC configuration files.

## Components

### ECUCService

Service chính để quản lý ECUC configuration generation.

**Chức năng:**
- Load dữ liệu từ DBC, LDF files
- Validate consistency của dữ liệu
- Merge data từ nhiều sources
- Generate ECUC configuration values
- Support AUTOSAR AR4.2.2 và AR4.5

**Usage:**

```python
from autosar.service import ECUCService
from autosar.model import AutosarVersion

# Create service
service = ECUCService(autosar_version=AutosarVersion.AR_4_2_2)

# Load network files
service.load_dbc('networks/body_can.dbc', network_name='BodyCAN')
service.load_ldf('networks/door_lin.ldf', network_name='DoorLIN')

# Validate data
service.validate_data()

# Generate ECUC project
project = service.generate_ecuc_project(
    project_name="BodyECU",
    ecu_instance="BodyECU_Instance_1",
    modules=['CanIf', 'Can', 'LinIf', 'Lin']
)
```

## Supported Modules

Service có thể generate configuration cho các BSW modules:

### CAN Modules

#### CanIf (CAN Interface)
- CanIfCtrlCfg - Controller configuration
- CanIfTxPduCfg - TX PDU configuration
- CanIfRxPduCfg - RX PDU configuration

#### Can (CAN Driver)
- CanGeneral - General configuration
- CanController - Controller settings (baudrate, etc.)

### LIN Modules

#### LinIf (LIN Interface)
- LinIfGlobalConfig - Global configuration
- LinIfChannel - Channel configuration
- LinIfFrame - Frame configuration

#### Lin (LIN Driver)
- LinGeneral - General configuration
- LinChannel - Channel settings (baudrate, etc.)

### Planned Modules
- CanTp (CAN Transport Protocol)
- PduR (PDU Router)
- Com (Communication Manager)
- ComM (Communication Manager)

## Data Validation

Service thực hiện các validation sau:

### CAN Networks
- ✓ No duplicate message IDs
- ✓ Signals fit within message size
- ✓ Valid byte order
- ✓ Valid message cycle times

### LIN Networks
- ✓ No duplicate frame IDs
- ✓ Signals fit within frame size
- ✓ Valid frame types
- ✓ Valid schedule tables

### Cross-Network
- ✓ Consistent signal definitions
- ✓ Valid node references
- ✓ No conflicting configurations

## ECUC Project Structure

Generated ECUC project có cấu trúc:

```
ECUCProject
├── autosar_version: AR4.2.2 / AR4.5
├── ecu_instance: "ECU_Name"
├── value_collection: ECUCValueCollection
│   ├── modules: List[ECUCModuleConfigurationValues]
│   │   ├── CanIf
│   │   │   └── containers
│   │   │       ├── CanIfInitCfg
│   │   │       │   ├── CanIfCtrlCfg
│   │   │       │   ├── CanIfTxPduCfg
│   │   │       │   └── CanIfRxPduCfg
│   │   ├── Can
│   │   │   └── containers
│   │   │       ├── CanGeneral
│   │   │       └── CanConfigSet
│   │   │           └── CanController
│   │   └── ...
└── metadata
    ├── generated_at
    ├── generator
    └── version
```

## Examples

### Example 1: Basic CAN Configuration

```python
from autosar.service import ECUCService
from autosar.model import AutosarVersion

service = ECUCService(autosar_version=AutosarVersion.AR_4_2_2)

# Load CAN network
service.load_dbc('powertrain.dbc')

# Validate
service.validate_data()

# Generate
project = service.generate_ecuc_project(
    project_name="PowertrainECU",
    ecu_instance="Powertrain_1",
    modules=['CanIf', 'Can']
)

# Get summary
summary = service.get_summary()
print(f"Generated {len(project.value_collection.modules)} modules")
```

### Example 2: Multiple Networks

```python
service = ECUCService()

# Load multiple networks
service.load_dbc('body_can.dbc', network_name='BodyCAN')
service.load_dbc('chassis_can.dbc', network_name='ChassisCAN')
service.load_ldf('door_lin.ldf', network_name='DoorLIN')

# Validate all
service.validate_data()

# Generate complete configuration
project = service.generate_ecuc_project(
    project_name="GatewayECU",
    ecu_instance="Gateway_1",
    modules=['CanIf', 'Can', 'LinIf', 'Lin', 'PduR']
)
```

### Example 3: AR4.5 Configuration

```python
from autosar.model import AutosarVersion

# Create service for AR4.5
service = ECUCService(autosar_version=AutosarVersion.AR_4_5_0)

service.load_dbc('network.dbc')

# Generate AR4.5 compatible configuration
project = service.generate_ecuc_project(
    project_name="ModernECU",
    ecu_instance="Modern_1",
    modules=['CanIf', 'Can']
)

assert project.autosar_version == AutosarVersion.AR_4_5_0
```

## Service Methods

### Loading Methods

#### `load_dbc(file_path, network_name=None)`
Load CAN network from DBC file.

**Parameters:**
- `file_path`: Path to DBC file
- `network_name`: Optional network name (default: filename)

**Returns:** `CANNetwork`

**Raises:** `ECUCServiceException`

#### `load_ldf(file_path, network_name=None)`
Load LIN network from LDF file.

**Parameters:**
- `file_path`: Path to LDF file
- `network_name`: Optional network name (default: filename)

**Returns:** `LINNetwork`

**Raises:** `ECUCServiceException`

### Validation Methods

#### `validate_data()`
Validate all loaded data for consistency.

**Returns:** `bool` - True if valid

**Raises:** `ValidationError` - If validation fails

**Checks:**
- Duplicate IDs
- Signal/message size consistency
- Valid references
- Correct data types

### Generation Methods

#### `generate_ecuc_project(project_name, ecu_instance, modules=None)`
Generate complete ECUC project.

**Parameters:**
- `project_name`: Name of the project
- `ecu_instance`: ECU instance identifier
- `modules`: List of module names to generate (None = auto-detect)

**Returns:** `ECUCProject`

**Raises:** `GenerationError`

**Supported Modules:**
- `'CanIf'` - CAN Interface
- `'Can'` - CAN Driver
- `'LinIf'` - LIN Interface
- `'Lin'` - LIN Driver
- `'CanTp'` - CAN Transport (planned)
- `'PduR'` - PDU Router (planned)

### Utility Methods

#### `get_summary()`
Get summary statistics of loaded data.

**Returns:** Dictionary with:
```python
{
    'autosar_version': str,
    'can_networks': int,
    'lin_networks': int,
    'source_files': int,
    'networks': {
        'NetworkName': {
            'type': 'CAN' | 'LIN',
            'baudrate': int,
            'messages' | 'frames': int,
            'signals': int,
            'nodes': int
        }
    }
}
```

#### `clear()`
Clear all loaded data and reset service.

## Error Handling

Service sử dụng custom exceptions:

### ECUCServiceException
Base exception cho tất cả service errors.

### DataMergeError
Raised khi merge data từ nhiều sources fails.

### ValidationError
Raised khi validation fails.

### GenerationError
Raised khi ECUC generation fails.

**Example:**

```python
from autosar.service import ECUCService, ValidationError

service = ECUCService()

try:
    service.load_dbc('invalid.dbc')
except Exception as e:
    print(f"Load failed: {e}")

try:
    service.validate_data()
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Configuration Best Practices

### 1. Load Order
Load networks theo thứ tự logical:
1. Primary CAN networks
2. Secondary CAN networks
3. LIN networks
4. Other network types

### 2. Validation
Luôn validate trước khi generate:
```python
service.validate_data()  # Required before generation
project = service.generate_ecuc_project(...)
```

### 3. Module Selection
Chỉ generate modules cần thiết:
```python
# Good: Specific modules
modules=['CanIf', 'Can']

# Avoid: Auto-detect nếu không cần tất cả
modules=None  # Generates all detected modules
```

### 4. Naming Conventions
Sử dụng clear, consistent names:
```python
project_name="BodyControlModule_Config"  # Good
ecu_instance="BCM_Instance_1"  # Good

project_name="test"  # Avoid
```

### 5. Error Handling
Handle exceptions properly:
```python
try:
    service.load_dbc(file_path)
except FileNotFoundError:
    # Handle missing file
    pass
except ParserError:
    # Handle parsing error
    pass
```

## Performance Considerations

### Caching
Loaders có built-in caching:
```python
# First load: parses file
network1 = service.load_dbc('network.dbc')

# Second load: uses cache (if same file)
network2 = service.load_dbc('network.dbc')
```

### Memory Management
Clear service khi không cần:
```python
service.clear()  # Frees memory
```

### Large Networks
Với large networks, generate theo batch:
```python
# Generate modules separately
project1 = service.generate_ecuc_project(
    "ECU1", "Instance1", modules=['CanIf']
)
project2 = service.generate_ecuc_project(
    "ECU1", "Instance1", modules=['Can']
)
```

## Testing

Service có comprehensive test coverage:

```bash
# Run service tests
pytest tests/test_service_ecuc.py -v

# Run with coverage
pytest tests/test_service_ecuc.py --cov=src/autosar/service
```

## Future Enhancements

### Planned Features
- [ ] XLSX loader integration
- [ ] ARXML loader integration
- [ ] More BSW modules (CanTp, PduR, Com)
- [ ] Signal routing configuration
- [ ] Multi-ECU configuration
- [ ] Configuration optimization
- [ ] Conflict resolution
- [ ] Import/export to other formats

### API Stability
Current API is considered **beta**. Breaking changes may occur in future versions.

## See Also

- [Model Documentation](../model/README.md)
- [Loader Documentation](../loader/README.md)
- [Generator Documentation](../generator/README.md)
- [Examples](../../examples/)
