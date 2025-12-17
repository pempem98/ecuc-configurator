# Test Suite Documentation

Bộ test suite cho **ECUC Configurator Project** được tổ chức theo cấu trúc chuyên nghiệp:

## 📋 Test Organization

```
tests/
├── unit/                   # Unit Tests - Test từng component riêng lẻ
│   ├── test_complete_xlsx_models.py      # Models (Signal, Message, Database)
│   ├── test_column_mappings.py           # Column mappings (RX/TX)
│   └── legacy/                           # Legacy tests (deprecated)
│       ├── test_loader_dbc.py
│       ├── test_loader_ldf.py
│       ├── test_loader_xlsx.py
│       ├── test_models.py
│       ├── test_service_ecuc.py
│       ├── test_xlsx_models.py
│       └── README.md                     # Legacy test documentation
│
├── integration/            # Integration Tests - Test tích hợp giữa components
│   └── test_complete_xlsx_loader.py      # Loader + Models integration
│
├── scenario/              # Scenario Tests - Test use cases thực tế
│   ├── test_autosar_config_generation.py # AUTOSAR config generation
│   └── test_data_validation_qa.py        # Data validation & QA
│
├── demo/                  # Demo Scripts - Minh họa cách sử dụng
│   ├── demo_complete_xlsx.py             # Demo complete XLSX loader
│   ├── demo_load_xlsx.py                 # Demo basic XLSX loader
│   ├── demo_xlsx_models.py               # Demo XLSX models
│   ├── demo_ecuc_generation.py           # Demo ECUC generation
│   └── README.md                         # Demo documentation
│
├── README.md              # This file - Test suite documentation
└── IMPLEMENTATION_COMPLETE.md            # Implementation summary
```

---

## 🧪 Test Categories

### 1. Unit Tests (`tests/unit/`)

**Mục đích**: Test từng class, method riêng biệt với mock data

**Đặc điểm**:
- ✅ Test isolated components
- ✅ Fast execution (< 1s per test)
- ✅ No external dependencies
- ✅ Mock/fixture data

**Files**:

#### `test_complete_xlsx_models.py` (600+ lines, 34 tests)
Test các model classes:
- **TestCompleteXLSXSignal** (15 tests):
  - Signal creation (minimal, RX, TX)
  - Signal properties (is_rx, is_tx, has_sna, etc.)
  - Legacy name handling
  - Field validation
  
- **TestCompleteXLSXMessage** (10 tests):
  - Message creation and validation
  - Signal management
  - Query methods (get_signal_by_name, get_signals_by_group)
  - Extended frame detection
  
- **TestCompleteXLSXDatabase** (9 tests):
  - Database creation
  - Message management
  - Query methods (get_message_by_id, get_message_by_name)
  - Statistics generation

#### `test_column_mappings.py` (340+ lines, 15 tests)
Test column mapping classes:
- **TestRxColumnMapping** (5 tests):
  - Bidirectional mapping (column ↔ field)
  - All 44 RX columns
  - Sequential indices
  
- **TestTxColumnMapping** (6 tests):
  - Bidirectional mapping
  - All 43 TX columns
  - Sequential indices
  
- **TestColumnMappingConsistency** (4 tests):
  - RX/TX consistency
  - Common fields validation

**Chạy unit tests**:
```bash
# All unit tests
pytest tests/unit/ -v

# Specific file
pytest tests/unit/test_complete_xlsx_models.py -v

# Specific test class
pytest tests/unit/test_complete_xlsx_models.py::TestCompleteXLSXSignal -v

# With coverage
pytest tests/unit/ --cov=src/autosar/model --cov-report=html
```

---

### 2. Integration Tests (`tests/integration/`)

**Mục đích**: Test tích hợp giữa loader, models, và file parsing

**Đặc điểm**:
- ✅ Test component interactions
- ✅ Use real Excel files
- ✅ Medium execution time (1-5s per test)
- ✅ End-to-end data flow

**Files**:

#### `test_complete_xlsx_loader.py` (500+ lines, 30+ tests)
Test loader integration với real data:

- **TestCompleteXLSXLoaderIntegration** (15 tests):
  - Load real Excel file (CAN_ECM_FD3.xlsx)
  - Parse RX/TX messages
  - Validate data structure
  - Convert to models
  - End-to-end workflow
  - Signal field completeness
  - Extended frame detection
  - Signal groups parsing
  - SNA signals detection
  - Legacy names preservation
  - Query operations
  
