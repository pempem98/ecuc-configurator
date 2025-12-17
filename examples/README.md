# Example Data Files

Thư mục này chứa **example data files** để test và demo AUTOSAR ECUC Configurator.

---

## 📁 Directory Structure

```
examples/
└── data/                       # All example data files
    ├── dbc/                    # CAN Database files
    ├── ldf/                    # LIN Description files
    ├── arxml/                  # AUTOSAR XML files
    └── xlsx/                   # Excel configuration files
```

---

## 🗂️ Data Categories

### 1. DBC Files (CAN Database)
**Location**: `examples/data/dbc/`

**Description**: CAN network definition files in DBC format

**Files** (5 files):
```
ECM_PMBD_FD14_2025-34_LB-WL_PRS_Release.dbc
ECM_PMBD_FD16_2025-34_LB-WL_PRS_Release.dbc
ECM_PMBD_FD3_2025-34_LB-WL_PRS_Release_v2.dbc
PLB26_E3A_R2_CCAN12.dbc
S_JL26_JT26_E3A_CCAN_2025-31_PRS_Release_ECM_PMBD_v2.dbc
```

**Usage**:
```python
from autosar.loader import DBCLoader

loader = DBCLoader()
database = loader.load("examples/data/dbc/ECM_PMBD_FD3_2025-34_LB-WL_PRS_Release_v2.dbc")
```

**Content**:
- CAN messages and signals
- Signal value tables
- Message cycle times
- Node definitions
- Comments and descriptions

---

### 2. LDF Files (LIN Description)
**Location**: `examples/data/ldf/`

**Description**: LIN network definition files in LDF format

**Files** (3 files):
```
ECM_GAS_LIN_1b_2329_PT_Release.ldf
HDCC27_E1A_R1_ECM_GAS_DSL_LIN1.ldf
HDCC27_E1A_R2_ECM_GAS_LIN2.ldf
```

**Usage**:
```python
from autosar.loader import LDFLoader

loader = LDFLoader()
network = loader.load("examples/data/ldf/ECM_GAS_LIN_1b_2329_PT_Release.ldf")
```

**Content**:
- LIN frames and signals
- LIN schedules
- Node configurations
- Signal encoding

---

### 3. ARXML Files (AUTOSAR XML)
**Location**: `examples/data/arxml/`

**Description**: AUTOSAR XML configuration files

**Files** (13 files):
```
comscl_ign_rx_grpsig.arxml
comscl_ign_tx_grpsig.arxml
comscl_netmtrx_rx_grpsig.arxml
comscl_netmtrx_rx.arxml
comscl_netmtrx_tx_grpsig.arxml
comscl_netmtrx_tx.arxml
comscl_netmtrx2_rx_grpsig.arxml
comscl_netmtrx2_rx.arxml
comscl_netmtrx2_tx_grpsig.arxml
comscl_netmtrx2_tx.arxml
comscl_netmtrx3_rx_grpsig.arxml
comscl_netmtrx3_tx_grpsig.arxml
comscl_netmtrx3_tx_simple.arxml
```

**Usage**:
```python
from autosar.loader import ARXMLLoader

loader = ARXMLLoader()
config = loader.load("examples/data/arxml/comscl_netmtrx_rx.arxml")
```

**Content**:
- COM signal groups
- RX/TX signal definitions
- Network matrix configurations
- AUTOSAR elements

---

### 4. XLSX Files (Excel Configurations)
**Location**: `examples/data/xlsx/`

**Description**: Excel-based ECU configuration files with **COMPLETE** data (ALL fields)

**Files** (3 files):
```
CAN_ECM_FD14.xlsx
CAN_ECM_FD16.xlsx
CAN_ECM_FD3.xlsx
```

**Usage**:
```python
from autosar.loader import CompleteXLSXLoader

loader = CompleteXLSXLoader()
database = loader.load_complete("examples/data/xlsx/CAN_ECM_FD3.xlsx")

# Access ALL 47 fields per signal
for msg in database.rx_messages:
    for sig in msg.signals:
        print(f"Signal: {sig.signal_name}")
        print(f"  Legacy Names: {sig.legacy_name_1}, {sig.legacy_name_2}, {sig.legacy_name_3}")
        print(f"  Routing: {sig.signal_routing}")
        print(f"  Gateway: {sig.gateway_routing}")
        # ... access all 47 fields
```

**Content**:
- **RX Sheet**: 44 columns (ALL fields captured)
- **TX Sheet**: 43 columns (ALL fields captured)
- **Total**: 47 unique fields per signal
- **Bidirectional column mappings** available

