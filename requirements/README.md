# 📦 Clisonix Dependency Management

## Isolation Strategy

Dependencies are **strictly isolated** to prevent conflicts:

...
requirements/
├── base.txt           # Core Python (no heavy deps)
├── api.txt            # FastAPI + web services
├── ocean.txt          # Ocean AI engine (lightweight)
├── excel.txt          # Excel/Office processing (ISOLATED)
├── ml.txt             # Machine Learning (ISOLATED)
└── dev.txt            # Development only
...

## ⚠️ CRITICAL RULES

### 1. Excel Dependencies (ISOLATED)

```bash
# Install in SEPARATE venv or container
pip install -r requirements/excel.txt
```

- **openpyxl, python-pptx, XlsxWriter** - Office files
- **Pillow** - Image processing
- Never mix with ML dependencies!

### 2. Ocean Core (LIGHTWEIGHT)

```bash
pip install -r requirements/ocean.txt
```

- NO pandas, NO numpy in core
- Uses DuckDB for data
- Binary encoding only (msgpack, cbor2, orjson)

### 3. API Services (STANDARD)

```bash
pip install -r requirements/api.txt
```

- FastAPI, Pydantic, SQLAlchemy
- pandas/numpy for data processing

### 4. ML Dependencies (ISOLATED)

```bash
# Install in SEPARATE venv or container  
pip install -r requirements/ml.txt
```

- torch, transformers, scikit-learn
- Heavy GPU/CPU requirements

## 🔧 Installation Patterns

### Development (Full Stack)

```bash
pip install -r requirements/dev.txt
```

### Production API

```bash
pip install -r requirements/api.txt
```

### Production Ocean

```bash
pip install -r requirements/ocean.txt
```

### Excel Worker (Separate Container)

```bash
docker run clisonix-excel:latest
# Uses requirements/excel.txt internally
```

## 🐳 Docker Isolation

```yaml
# docker-compose.yml
services:
  api:
    build:
      args:
        REQUIREMENTS: requirements/api.txt
        
  ocean:
    build:
      args:
        REQUIREMENTS: requirements/ocean.txt
        
  excel-worker:
    build:
      args:
        REQUIREMENTS: requirements/excel.txt
```

## 📋 Dependency Matrix

| Package  | api | ocean | excel | ml  |
| -------- | --- | ----- | ----- | --- |
| fastapi  | ✅  | ✅    | ❌    | ❌  |
| pandas   | ✅  | ❌    | ❌    | ✅  |
| numpy    | ✅  | ❌    | ❌    | ✅  |
| openpyxl | ❌  | ❌    | ✅    | ❌  |
| torch    | ❌  | ❌    | ❌    | ✅  |
| duckdb   | ❌  | ✅    | ❌    | ❌  |
