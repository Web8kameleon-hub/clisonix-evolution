"""
UltraWebThinking - API Collector Main Controller
Orkestron të gjitha layer-et për mbledh 200k+ APIs

Usage:
    python main.py --layers all
    python main.py --layers 1,2,3
    python main.py --export xlsx
"""

import asyncio
import argparse
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

from .db_manager import DatabaseManager
from .deduplicator import APIDeduplicator
from .exporter import APIExporter
from . import LAYER_DESCRIPTIONS, TARGET_APIS

# Import all layers
from .layers.layer1_public_apis import Layer1PublicAPIs
from .layers.layer2_apis_guru import Layer2APIsGuru
from .layers.layer3_github_crawler import Layer3GitHubCrawler
from .layers.layer4_data_gov import Layer4DataGov
from .layers.layer5_eu_data import Layer5EUData
from .layers.layer6_kaggle import Layer6Kaggle
from .layers.layer7_rapidapi import Layer7RapidAPI
from .layers.layer8_opensource_projects import Layer8OpenSourceProjects
from .layers.layer9_research_labs import Layer9ResearchLabs
from .layers.layer10_iot_mesh_data import Layer10IoTMeshData
from .layers.layer11_ai_libraries import Layer11AILibraries
from .layers.layer12_post_quantum_security import Layer12PostQuantumSecurity

class APICollectorMain:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.deduplicator = APIDeduplicator()
        self.exporter = APIExporter()
        
        # Initialize all layers
        self.layers = {
            1: Layer1PublicAPIs(),
            2: Layer2APIsGuru(),
            3: Layer3GitHubCrawler(),
            4: Layer4DataGov(),
            5: Layer5EUData(),
            6: Layer6Kaggle(),
            7: Layer7RapidAPI(),
            8: Layer8OpenSourceProjects(),
            9: Layer9ResearchLabs(),
            10: Layer10IoTMeshData(),
            11: Layer11AILibraries(),
            12: Layer12PostQuantumSecurity()
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging system"""
        log_dir = Path("../data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "collector.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def collect_layer(self, layer_num: int) -> Dict[str, Any]:
        """Collect APIs from a specific layer"""
        if layer_num not in self.layers:
            raise ValueError(f"Layer {layer_num} not found")
        
        layer = self.layers[layer_num]
        layer_name = LAYER_DESCRIPTIONS[layer_num]
        target_count = TARGET_APIS.get(f"layer{layer_num}", 1000)
        
        self.logger.info(f"🚀 Starting Layer {layer_num}: {layer_name}")
        self.logger.info(f"📊 Target APIs: {target_count:,}")
        
        start_time = time.time()
        
        try:
            # Collect APIs from this layer
            apis = await layer.collect()
            
            # Deduplicate within layer
            unique_apis = self.deduplicator.deduplicate_layer(apis, layer_num)
            
            # Save to database
            saved_count = await self.db_manager.save_apis(unique_apis, layer_num)
            
            duration = time.time() - start_time
            
            result = {
                "layer": layer_num,
                "name": layer_name,
                "collected": len(apis),
                "unique": len(unique_apis),
                "saved": saved_count,
                "target": target_count,
                "completion": (saved_count / target_count) * 100,
                "duration": duration
            }
            
            self.logger.info(f"✅ Layer {layer_num} completed:")
            self.logger.info(f"   📦 Collected: {len(apis):,} APIs")
            self.logger.info(f"   🔍 Unique: {len(unique_apis):,} APIs")
            self.logger.info(f"   💾 Saved: {saved_count:,} APIs")
            self.logger.info(f"   🎯 Progress: {result['completion']:.1f}% of target")
            self.logger.info(f"   ⏱️ Duration: {duration:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Layer {layer_num} failed: {e}")
            return {
                "layer": layer_num,
                "name": layer_name,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    async def collect_layers(self, layer_numbers: List[int]) -> List[Dict[str, Any]]:
        """Collect APIs from multiple layers"""
        self.logger.info(f"🌟 Starting UltraWebThinking API Collection")
        self.logger.info(f"📋 Layers to process: {layer_numbers}")
        
        # Initialize database
        await self.db_manager.initialize()
        
        # Collect from each layer
        results = []
        for layer_num in layer_numbers:
            result = await self.collect_layer(layer_num)
            results.append(result)
            
            # Brief pause between layers
            await asyncio.sleep(1)
        
        # Global deduplication across all layers
        self.logger.info("🔄 Performing global deduplication...")
        await self.deduplicator.global_deduplicate()
        
        # Generate summary
        total_collected = sum(r.get("collected", 0) for r in results)
        total_unique = sum(r.get("unique", 0) for r in results)
        total_saved = sum(r.get("saved", 0) for r in results)
        total_target = sum(TARGET_APIS.get(f"layer{r['layer']}", 0) for r in results if "layer" in r)
        
        self.logger.info(f"🎉 Collection Summary:")
        self.logger.info(f"   📦 Total Collected: {total_collected:,} APIs")
        self.logger.info(f"   🔍 Total Unique: {total_unique:,} APIs")
        self.logger.info(f"   💾 Total Saved: {total_saved:,} APIs")
        self.logger.info(f"   🎯 Overall Progress: {(total_saved/total_target)*100:.1f}% of target")
        
        return results
    
    async def export_data(self, format_type: str = "all"):
        """Export collected APIs to various formats"""
        self.logger.info(f"📤 Exporting data in format: {format_type}")
        
        if format_type in ["json", "all"]:
            await self.exporter.export_json()
        
        if format_type in ["csv", "all"]:
            await self.exporter.export_csv()
        
        if format_type in ["xlsx", "all"]:
            await self.exporter.export_xlsx()
        
        self.logger.info("✅ Export completed")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return await self.db_manager.get_statistics()

def parse_layer_argument(layers_arg: str) -> List[int]:
    """Parse layer argument (e.g., 'all', '1,2,3', '1-5')"""
    if layers_arg.lower() == "all":
        return list(range(1, 13))  # All 12 layers
    
    layers = []
    for part in layers_arg.split(","):
        if "-" in part:
            start, end = map(int, part.split("-"))
            layers.extend(range(start, end + 1))
        else:
            layers.append(int(part))
    
    return sorted(set(layers))

async def main():
    parser = argparse.ArgumentParser(description="UltraWebThinking API Collector")
    parser.add_argument("--layers", default="all", help="Layers to process (e.g., 'all', '1,2,3', '1-5')")
    parser.add_argument("--export", default="all", help="Export format (json, csv, xlsx, all)")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    
    args = parser.parse_args()
    
    collector = APICollectorMain()
    
    if args.stats:
        stats = await collector.get_statistics()
        print("\n📊 API Collection Statistics:")
        print(f"Total APIs: {stats.get('total_apis', 0):,}")
        print(f"Unique URLs: {stats.get('unique_urls', 0):,}")
        print(f"Categories: {stats.get('categories', 0):,}")
        print(f"Sources: {stats.get('sources', 0):,}")
        return
    
    try:
        layer_numbers = parse_layer_argument(args.layers)
        
        # Collect APIs
        results = await collector.collect_layers(layer_numbers)
        
        # Export data
        if args.export:
            await collector.export_data(args.export)
        
        print("\n🎉 UltraWebThinking API Collection Completed!")
        print("📁 Check ./backend/data/exports/ for output files")
        
    except Exception as e:
        logging.error(f"💥 Collection failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
