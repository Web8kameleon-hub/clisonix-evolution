#!/usr/bin/env python3
import sys
sys.path.insert(0, 'ocean-core')
from mega_layer_engine import MegaLayerEngine

engine = MegaLayerEngine()
query = 'Çfarë është Curiosity Ocean?'

try:
    activation, results = engine.process_query(query)
    print('✅ Core process_query works')
    print(f'Combinations: {results.get("combinations_used", 0)}')
    print(f'Meta Level: {activation.meta_level.name}')
    print(f'Multi-script zones: {results.get("multi_script", {}).get("zones_found", [])}')
except Exception as e:
    import traceback
    print(f'❌ Error: {type(e).__name__}: {e}')
    traceback.print_exc()
