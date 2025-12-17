# Legacy Tests

Thư mục này chứa các **legacy test files** từ initial development phase.

## ⚠️ Status: LEGACY / DEPRECATED

Các test files này đã được **thay thế** bởi test suite mới (organized tests) nhưng được giữ lại để:
- Reference historical implementation
- Compare old vs new approaches
- Preserve test coverage during migration

---

## 📁 Legacy Test Files

### 1. `test_loader_dbc.py` (5.6 KB)
**Status**: ⚠️ Legacy - Consider migrating to `tests/unit/`

**Coverage**:
- Basic DBC loader tests
- DBC file parsing validation

**Migration Status**: Should be reviewed and migrated

---

### 2. `test_loader_ldf.py` (7.4 KB)
**Status**: ⚠️ Legacy - Consider migrating to `tests/unit/`

**Coverage**:
- Basic LDF loader tests
- LDF file parsing validation

**Migration Status**: Should be reviewed and migrated

---

### 3. `test_loader_xlsx.py` (9.9 KB)
**Status**: ⚠️ Legacy - **REPLACED** by `tests/integration/test_complete_xlsx_loader.py`

**Coverage**:
- OLD: Basic XLSX loader (partial fields)
- NEW: Complete XLSX loader (ALL 47 fields)

**Migration Status**: ✅ Replaced - Can be archived

---

### 4. `test_models.py` (9.4 KB)
**Status**: ⚠️ Legacy - **REPLACED** by `tests/unit/test_complete_xlsx_models.py`

**Coverage**:
- OLD: Basic CAN/LIN models
- NEW: Complete XLSX models with validation

**Migration Status**: ✅ Replaced - Can be archived

---

### 5. `test_service_ecuc.py` (12 KB)
**Status**: ⚠️ Legacy - Consider migrating to `tests/scenario/`

**Coverage**:
- ECUC service layer tests
- Configuration generation tests

**Migration Status**: Should be reviewed and migrated

---

### 6. `test_xlsx_models.py`
**Status**: ⚠️ Legacy - **REPLACED** by `tests/unit/test_complete_xlsx_models.py`

**Coverage**:
- OLD: Basic XLSX models (partial fields)
- NEW: Complete XLSX models (ALL 47 fields)

**Migration Status**: ✅ Replaced - Can be archived

---

## 🔄 Migration Status

| Legacy Test | New Test Location | Status | Action Needed |
|-------------|-------------------|--------|---------------|
| `test_loader_dbc.py` | N/A | ⚠️ Pending | Review & migrate |
| `test_loader_ldf.py` | N/A | ⚠️ Pending | Review & migrate |
| `test_loader_xlsx.py` | `tests/integration/test_complete_xlsx_loader.py` | ✅ Replaced | Can archive |
| `test_models.py` | `tests/unit/test_complete_xlsx_models.py` | ✅ Replaced | Can archive |
| `test_service_ecuc.py` | N/A | ⚠️ Pending | Review & migrate |
| `test_xlsx_models.py` | `tests/unit/test_complete_xlsx_models.py` | ✅ Replaced | Can archive |

---

## ⚠️ DO NOT USE for CI/CD

**Legacy tests should NOT be run in CI/CD pipelines!**

Reasons:
- May contain outdated assertions
- May test deprecated functionality
- May conflict with new implementation
- Not maintained/updated

---

## ✅ Use New Test Suite Instead

### For Unit Tests:
```bash
pytest tests/unit/test_complete_xlsx_models.py
pytest tests/unit/test_column_mappings.py
```

### For Integration Tests:
```bash
pytest tests/integration/test_complete_xlsx_loader.py
```

### For Scenario Tests:
```bash
pytest tests/scenario/test_autosar_config_generation.py
pytest tests/scenario/test_data_validation_qa.py
```

### For All Tests:
```bash
pytest tests/unit/ tests/integration/ tests/scenario/
```

---

## 🗑️ Future Actions

### Option 1: Archive (Recommended)
```bash
# Create archive folder
mkdir -p archive/legacy_tests

# Move legacy tests to archive
mv tests/unit/legacy/* archive/legacy_tests/

# Update .gitignore to exclude archive
echo "archive/" >> .gitignore
```

### Option 2: Delete (If confident)
```bash
# Delete legacy tests after confirming new tests have equivalent coverage
rm -rf tests/unit/legacy/
```

### Option 3: Keep (Current approach)
- Keep in `tests/unit/legacy/` for reference
- Do NOT run in CI/CD
- Review periodically for migration opportunities

---

## 📊 Test Coverage Comparison

| Aspect | Legacy Tests | New Test Suite |
|--------|-------------|----------------|
| **Test count** | ~40 tests | 81 tests |
| **Coverage** | Basic features | Comprehensive |
| **Organization** | Flat | 3-level hierarchy |
| **Data completeness** | Partial fields | ALL 47 fields |
| **Validation** | Basic | Advanced validators |
| **Maintenance** | ⚠️ Not maintained | ✅ Active |

---

## 🔗 References

- **New Test Suite**: `tests/unit/`, `tests/integration/`, `tests/scenario/`
- **Test Documentation**: `tests/README.md`
- **Implementation Summary**: `tests/IMPLEMENTATION_COMPLETE.md`

---

**Last Updated**: December 17, 2025  
**Status**: Legacy - For reference only
