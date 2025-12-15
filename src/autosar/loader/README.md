# AUTOSAR Loader Module

## Tổng quan

Module **Loader** cung cấp các thành phần Python để đọc và phân tích các định dạng file khác nhau được sử dụng trong ngành công nghiệp ô tô, bao gồm:

- **DBC** (CAN Database) - Định dạng mô tả mạng CAN
- **XLSX** (Excel) - Bảng tính Excel chứa cấu hình
- **ARXML** (AUTOSAR XML) - File cấu hình AUTOSAR
- **LDF** (LIN Description File) - Định dạng mô tả mạng LIN

Các loader sẽ chuyển đổi dữ liệu từ các file này thành các đối tượng model cụ thể được định nghĩa trong module `autosar.model`.

## Kiến trúc

```
loader/
├── README.md           # File tài liệu này
├── __init__.py         # Package initialization
├── base_loader.py      # Abstract base class cho tất cả loader
├── dbc_loader.py       # Loader cho file DBC
├── xlsx_loader.py      # Loader cho file Excel
├── arxml_loader.py     # Loader cho file ARXML
├── ldf_loader.py       # Loader cho file LDF
└── utils/
    ├── __init__.py
    ├── parser_utils.py # Các hàm tiện ích chung
    └── validator.py    # Validate dữ liệu đầu vào
```

## Các thành phần chính

### 1. Base Loader

**File:** `base_loader.py`

Abstract base class định nghĩa interface chung cho tất cả các loader:

```python
class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load và parse file"""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate dữ liệu đã load"""
        pass
    
    @abstractmethod
    def to_model(self, data: Dict[str, Any]) -> List[BaseModel]:
        """Convert sang model objects"""
        pass
```

### 2. DBC Loader

**File:** `dbc_loader.py`

Load và parse file CAN Database (*.dbc):

**Chức năng:**
- Parse CAN messages, signals, nodes
- Xử lý attributes và value tables
- Chuyển đổi sang CANMessage, CANSignal models
- Hỗ trợ encoding/decoding signals

**Ví dụ sử dụng:**
```python
from autosar.loader import DBCLoader

loader = DBCLoader()
messages = loader.load("path/to/file.dbc")
can_database = loader.to_model(messages)
```

### 3. XLSX Loader

**File:** `xlsx_loader.py`

Load và parse file Excel chứa cấu hình:

**Chức năng:**
- Đọc nhiều sheets với cấu trúc khác nhau
- Parse ECU configuration parameters
- Xử lý containers, modules, parameters
- Validate format và data types
- Chuyển đổi sang EcuConfiguration, Container models

**Ví dụ sử dụng:**
```python
from autosar.loader import XLSXLoader

loader = XLSXLoader()
config = loader.load("path/to/config.xlsx")
ecu_config = loader.to_model(config)
```

### 4. ARXML Loader

**File:** `arxml_loader.py`

Load và parse file AUTOSAR XML:

**Chức năng:**
- Parse AUTOSAR XML schema (AR 4.x)
- Xử lý packages, components, interfaces
- Load ECU configuration, SWC descriptions
- Hỗ trợ namespaces và references
- Chuyển đổi sang các AUTOSAR model objects

**Ví dụ sử dụng:**
```python
from autosar.loader import ARXMLLoader

loader = ARXMLLoader(version="4.3.1")
arxml_data = loader.load("path/to/config.arxml")
autosar_model = loader.to_model(arxml_data)
```

### 5. LDF Loader

**File:** `ldf_loader.py`

Load và parse LIN Description File:

**Chức năng:**
- Parse LIN network configuration
- Xử lý master/slave nodes
- Load frames và signals
- Parse schedule tables
- Chuyển đổi sang LINNetwork, LINFrame models

**Ví dụ sử dụng:**
```python
from autosar.loader import LDFLoader

loader = LDFLoader()
lin_config = loader.load("path/to/network.ldf")
lin_network = loader.to_model(lin_config)
```

## Quy trình xử lý chung

```
┌─────────────┐
│  Input File │
│ (DBC/XLSX/  │
│  ARXML/LDF) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Loader    │
│   .load()   │  ← Parse file content
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validator  │
│ .validate() │  ← Validate data structure
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Transform  │
│ .to_model() │  ← Convert to model objects
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Model Objects│
│  (từ model/ │
│   folder)   │
└─────────────┘
```

## Dependencies

