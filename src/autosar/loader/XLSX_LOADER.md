# XLSX Loader

XLSX Loader cho phép đọc file Excel chứa cấu hình CAN message và signal.

## Tính năng

- ✅ Đọc file Excel (.xlsx) với định dạng customer
- ✅ Hỗ trợ sheet Rx (Receive messages)
- ✅ Hỗ trợ sheet Tx (Transmit messages)
- ✅ Tự động phát hiện Extended CAN Frame (29-bit ID)
- ✅ Parse các format Message ID: `5B0h`, `0x5B0`, hex, decimal
- ✅ Convert sang CANDatabase model (Pydantic)
- ✅ Validation đầy đủ

## Cấu trúc File Excel

### Sheet Rx (Receive Messages)

| Column | Name | Description |
|--------|------|-------------|
| A | CAN Message Name | Tên message |
| B | CAN Message ID | ID (hex với suffix 'h' hoặc '0x') |
| C | CAN Signal Name | Tên signal |
| D | Legacy RX SRD Name | Tên legacy (optional) |
| E | Legacy Implementation name | Tên impl legacy (optional) |
| F | Signal size [in bits] | Độ dài signal (bits) |
| G | Units | Đơn vị |
| H | CAN Signal Group Name | Group name |
| I | Signal has SNA? | Yes/No |
| J | Signal Periodicity [ms] | Chu kỳ (ms) |

### Sheet Tx (Transmit Messages)

| Column | Name | Description |
|--------|------|-------------|
| A | CAN Message Name | Tên message |
| B | CAN Message ID | ID (hex với suffix 'h' hoặc '0x') |
| C | CAN Signal Name | Tên signal |
| D | CAN Signal Group Name | Group name |
| E | Signal Size [in bits] | Độ dài signal (bits) |
| F | Units | Đơn vị |
| G | Signal has SNA? | Yes/No |
| H | Signal Periodicity [ms] | Chu kỳ (ms) |
| I | DBC Comment | Comment |
| J | Notes | Ghi chú |

**Lưu ý:**
- Dòng 1: Title
- Dòng 2: Header
- Dòng 3+: Data
- Merged cells cho message name được xử lý tự động

## Cách sử dụng

### 1. Basic Usage

```python
from autosar.loader import XLSXLoader

# Tạo loader
loader = XLSXLoader()

# Load file
data = loader.load('path/to/file.xlsx')

# Validate
loader.validate(data)

# Convert sang model
database = loader.to_model(data)

# Sử dụng
print(f"Database: {database.name}")
print(f"Messages: {len(database.messages)}")
for msg in database.messages:
    print(f"  - {msg.name} (0x{msg.message_id:03X})")
```

### 2. Xử lý Rx/Tx riêng biệt

```python
loader = XLSXLoader()
data = loader.load('CAN_ECM_FD3.xlsx')

# Lấy Rx messages
rx_messages = [m for m in data['messages'] if m.get('direction') == 'rx']
print(f"RX Messages: {len(rx_messages)}")

# Lấy Tx messages
tx_messages = [m for m in data['messages'] if m.get('direction') == 'tx']
print(f"TX Messages: {len(tx_messages)}")
```

### 3. Xử lý Extended Frame

```python
loader = XLSXLoader()
data = loader.load('CAN_ECM_FD3.xlsx')

# Lọc extended frames (ID > 0x7FF)
extended = [m for m in data['messages'] if m['is_extended']]
print(f"Extended frames: {len(extended)}")

for msg in extended:
    print(f"  {msg['name']}: 0x{msg['message_id']:08X}")
```

## Message ID Formats

Loader hỗ trợ nhiều format Message ID:

| Format | Example | Decimal Value |
|--------|---------|---------------|
| Hex với 'h' | `5B0h` | 1456 |
| Hex với '0x' | `0x5B0` | 1456 |
| Plain hex | `5B0` | 1456 |
| Integer | `1456` | 1456 |
| Extended | `1E394F10h` | 507072272 |

## Extended Frame Detection

- **Standard Frame**: ID ≤ 0x7FF (11-bit)
- **Extended Frame**: ID > 0x7FF (29-bit)

Loader tự động detect based on ID value.

