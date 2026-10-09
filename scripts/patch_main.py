#!/usr/bin/env python3
"""
Patch main.py to include Unified Status Layer
"""
import re

# Read main.py
with open('/app/main.py', 'r') as f:
    content = f.read()

# Check if already patched
if 'unified_status_layer' in content:
    print('✅ Already patched - skipping')
    exit(0)

# The patch code to insert after app = FastAPI(...)
patch_code = '''

# =============================================================================
# UNIFIED STATUS LAYER - Solves 3 Critical Problems:
# 1. Rate Limiting (60 req/min per IP)
# 2. Intelligent Caching (10-30s for status endpoints)
# 3. Global Error Handling (404/5xx tracking)
# =============================================================================
try:
    from unified_status_layer import (
        unified_router,
        CachingMiddleware,
        NotFoundMiddleware,
        status_cache,
        error_handler
    )
    
    # Add unified status router (/api/system/health)
    app.include_router(unified_router)
    
    # Add middlewares
    app.add_middleware(NotFoundMiddleware)
    app.add_middleware(CachingMiddleware)
    
    print("[OK] Unified Status Layer initialized - Caching + Error Handling active")
except ImportError as e:
    print(f"[WARN] Unified Status Layer not available: {e}")
    status_cache = None
    error_handler = None

'''

# Find the location after app = FastAPI(...) block
pattern = r'(app = FastAPI\([^)]*\))'
match = re.search(pattern, content, re.DOTALL)
if match:
    insert_pos = match.end()
    # Insert patch after the FastAPI initialization
    new_content = content[:insert_pos] + patch_code + content[insert_pos:]
    
    with open('/app/main.py', 'w') as f:
        f.write(new_content)
    print("✅ main.py patched successfully")
    print(f"   Inserted at position {insert_pos}")
else:
    print("❌ Could not find FastAPI initialization pattern")
    exit(1)
