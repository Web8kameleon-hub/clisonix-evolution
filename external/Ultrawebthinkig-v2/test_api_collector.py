"""
UltraWebThinking - API Collector Test Runner
Simple test script for the 12-layer API collection system

Usage:
    python test_api_collector.py --layers 1,2
    python test_api_collector.py --layers all --limit 10
"""

import asyncio
import sys
import os
import argparse
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from api_collector.layers.layer1_public_apis import Layer1PublicAPIs
from api_collector.layers.layer2_apis_guru import Layer2APIsGuru

async def test_layer(layer_class, layer_name: str, limit: int = None):
    """Test a specific layer"""
    print(f"\n🚀 Testing {layer_name}...")
    
    try:
        layer = layer_class()
        apis = await layer.collect()
        
        if limit:
            apis = apis[:limit]
        
        print(f"✅ {layer_name} collected {len(apis)} APIs")
        
        # Show sample results
        if apis:
            print(f"📋 Sample APIs from {layer_name}:")
            for i, api in enumerate(apis[:3]):
                print(f"   {i+1}. {api.get('name', 'Unknown')} - {api.get('category', 'No category')}")
                print(f"      URL: {api.get('url', 'No URL')}")
                print(f"      Source: {api.get('source', 'Unknown source')}")
                print()
        
        return len(apis)
        
    except Exception as e:
        print(f"❌ {layer_name} failed: {e}")
        return 0

async def main():
    parser = argparse.ArgumentParser(description="Test UltraWebThinking API Collector")
    parser.add_argument("--layers", default="1,2", help="Layers to test (e.g., '1,2' or 'all')")
    parser.add_argument("--limit", type=int, help="Limit results per layer")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("🌟 UltraWebThinking API Collector Test")
    print("=" * 50)
    
    # Available layers for testing
    test_layers = {
        1: (Layer1PublicAPIs, "Layer 1: Public APIs Directory"),
        2: (Layer2APIsGuru, "Layer 2: APIs Guru OpenAPI Catalog")
    }
    
    # Parse layer argument
    if args.layers.lower() == "all":
        layers_to_test = list(test_layers.keys())
    else:
        layers_to_test = [int(x) for x in args.layers.split(",")]
    
    total_apis = 0
    
    # Test each layer
    for layer_num in layers_to_test:
        if layer_num in test_layers:
            layer_class, layer_name = test_layers[layer_num]
            apis_count = await test_layer(layer_class, layer_name, args.limit)
            total_apis += apis_count
        else:
            print(f"⚠️ Layer {layer_num} not available for testing")
    
    print(f"\n🎉 Test completed!")
    print(f"📊 Total APIs collected: {total_apis}")
    print(f"🎯 Layers tested: {len(layers_to_test)}")

if __name__ == "__main__":
    asyncio.run(main())