## Data Structure

### Loaded Data Dictionary

```python
{
    'version': '1.0',
    'messages': [
        {
            'name': 'ADAS_FD_HMI',
            'message_id': 0x5B0,
            'is_extended': False,
            'dlc': 8,
            'cycle_time': 100,
            'senders': [],  # Rx
            'comment': 'RX Message from XLSX',
            'signals': [...],
            'direction': 'rx',
        },
        ...
    ],
    'nodes': ['ECU'],
    'file_path': '/path/to/file.xlsx',
    'rx_count': 67,
    'tx_count': 18,
}
```

### Signal Data

```python
{
    'name': 'CRC_ADAS_FD_HMI',
    'start_bit': 0,  # Default, needs calculation
    'length': 8,
    'byte_order': ByteOrder.LITTLE_ENDIAN,
    'value_type': ValueType.UNSIGNED,
    'signal_type': SignalType.STANDARD,
    'factor': 1.0,
    'offset': 0.0,
    'minimum': 0.0,
    'maximum': 0.0,
    'unit': '-',
    'receivers': ['ECU'],
    'comment': '',
    'signal_group': '',
    'has_sna': False,
}
```

## Limitations & Notes

### Hiện tại KHÔNG hỗ trợ

- ❌ `start_bit` - được set về 0, cần tính toán thủ công
- ❌ `byte_order` - mặc định Little Endian
- ❌ `value_type` - mặc định Unsigned
- ❌ `factor`, `offset` - mặc định 1.0, 0.0
- ❌ `min`, `max` - mặc định 0.0
- ❌ Value tables / enumerations

### Sheet names

- Sheet name phải chính xác: `Rx`, `Tx`
- Case-sensitive

### Data Quality

- Message name không được trống
- Signal name không được trống
- Message ID phải valid
- Signal size phải là số nguyên

## Error Handling

```python
from autosar.loader import XLSXLoader
from autosar.loader.base_loader import (
    ParserError,
    ValidationError,
    ConversionError
)

loader = XLSXLoader()

try:
    data = loader.load('file.xlsx')
    loader.validate(data)
    database = loader.to_model(data)
except FileNotFoundError:
    print("File không tồn tại")
except ParserError as e:
    print(f"Lỗi parse file: {e}")
except ValidationError as e:
    print(f"Lỗi validation: {e}")
except ConversionError as e:
    print(f"Lỗi convert model: {e}")
```

## Examples

Xem các file example:
- `examples/load_xlsx_example.py` - Full example với tất cả files
- `examples/test_xlsx_simple.py` - Simple test script
- `tests/test_loader_xlsx.py` - Unit tests

## Testing

```bash
# Run all tests
pytest tests/test_loader_xlsx.py -v

# Run specific test
pytest tests/test_loader_xlsx.py::TestXLSXLoader::test_full_load_flow -v

# Run with output
pytest tests/test_loader_xlsx.py -v -s
```

## Implementation Notes

### Field Order in Pydantic v2

Trong `CANMessage` model, field `is_extended` phải được định nghĩa **TRƯỚC** `message_id` để validator có thể access được giá trị:

```python
class CANMessage(Identifiable):
    is_extended: bool = Field(default=False)  # MUST be first
    message_id: int = Field(...)
    
    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: int, info) -> int:
        is_extended = info.data.get('is_extended', False)  # Can access now
        if not is_extended and v > 0x7FF:
            raise ValueError(...)
        return v
```

### Merged Cells Handling

Excel merged cells được xử lý bằng cách:
1. Khi gặp cell trống cho message name
2. Sử dụng message name của row trước
3. Add signal vào message đó

## Future Enhancements

- [ ] Tính toán `start_bit` từ signal ordering
- [ ] Parse `byte_order` từ comment hoặc convention
- [ ] Parse `factor`, `offset` từ comment
- [ ] Parse min/max từ signal type hoặc comment
- [ ] Hỗ trợ value tables
- [ ] Hỗ trợ custom sheet names
- [ ] Hỗ trợ NewRx, NewTx, ModRx, ModTx sheets
- [ ] Export validation report
- [ ] Signal layout visualization

## License

MIT License - See LICENSE file for details
