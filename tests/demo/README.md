# Demo Scripts

Thư mục này chứa các **demo scripts** để minh họa cách sử dụng ECUC Configurator.

## 📁 Danh sách Demo Scripts

### 1. `demo_complete_xlsx.py`
**Mục đích**: Demo sử dụng Complete XLSX Loader để load **TẤT CẢ** thông tin từ Excel files

**Chức năng**:
- Load complete Excel database (ALL 47 fields per signal)
- Truy cập bidirectional column mappings
- Validate data integrity
- Export complete data

**Usage**:
```bash
python tests/demo/demo_complete_xlsx.py
```

**Input**: `examples/data/xlsx/CAN_ECM_FD3.xlsx`

---

### 2. `demo_load_xlsx.py`
**Mục đích**: Demo basic XLSX loading (legacy loader - chỉ load basic fields)

**Chức năng**:
- Load basic Excel data
- Parse RX/TX sheets
- Convert to basic models

**Usage**:
```bash
python tests/demo/demo_load_xlsx.py
```

**Input**: `examples/data/xlsx/*.xlsx`

---

### 3. `demo_xlsx_models.py`
**Mục đích**: Demo các XLSX models và validation

**Chức năng**:
- Tạo và validate CompleteXLSXSignal
- Tạo và validate CompleteXLSXMessage
- Tạo CompleteXLSXDatabase
- Test field validators

**Usage**:
```bash
python tests/demo/demo_xlsx_models.py
```

---

### 4. `demo_ecuc_generation.py`
**Mục đích**: Demo generate AUTOSAR ECUC configuration từ nhiều nguồn

**Chức năng**:
- Load DBC files
- Load LDF files
- Load XLSX files
- Generate ECUC ARXML output

**Usage**:
```bash
python tests/demo/demo_ecuc_generation.py
```

**Input**: 
- `examples/data/dbc/*.dbc`
- `examples/data/ldf/*.ldf`
- `examples/data/xlsx/*.xlsx`

**Output**: Generated ECUC configuration files

---

## 🎯 Khi nào dùng Demo Scripts?

### ✅ Dùng demo scripts khi:
- Bạn muốn xem cách sử dụng library
- Bạn muốn test nhanh với data thật
- Bạn muốn hiểu workflow của loader
- Bạn muốn prototype tính năng mới

### ❌ KHÔNG dùng demo scripts khi:
- Bạn muốn run automated tests → Dùng `pytest tests/`
- Bạn muốn validate code quality → Dùng unit/integration tests
- Bạn cần CI/CD testing → Dùng test suite

---

## 📊 So sánh: Demo vs Tests

| Khía cạnh | Demo Scripts | Test Scripts |
|-----------|-------------|--------------|
| **Mục đích** | Minh họa usage | Validate correctness |
| **Output** | Print to console | Pass/Fail assertions |
| **Data** | Real example files | Mock + Real data |
| **Run method** | `python tests/demo/xxx.py` | `pytest tests/` |
| **Coverage** | Selected scenarios | Comprehensive coverage |

---

## 🚀 Quick Start

### Run tất cả demo scripts:
```bash
# Demo 1: Complete XLSX Loader
python tests/demo/demo_complete_xlsx.py

# Demo 2: Basic XLSX Loader (legacy)
python tests/demo/demo_load_xlsx.py

# Demo 3: XLSX Models
python tests/demo/demo_xlsx_models.py

# Demo 4: ECUC Generation
python tests/demo/demo_ecuc_generation.py
```

### Run từng demo với data cụ thể:
```bash
# Modify demo script để point to specific data file
# Example: Edit demo_complete_xlsx.py
# Change: file_path = "examples/data/xlsx/CAN_ECM_FD14.xlsx"
```

---

## 📝 Notes

- **Demo scripts không phải là tests** - Chúng chỉ minh họa cách sử dụng
- **Demo scripts có thể fail** nếu data files không tồn tại
- **Để chạy tests thật**, dùng: `pytest tests/unit/ tests/integration/ tests/scenario/`
- **Example data** nằm ở: `examples/data/`

---

## 🔗 Related

- **Test Suite**: `tests/unit/`, `tests/integration/`, `tests/scenario/`
- **Example Data**: `examples/data/`
- **Main Documentation**: `README.md`
- **Test Documentation**: `tests/README.md`

---

**Last Updated**: December 17, 2025
