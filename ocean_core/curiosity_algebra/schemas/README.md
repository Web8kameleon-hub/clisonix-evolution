# Curiosity Algebra Binary Schemas

## Overview

Clisonix Binary Schema (`.clsn`) files define the binary wire format for Curiosity Algebra operations. These schemas enable efficient binary communication between services.

## Schema Files

| File | Magic | Type ID | Description |
|------|-------|---------|-------------|
| `algebra.clsn` | BALG | 0x30 | Binary algebra operations (AND, OR, XOR, etc.) |
| `matrix.clsn` | BMAT | 0x31 | Binary matrix operations |
| `binary_signal.clsn` | BSIG | 0x32 | Binary signal processing |
| `batch.clsn` | BBAT | 0x33 | Batch operations |
| `calculate.clsn` | CLSN | 0x01 | General calculation responses |
| `signal.clsn` | CLSN | 0x10 | Signal frames (metrics, events, alarms) |
| `chat.clsn` | CLSN | 0x20 | Chat message frames |
| `stream.clsn` | CLSN | 0x21 | Streaming data frames |
| `time.clsn` | CLSN | 0x02 | Time-series data |

## Operation Codes

### Algebra Operations (BALG)
```
0x00 AND    0x04 NAND   0x08 SHR    0x0C SUB
0x01 OR     0x05 NOR    0x09 ROL    0x0D MUL
0x02 XOR    0x06 XNOR   0x0A ROR    0x0E DIV
0x03 NOT    0x07 SHL    0x0B ADD    0x0F MOD
```

### Matrix Operations (BMAT)
```
0x00 AND         0x04 MULTIPLY_GF2
0x01 OR          0x05 TRANSPOSE
0x02 XOR         0x06 IDENTITY
0x03 NOT         0x07 INVERSE_GF2
```

### Signal Operations (BSIG)
```
0x00 AND     0x03 NOT       0x06 CONVOLVE
0x01 OR      0x04 SHIFT     0x07 CLOCK
0x02 XOR     0x05 CORRELATE 0x08 PULSE
```

## Binary Format

All schemas follow this structure:

```
┌─────────────────────────────────────────┐
│ HEADER                                  │
├─────────────────────────────────────────┤
│ Magic (4 bytes) + Version (1 byte)      │
│ Timestamp (8 bytes, microseconds)       │
│ Flags/Field Count (varies)              │
├─────────────────────────────────────────┤
│ FIELDS                                  │
├─────────────────────────────────────────┤
│ Data fields as specified in schema      │
├─────────────────────────────────────────┤
│ CHECKSUM                                │
├─────────────────────────────────────────┤
│ CRC32 (4 bytes)                         │
└─────────────────────────────────────────┘
```

## Usage with Python

```python
from curiosity_algebra.binary_algebra import get_binary_algebra, BinaryOp

# Get engine
engine = get_binary_algebra()

# Perform operation
result = engine.operate(0xFF, BinaryOp.AND, 0x0F, bits=8)
print(result.binary)  # "00001111"
print(result.hex)     # "0f"

# Create binary packet
packet = engine.create_packet({
    "operation": "and",
    "operand_a": 0xFF,
    "operand_b": 0x0F,
    "result": 0x0F
})
```

## Schema Version History

| Schema | Version | Date | Changes |
|--------|---------|------|---------|
| algebra.clsn | 2.0 | 2026-02-23 | Added flags, hex_result, carry, overflow, error handling |
| matrix.clsn | 1.0 | 2026-02-23 | Initial release |
| binary_signal.clsn | 1.0 | 2026-02-23 | Initial release |
| batch.clsn | 1.0 | 2026-02-23 | Initial release |