**Excel Structure**:
```
CAN_ECM_FD3.xlsx
├── Sheet "RX"              # RX messages & signals (44 columns)
│   ├── Message ID
│   ├── Message Name
│   ├── Signal Name
│   ├── Legacy Names (1, 2, 3)
│   ├── Signal Routing
│   ├── Gateway Routing
│   └── ... (38 more columns)
└── Sheet "TX"              # TX messages & signals (43 columns)
    ├── Message ID
    ├── Message Name
    ├── Signal Name
    └── ... (40 more columns)
```

---

## 🎯 Usage Scenarios

### Scenario 1: Load Complete XLSX Data
```python
from autosar.loader import CompleteXLSXLoader

# Load ALL 47 fields per signal
loader = CompleteXLSXLoader()
db = loader.load_complete("examples/data/xlsx/CAN_ECM_FD3.xlsx")

print(f"RX Messages: {len(db.rx_messages)}")
print(f"TX Messages: {len(db.tx_messages)}")
print(f"Total Signals: {db.total_signal_count}")

# Access column mappings
rx_mapping = db.get_rx_column_mapping()
print(f"RX Columns: {len(rx_mapping)}")
```

### Scenario 2: Load DBC and Compare with XLSX
```python
from autosar.loader import DBCLoader, CompleteXLSXLoader

# Load DBC
dbc_loader = DBCLoader()
dbc_db = dbc_loader.load("examples/data/dbc/ECM_PMBD_FD3_2025-34_LB-WL_PRS_Release_v2.dbc")

# Load XLSX
xlsx_loader = CompleteXLSXLoader()
xlsx_db = xlsx_loader.load_complete("examples/data/xlsx/CAN_ECM_FD3.xlsx")

# Compare
print(f"DBC Messages: {len(dbc_db.messages)}")
print(f"XLSX Messages: {len(xlsx_db.rx_messages) + len(xlsx_db.tx_messages)}")
```

### Scenario 3: Generate ECUC from Multiple Sources
```python
from autosar.service import ECUCService

service = ECUCService()

# Add DBC files
service.add_dbc("examples/data/dbc/ECM_PMBD_FD3_2025-34_LB-WL_PRS_Release_v2.dbc")

# Add LDF files
service.add_ldf("examples/data/ldf/ECM_GAS_LIN_1b_2329_PT_Release.ldf")

# Add XLSX files (complete data)
service.add_xlsx("examples/data/xlsx/CAN_ECM_FD3.xlsx")

# Generate ECUC
ecuc_config = service.generate_ecuc()
service.save_arxml("output_ecuc.arxml")
```

---

## 📊 Data Statistics

| Type | Count | Total Size | Format |
|------|-------|-----------|--------|
| **DBC** | 5 files | ~500 KB | CAN Database |
| **LDF** | 3 files | ~200 KB | LIN Description |
| **ARXML** | 13 files | ~1.5 MB | AUTOSAR XML |
| **XLSX** | 3 files | ~800 KB | Excel Workbook |
| **Total** | **24 files** | **~3 MB** | Various |

---

## ⚠️ Important Notes

### Excel Files (XLSX):
- ✅ **Complete data capture**: ALL 47 fields per signal
- ✅ **Bidirectional mappings**: Python field ↔ Excel column
- ✅ **RX + TX sheets**: Both directions supported
- ⚠️ **Do NOT edit manually** - Use CompleteXLSXLoader to preserve data integrity
- ⚠️ **Temp files (~$*.xlsx)** are ignored by .gitignore

### DBC Files:
- ✅ **Standard format**: Vector CANdb++ format
- ✅ **Widely compatible**: Works with most CAN tools
- ⚠️ **Encoding**: UTF-8 recommended

### LDF Files:
- ✅ **LIN 2.x format**: Standard LIN description
- ⚠️ **Version specific**: Check LDF version compatibility

### ARXML Files:
- ✅ **AUTOSAR 4.x**: Compatible with AUTOSAR standard
- ⚠️ **Large files**: Some files >100 KB

---

## 🔗 Related

- **Demo Scripts**: `tests/demo/` - How to use these data files
- **Test Suite**: `tests/` - Tests using these data files
- **Loaders**: `src/autosar/loader/` - Code to parse these files
- **Models**: `src/autosar/model/` - Data models for these files

---

## 🚀 Quick Start

### 1. Browse Data
```bash
# List all data files
find examples/data -type f

# Check file sizes
du -h examples/data/*
```

### 2. Run Demos with Data
```bash
# Demo: Complete XLSX loader
python tests/demo/demo_complete_xlsx.py

# Demo: ECUC generation
python tests/demo/demo_ecuc_generation.py
```

### 3. Run Tests with Data
```bash
# Integration test: Load real XLSX file
pytest tests/integration/test_complete_xlsx_loader.py -v

# Scenario test: Data validation
pytest tests/scenario/test_data_validation_qa.py -v
```

---

**Last Updated**: December 17, 2025  
**Total Files**: 24 example data files  
**Purpose**: Testing, demo, and development
