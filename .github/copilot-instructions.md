# GitHub Copilot Instructions - ECUC Configurator Project

## Project Overview

Đây là dự án **AUTOSAR ECUC Configurator** - một công cụ Python để đọc, xử lý và generate cấu hình AUTOSAR ECU, bao gồm:
- CAN/LIN network definitions (DBC, LDF files)
- AUTOSAR XML configurations (ARXML files)
- Excel-based ECU configurations (XLSX files)

## Project Structure

```
ecuc_configurator/
├── src/autosar/
│   ├── model/          # Data models (CAN, LIN, AUTOSAR, ECU)
│   ├── loader/         # File loaders (DBC, LDF, ARXML, XLSX)
│   ├── generator/      # Code generators
│   └── service/        # Business logic services
├── tests/              # Unit tests
├── examples/           # Example files and usage
└── doc/               # Documentation
```

## Coding Standards & Best Practices

### 1. Python Style Guide
- **Python version**: >= 3.8
- **Style**: Follow PEP 8
- **Type hints**: ALWAYS use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings for all classes and functions
- **Line length**: Max 88 characters (Black formatter)

### 2. Data Models (Pydantic)
- **Framework**: Use Pydantic v2 for all data models
- **Validation**: Add field validators using `@field_validator`
- **Base classes**: Always inherit from appropriate base class:
  - `BaseElement` - Basic elements with name, description, uuid
  - `Identifiable` - AUTOSAR identifiable elements with short_name
  - `Referenceable` - Elements that can be referenced

**Example:**
```python
from pydantic import Field, field_validator
from .base import Identifiable

class MyModel(Identifiable):
    """Model description."""
    
    value: int = Field(..., ge=0, le=100, description="Value range 0-100")
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: int) -> int:
        """Custom validation logic."""
        if v % 2 != 0:
            raise ValueError("Value must be even")
        return v
```

### 3. File Loaders
- **Pattern**: Implement abstract base class `BaseLoader`
- **Methods required**:
  - `load(file_path: str)` - Load and parse file
  - `validate(data)` - Validate parsed data
  - `to_model(data)` - Convert to model objects
- **Error handling**: Use custom exceptions from `loader.exceptions`
- **Logging**: Add logging for debug information

**Template:**
```python
from .base_loader import BaseLoader
from ..model import MyModel

class MyFileLoader(BaseLoader):
    """Loader for MY file format."""
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load file and return raw data."""
        self._validate_file_exists(file_path)
        # Implementation
        
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data structure."""
        # Implementation
        
    def to_model(self, data: Dict[str, Any]) -> List[MyModel]:
        """Convert to model objects."""
        # Implementation
```

## Common Errors and Solutions

### Error 1: Pydantic Validation Error
**Problem**: `ValidationError: X validation errors for ModelName`

**Solutions**:
- Check all required fields are provided (marked with `...`)
- Verify field types match declaration
- Check field constraints (ge, le, min_length, etc.)
- Use `model_validate()` instead of direct instantiation for complex objects

**Example Fix:**
```python
# ❌ Wrong
signal = CANSignal(name="Test", start_bit=0)  # Missing required 'length'

# ✅ Correct
signal = CANSignal(name="Test", short_name="Test", start_bit=0, length=16)
```

### Error 2: Module Import Error
**Problem**: `ModuleNotFoundError: No module named 'autosar'`

**Solutions**:
- Install package in development mode: `pip install -e .`
- Ensure all `__init__.py` files exist in package directories
- Check Python path includes `src/` directory
- Verify imports use relative imports within package: `from .base import BaseElement`

### Error 3: Field Validator Issues (Pydantic v2)
**Problem**: Validator not being called or incorrect signature

**Solutions**:
- Use `@field_validator('field_name')` decorator (Pydantic v2 syntax)
- Make validator a `@classmethod`
- Access other field values via `info.data.get('field_name')`
- For model-level validation, use `@model_validator(mode='after')`

**Example:**
```python
from pydantic import field_validator, model_validator

class MyModel(BaseModel):
    value1: int
    value2: int
    
    @field_validator('value1')
    @classmethod
    def check_value1(cls, v: int) -> int:
        """Validate single field."""
        if v < 0:
            raise ValueError("Must be positive")
        return v
    
    @model_validator(mode='after')
    def check_values_together(self):
        """Validate multiple fields together."""
        if self.value1 > self.value2:
            raise ValueError("value1 must be <= value2")
        return self
```