- **TestCompleteXLSXLoaderErrorHandling** (4 tests):
  - Non-existent file
  - Invalid file extension
  - Invalid data structure
  - Missing required fields
  
- **TestCompleteXLSXLoaderDataIntegrity** (7 tests):
  - Valid message IDs
  - Valid signal sizes
  - Signal/message direction consistency
  - Consumer/producer info
  - Statistics consistency

**Chạy integration tests**:
```bash
# All integration tests
pytest tests/integration/ -v

# With real data validation
pytest tests/integration/ -v --tb=short

# Skip if test files missing
pytest tests/integration/ -v -rs
```

---

### 3. Scenario Tests (`tests/scenario/`)

**Mục đích**: Test use cases thực tế của các teams

**Đặc điểm**:
- ✅ Real-world workflows
- ✅ Cross-functional scenarios
- ✅ Business logic validation
- ✅ Team collaboration scenarios

**Files**:

#### `test_autosar_config_generation.py` (400+ lines, 20+ tests)
Test scenarios cho AUTOSAR configuration:

- **TestAutosarConfigGeneration** (6 scenarios):
  - Extract COM I-PDU config (85 I-PDUs)
  - Extract signal group config (31 groups)
  - Extract invalidation config (SNA values)
  - Extract timeout monitoring (RX messages)
  - Extract BSW layer mapping (data elements)
  - Extract RTE config (ports, interfaces)

- **TestLegacyMigrationScenario** (3 scenarios):
  - Legacy signal name mapping
  - Frame type migration (standard → extended)
  - Signal scaling migration

- **TestTeamCollaborationScenario** (3 scenarios):
  - Generate team status report
  - Identify SWC dependencies
  - Generate signal documentation

#### `test_data_validation_qa.py` (450+ lines, 15+ tests)
Test scenarios cho QA và cross-team integration:

- **TestDataValidationScenario** (5 scenarios):
  - Validate signal boundaries (no overflow)
  - Validate unique message IDs
  - Validate signal naming conventions
  - Validate data consistency (SNA, invalidation)
  - Validate field coverage completeness

- **TestCrossTeamIntegrationScenario** (4 scenarios):
  - COM team requirements (I-PDUs, signal groups)
  - RTE team requirements (ports, interfaces)
  - SWC team requirements (producer/consumer)
  - CanIf team requirements (frame types)

- **TestPerformanceScenario** (2 scenarios):
  - Load large file performance (< 5s for 781 signals)
  - Query performance (< 10ms per lookup)

**Chạy scenario tests**:
```bash
# All scenario tests
pytest tests/scenario/ -v

# Specific scenario
pytest tests/scenario/test_autosar_config_generation.py::TestAutosarConfigGeneration -v

# With performance metrics
pytest tests/scenario/test_data_validation_qa.py::TestPerformanceScenario -v -s
```

---

## 🎯 Test Coverage Goals

| Category | Coverage Goal | Current Status |
|----------|--------------|----------------|
| Models | 90%+ | ✅ ~95% (34 tests) |
| Column Mappings | 100% | ✅ 100% (15 tests) |
| Loader | 85%+ | ✅ ~90% (30+ tests) |
| Integration | 80%+ | ✅ ~85% (30+ tests) |
| Scenarios | N/A | ✅ 20+ scenarios |

---

## 📊 Running All Tests

### Run Everything
```bash
# All tests
pytest -v

# With coverage report
pytest --cov=src/autosar --cov-report=html --cov-report=term

# Parallel execution (faster)
pytest -n auto
```

### Run by Category
```bash
# Only unit tests
pytest tests/unit/ -v

# Only integration tests
pytest tests/integration/ -v

# Only scenario tests
pytest tests/scenario/ -v
```

### Run with Markers (Future)
```bash
# Fast tests only
pytest -m "not slow" -v

# Smoke tests
pytest -m smoke -v
```

---

## 📝 Test Data

### Test Files Required
```
examples/xlsx/
└── CAN_ECM_FD3.xlsx    # Main test file (85 messages, 781 signals)
```

### Known Test Values
From `CAN_ECM_FD3.xlsx`:
- **Messages**: 85 total (67 RX, 18 TX)
- **Signals**: 781 total (411 RX, 370 TX)
- **Extended frames**: 4
- **Signal groups**: 31 unique
- **Signals with SNA**: 292
- **SWC producers**: 9 unique
- **SWC consumers**: 9 unique

---

## 🔧 Test Fixtures