```txt
# Core dependencies
python >= 3.8

# File parsing
cantools          # DBC parsing
openpyxl          # Excel parsing
lxml              # XML parsing
ldfparser         # LDF parsing

# Data validation
pydantic          # Data modeling & validation
jsonschema        # Schema validation

# Utilities
typing-extensions
dataclasses
```

## Cài đặt

```bash
pip install -r requirements.txt
```

## Testing

```bash
# Run all loader tests
pytest tests/test_loader/

# Test specific loader
pytest tests/test_loader/test_dbc_loader.py
pytest tests/test_loader/test_xlsx_loader.py
pytest tests/test_loader/test_arxml_loader.py
pytest tests/test_loader/test_ldf_loader.py
```

## Sử dụng

### Ví dụ cơ bản

```python
from autosar.loader import DBCLoader, XLSXLoader, ARXMLLoader, LDFLoader

# Load DBC file
dbc_loader = DBCLoader()
can_db = dbc_loader.load_and_convert("network.dbc")

# Load Excel configuration
xlsx_loader = XLSXLoader()
ecu_config = xlsx_loader.load_and_convert("ecu_config.xlsx")

# Load ARXML
arxml_loader = ARXMLLoader()
autosar_model = arxml_loader.load_and_convert("system.arxml")

# Load LDF
ldf_loader = LDFLoader()
lin_network = ldf_loader.load_and_convert("lin_cluster.ldf")
```

### Ví dụ nâng cao - Custom configuration

```python
from autosar.loader import XLSXLoader
from autosar.loader.utils import LoaderConfig

# Custom configuration
config = LoaderConfig(
    strict_mode=True,
    skip_validation=False,
    encoding="utf-8",
    error_handling="raise"  # or "warn", "ignore"
)

loader = XLSXLoader(config=config)
loader.register_custom_parser("CustomModule", custom_parser_func)
result = loader.load("config.xlsx")
```

## Error Handling

Các loader sẽ raise các exception sau:

- `FileNotFoundError`: File không tồn tại
- `ParserError`: Lỗi khi parse file
- `ValidationError`: Dữ liệu không hợp lệ
- `ConversionError`: Không thể chuyển đổi sang model
- `UnsupportedFormatError`: Format không được hỗ trợ

```python
from autosar.loader import DBCLoader
from autosar.loader.exceptions import ParserError, ValidationError

try:
    loader = DBCLoader()
    result = loader.load("file.dbc")
except FileNotFoundError:
    print("File không tồn tại")
except ParserError as e:
    print(f"Lỗi parse: {e}")
except ValidationError as e:
    print(f"Dữ liệu không hợp lệ: {e}")
```

## Extensibility

Để tạo loader mới cho format khác:

```python
from autosar.loader.base_loader import BaseLoader

class CustomLoader(BaseLoader):
    def load(self, file_path: str):
        # Implement your loading logic
        pass
    
    def validate(self, data):
        # Implement validation
        pass
    
    def to_model(self, data):
        # Convert to model objects
        pass
```

## Best Practices

1. **Validation**: Luôn validate dữ liệu sau khi load
2. **Error Handling**: Sử dụng try-except để xử lý lỗi gracefully
3. **Logging**: Enable logging để debug
4. **Memory**: Xử lý file lớn theo chunks nếu cần
5. **Caching**: Cache kết quả parse nếu load nhiều lần

## Roadmap

- [ ] Implement base loader abstract class
- [ ] DBC Loader implementation
- [ ] XLSX Loader implementation  
- [ ] ARXML Loader implementation
- [ ] LDF Loader implementation
- [ ] Validator utilities
- [ ] Parser utilities
- [ ] Unit tests cho từng loader
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Documentation hoàn chỉnh

## Tham khảo

- [AUTOSAR Standard](https://www.autosar.org/)
- [DBC File Format](https://www.csselectronics.com/pages/can-dbc-file-database-intro)
- [LDF Specification](https://www.lin-cia.org/)
- [cantools Documentation](https://cantools.readthedocs.io/)
- [lxml Documentation](https://lxml.de/)

## Đóng góp

Khi thêm loader mới:

1. Kế thừa từ `BaseLoader`
2. Implement các abstract methods
3. Thêm unit tests
4. Update documentation
5. Thêm ví dụ sử dụng

## License

[Thêm thông tin license ở đây]

---

**Lưu ý:** Đây là tài liệu thiết kế ban đầu. Các chi tiết implementation có thể thay đổi trong quá trình phát triển.
