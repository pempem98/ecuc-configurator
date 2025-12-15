# AUTOSAR ECUC Configurator

**A Python-based AUTOSAR ECU Configuration Tool**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-54%20passed-success.svg)](./tests/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

## Overview

ECUC Configurator là một công cụ Python mạnh mẽ để đọc, xử lý và generate cấu hình AUTOSAR ECU. Hỗ trợ:

- **CAN Network** - Load từ DBC files
- **LIN Network** - Load từ LDF files  
- **ECUC Generation** - Generate AUTOSAR configuration values
- **ARXML Export** - Export sang AUTOSAR XML format
- **AR4.2.2 & AR4.5** - Support cả 2 phiên bản AUTOSAR

## Features

### Core Capabilities

- **Network Loaders**
  - DBC (CAN Database) file parser
  - LDF (LIN Description File) parser
  - XLSX (Excel) configuration reader (planned)
  - ARXML (AUTOSAR XML) reader (planned)

- **Data Models**
  - Pydantic-based models với full validation
  - CAN, LIN, ECU, AUTOSAR models
  - Type-safe enums và data types
  - Hierarchical structure support

- **ECUC Service**
  - Load và merge data từ nhiều sources
  - Validate consistency (duplicate IDs, signal boundaries)
  - Generate ECUC configuration values
  - Support BSW modules: CanIf, Can, LinIf, Lin

- **ARXML Generator**
  - Generate AUTOSAR-compliant ARXML files
  - Pretty printing support
  - AR4.2.2 và AR4.5.0 compatible

### Supported BSW Modules

| Module | Description | Status |
|--------|-------------|--------|
| **CanIf** | CAN Interface | Implemented |
| **Can** | CAN Driver | Implemented |
| **LinIf** | LIN Interface | Implemented |
| **Lin** | LIN Driver | Implemented |
| **CanTp** | CAN Transport Protocol | Planned |
| **PduR** | PDU Router | Planned |
| **Com** | Communication Manager | Planned |

## Installation

### Requirements

- Python >= 3.8
- Dependencies listed in `requirements.txt`

### Install from source

```bash
# Clone repository
git clone https://github.com/yourusername/ecuc_configurator.git
cd ecuc_configurator

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

### Example: Generate ECUC from DBC

```python
from autosar.service import ECUCService
from autosar.generator import ECUCGenerator
from autosar.model import AutosarVersion

# 1. Create service
service = ECUCService(autosar_version=AutosarVersion.AR_4_2_2)

# 2. Load network files
service.load_dbc('networks/powertrain.dbc')
service.load_ldf('networks/door.ldf')

# 3. Validate data
service.validate_data()

# 4. Generate ECUC project
project = service.generate_ecuc_project(
    project_name="MyECU",
    ecu_instance="MyECU_Instance_1",
    modules=['CanIf', 'Can', 'LinIf', 'Lin']
)

# 5. Export to ARXML
generator = ECUCGenerator()
generator.generate(project, 'output/MyECU_Config.arxml')

print(f"✓ Generated {len(project.value_collection.modules)} modules")
```

### Example: Programmatic Network Creation

```python
from autosar.model import (
    CANDatabase, CANMessage, CANSignal, ByteOrder
)

# Create CAN network
network = CANDatabase(
    name="BodyCAN",
    short_name="BodyCAN",
    baudrate=500000,
    uuid="body-can-uuid"
)

# Add message
msg = CANMessage(
    name="DoorStatus",
    short_name="DoorStatus",
    message_id=0x200,
    length=8,  # or dlc=8
    uuid="msg-uuid"
)

# Add signals
sig = CANSignal(
    name="DoorLeft",
    short_name="DoorLeft",
    start_bit=0,
    length=8,
    byte_order=ByteOrder.LITTLE_ENDIAN,
    uuid="sig-uuid"
)

msg.signals.append(sig)
network.messages.append(msg)

# Use with service
service.can_networks["BodyCAN"] = network
```

## Project Structure

```
ecuc_configurator/
├── src/
│   └── autosar/
│       ├── model/          # Data models (CAN, LIN, AUTOSAR, ECUC)
│       │   ├── base.py
│       │   ├── types.py
│       │   ├── can_model.py
│       │   ├── lin_model.py
│       │   ├── ecu_model.py
│       │   ├── autosar_model.py
│       │   └── ecuc_model.py
│       ├── loader/         # File loaders
│       │   ├── base_loader.py
│       │   ├── dbc_loader.py
│       │   ├── ldf_loader.py
│       │   └── (xlsx_loader.py - planned)
│       ├── service/        # Business logic
│       │   └── ecuc_service.py
│       └── generator/      # Code generators
│           └── ecuc_generator.py
├── tests/                  # Unit tests
│   ├── test_models.py
│   ├── test_loader_dbc.py
│   ├── test_loader_ldf.py
│   └── test_service_ecuc.py
├── examples/               # Usage examples
│   └── generate_ecuc.py
├── doc/                    # Documentation
└── README.md
```

## Documentation

- [Model Documentation](./src/autosar/model/README.md) - Data models guide
- [Loader Documentation](./src/autosar/loader/README.md) - File loaders guide
- [Service Documentation](./src/autosar/service/README.md) - Service layer guide
- [Copilot Instructions](./.github/copilot-instructions.md) - Development guide
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Project status

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/autosar --cov-report=html

# Run specific test file
pytest tests/test_service_ecuc.py -v

# Run specific test
pytest tests/test_service_ecuc.py::TestECUCService::test_service_initialization -v
```

**Current Test Status:**
```
Tests: 54 passed (100%)
Coverage: Models, Loaders, Service
```

## Examples

Run the complete example:

```bash
python examples/generate_ecuc.py
```

This will:
1. Create CAN and LIN networks
2. Validate the data
3. Generate ECUC configuration
4. Export to ARXML files
5. Display preview

Output files created in `examples/output/`:
- `BodyECU_Config.arxml` (AR4.2.2)
- `PowertrainECU_AR45.arxml` (AR4.5.0)

## Architecture

### Data Flow

```
DBC File ──┐
           ├─→ Loaders ─→ Data Models ─→ ECUC Service ─→ ECUC Models ─→ Generator ─→ ARXML
LDF File ──┘
```

### Key Components

1. **Models** - Pydantic-based data structures
   - Type validation
   - Field constraints
   - Helper methods

2. **Loaders** - Parse input files
   - DBC parser (using cantools)
   - LDF parser (regex-based)
   - Base loader with caching

3. **Service** - Business logic
   - Data validation
   - Merging multiple sources
   - ECUC generation

4. **Generator** - Output generation
   - ARXML format
   - Pretty printing
   - Version-specific schemas

## API Reference

### ECUCService

```python
service = ECUCService(autosar_version=AutosarVersion.AR_4_2_2)

# Load data
service.load_dbc(file_path: str, network_name: Optional[str] = None)
service.load_ldf(file_path: str, network_name: Optional[str] = None)

# Validate
service.validate_data() -> bool

# Generate
service.generate_ecuc_project(
    project_name: str,
    ecu_instance: str,
    modules: Optional[List[str]] = None
) -> ECUCProject

# Utilities
service.get_summary() -> Dict[str, Any]
service.clear()
```

### ECUCGenerator

```python
generator = ECUCGenerator()

# Generate to file
generator.generate(
    project: ECUCProject,
    output_path: str,
    pretty_print: bool = True
)

# Generate to string
arxml_str = generator.generate_to_string(
    project: ECUCProject,
    pretty_print: bool = True
)
```

## Development

### Code Style

- Follow PEP 8
- Use type hints
- Max line length: 88 characters (Black formatter)
- Docstrings: Google style

### Adding a New Module

1. Define models in `src/autosar/model/`
2. Add loader if needed in `src/autosar/loader/`
3. Implement generation logic in service
4. Add tests in `tests/`
5. Update documentation

### Running Tests Locally

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with coverage
pytest --cov=src/autosar --cov-report=term-missing

# Run linting
flake8 src/ tests/
mypy src/
```

## Roadmap

### Phase 1: Core (Complete)
- [x] Data models (CAN, LIN, ECUC)
- [x] DBC loader
- [x] LDF loader
- [x] ECUC service
- [x] ARXML generator
- [x] Basic BSW modules (CanIf, Can, LinIf, Lin)

### Phase 2: Extended Loaders (In Progress)
- [ ] XLSX loader for ECU configuration
- [ ] ARXML loader for importing configurations
- [ ] Support more DBC features

### Phase 3: Advanced Features (Planned)
- [ ] More BSW modules (CanTp, PduR, Com, ComM)
- [ ] Signal routing configuration
- [ ] Multi-ECU configuration
- [ ] Configuration validation rules
- [ ] Conflict resolution

### Phase 4: Tools (Planned)
- [ ] CLI tool
- [ ] GUI application
- [ ] Configuration diff/merge
- [ ] Report generation

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## References

- [AUTOSAR Standard](https://www.autosar.org/)
- [DBC File Format](https://www.csselectronics.com/pages/can-dbc-file-database-intro)
- [LDF Specification](https://www.lin-cia.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Acknowledgments

- cantools library for DBC parsing
- AUTOSAR consortium for specifications
- Python community for excellent tools

## Support

For questions, issues, or feature requests:
- Email: your.email@example.com
- Issues: [GitHub Issues](https://github.com/yourusername/ecuc_configurator/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/ecuc_configurator/discussions)

---

**Status**: Production Ready

**Last Updated**: December 15, 2025

**Version**: 0.1.0