### Error 4: Type Hints and Optional
**Problem**: Type hint errors with Optional fields

**Solution**:
- Use `Optional[Type]` for nullable fields
- Always provide default value (None or Field(None))
- For lists, use `Field(default_factory=list)` not `= []`

**Example:**
```python
from typing import Optional, List
from pydantic import Field

class MyModel(BaseModel):
    # ✅ Correct
    name: str = Field(..., description="Required field")
    optional_value: Optional[int] = Field(None, description="Optional")
    items: List[str] = Field(default_factory=list)
    
    # ❌ Wrong
    # items: List[str] = []  # Mutable default!
```

### Error 5: File Path Issues on Windows
**Problem**: Path separator issues `\` vs `/`

**Solutions**:
- Use `pathlib.Path` for path operations
- Convert to string only when needed
- Use `Path.resolve()` for absolute paths

**Example:**
```python
from pathlib import Path

def load_file(file_path: str) -> Data:
    """Load file from path."""
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    with path.open('r', encoding='utf-8') as f:
        data = f.read()
    return parse(data)
```

## Testing Guidelines

### Test Structure
```python
import pytest
from autosar.model import MyModel

class TestMyModel:
    """Test suite for MyModel."""
    
    def test_creation_success(self):
        """Test successful model creation."""
        model = MyModel(name="Test", value=42)
        assert model.name == "Test"
        assert model.value == 42
    
    def test_validation_error(self):
        """Test validation catches invalid data."""
        with pytest.raises(ValueError):
            MyModel(name="Test", value=-1)  # Invalid value
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/autosar --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_models.py::TestCANModels::test_signal_creation -v
```

## Dependencies Management

### Core Dependencies
- `pydantic>=2.0.0` - Data validation and modeling
- `typing-extensions>=4.5.0` - Extended type hints
- `cantools>=39.0.0` - DBC file parsing
- `openpyxl>=3.1.0` - Excel file handling
- `lxml>=4.9.0` - XML parsing (ARXML)

### Installing Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Architecture Patterns

### 1. Loader Pattern
```
File Input → Loader.load() → Raw Data → Loader.validate() 
→ Validated Data → Loader.to_model() → Model Objects
```

### 2. Model Hierarchy
```
BaseElement (basic fields)
    ↓
Identifiable (AUTOSAR naming)
    ↓
Referenceable (reference support)
    ↓
Specific Models (CANMessage, LINFrame, etc.)
```

### 3. Service Layer
- Business logic separate from models
- Services use loaders to get models
- Services perform transformations and validations
- Services generate output files

## Git Commit Messages

Follow conventional commits format:
```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(model): add CAN signal value table support

fix(loader): handle empty DBC files gracefully

docs(readme): update installation instructions

test(model): add validation tests for LIN frames
```

## Code Generation Guidelines

### When generating new models:
1. ✅ Inherit from appropriate base class
2. ✅ Add docstrings (class and important methods)
3. ✅ Use type hints everywhere
4. ✅ Add field descriptions in Field()
5. ✅ Add validators for business logic
6. ✅ Implement helper methods (get_by_name, etc.)

### When generating loaders:
1. ✅ Inherit from BaseLoader
2. ✅ Implement all abstract methods
3. ✅ Add error handling with custom exceptions
4. ✅ Add logging for debugging
5. ✅ Write corresponding tests

### When generating tests:
1. ✅ Group tests in classes by functionality
2. ✅ Test both success and failure cases
3. ✅ Use descriptive test names
4. ✅ Test edge cases and boundary conditions
5. ✅ Mock external dependencies

## Performance Considerations

- Use generators for large file processing
- Cache parsed results when loading multiple times
- Use `__slots__` for memory-critical classes
- Profile code with `cProfile` if performance issues arise

## Documentation

- Keep README.md files in each major folder
- Document all public APIs
- Provide usage examples
- Update CHANGELOG.md for releases

## Contact & References

- AUTOSAR Standard: https://www.autosar.org/
- DBC Format: https://www.csselectronics.com/pages/can-dbc-file-database-intro
- Pydantic Docs: https://docs.pydantic.dev/
- Project Repository: [Add your repo URL]

---

**Last Updated**: December 15, 2025

**Note**: This file should be updated whenever new patterns, common errors, or best practices are discovered during development.