### Common Fixtures
```python
@pytest.fixture
def loader():
    """CompleteXLSXLoader instance."""
    return CompleteXLSXLoader()

@pytest.fixture
def test_file():
    """Path to test Excel file."""
    return str(TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx')

@pytest.fixture
def database(loader, test_file):
    """Loaded database with all data."""
    return loader.load_complete(test_file)
```

---

## 🐛 Debugging Tests

### Run Single Test with Output
```bash
pytest tests/unit/test_complete_xlsx_models.py::TestCompleteXLSXSignal::test_signal_creation_minimal -v -s
```

### Show Print Statements
```bash
pytest -v -s
```

### Stop on First Failure
```bash
pytest -x
```

### Show Local Variables on Failure
```bash
pytest -l
```

### Full Traceback
```bash
pytest --tb=long
```

---

## 📚 Writing New Tests

### Unit Test Template
```python
class TestMyNewComponent:
    """Unit tests for MyNewComponent."""
    
    def test_creation_success(self):
        """Test successful creation."""
        obj = MyComponent(param="value")
        assert obj.param == "value"
    
    def test_validation_error(self):
        """Test validation catches errors."""
        with pytest.raises(ValueError):
            MyComponent(param="invalid")
```

### Integration Test Template
```python
class TestMyIntegration:
    """Integration tests for component interaction."""
    
    @pytest.fixture
    def components(self):
        """Setup integrated components."""
        return ComponentA(), ComponentB()
    
    def test_interaction(self, components):
        """Test components work together."""
        a, b = components
        result = a.process(b.get_data())
        assert result is not None
```

### Scenario Test Template
```python
class TestMyScenario:
    """Scenario test for real-world use case."""
    
    def test_scenario_user_workflow(self):
        """
        Scenario: User completes typical workflow.
        
        Use case: Product Owner needs report.
        Expected: Complete data generated.
        """
        # Arrange
        data = load_real_data()
        
        # Act
        report = generate_report(data)
        
        # Assert
        assert report['completeness'] > 0.95
```

---

---

## 🎯 Demo Scripts vs Tests

### Demo Scripts (`tests/demo/`)
**Purpose**: Minh họa cách sử dụng library cho developers

**Characteristics**:
- ✅ Show real-world usage examples
- ✅ Print output to console
- ✅ Use real data files from `examples/data/`
- ✅ Can be modified for experimentation
- ❌ **NOT** part of test suite (not run by pytest)

**Run Demo Scripts**:
```bash
# Run individual demo
python tests/demo/demo_complete_xlsx.py

# Run all demos
for demo in tests/demo/*.py; do python "$demo"; done
```

**See**: `tests/demo/README.md` for detailed demo documentation

---

### Legacy Tests (`tests/unit/legacy/`)
**Purpose**: Preserve historical test files from initial development

**Status**: ⚠️ **DEPRECATED** - Not maintained

**Characteristics**:
- ⚠️ Old implementation (basic fields only)
- ⚠️ May contain outdated assertions
- ⚠️ Replaced by new organized test suite
- ⚠️ **DO NOT RUN** in CI/CD

**Migration Status**:
- `test_loader_xlsx.py` → ✅ Replaced by `tests/integration/test_complete_xlsx_loader.py`
- `test_models.py` → ✅ Replaced by `tests/unit/test_complete_xlsx_models.py`
- `test_xlsx_models.py` → ✅ Replaced by `tests/unit/test_complete_xlsx_models.py`
- `test_loader_dbc.py` → ⚠️ Pending migration
- `test_loader_ldf.py` → ⚠️ Pending migration
- `test_service_ecuc.py` → ⚠️ Pending migration

**See**: `tests/unit/legacy/README.md` for legacy test documentation

---

## 📖 References

- **pytest docs**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **Project Guidelines**: See `/.github/copilot-instructions.md`
- **Demo Scripts**: See `tests/demo/README.md`
- **Legacy Tests**: See `tests/unit/legacy/README.md`
- **Example Data**: See `examples/README.md`

---

## 🎓 Test Best Practices

1. ✅ **Descriptive Names**: Use clear test method names
2. ✅ **One Assertion Focus**: Test one thing per test
3. ✅ **AAA Pattern**: Arrange, Act, Assert
4. ✅ **Fast Execution**: Keep unit tests < 1s
5. ✅ **Isolated**: No dependencies between tests
6. ✅ **Repeatable**: Same results every run
7. ✅ **Fixtures**: Reuse setup code with fixtures
8. ✅ **Docstrings**: Document test purpose

---

**Last Updated**: December 15, 2025  
**Test Suite Version**: 1.0.0
