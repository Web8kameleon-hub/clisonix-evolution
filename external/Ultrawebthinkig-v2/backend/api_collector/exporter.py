"""
UltraWebThinking - API Exporter
Nxjerr në CSV, XLSX, JSON formats
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class APIExporter:
    def __init__(self, export_dir: str = "../data/exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def export_json(self, filename: str = None) -> str:
        """Export APIs to JSON format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_apis_{timestamp}.json"
        
        filepath = self.export_dir / filename
        
        from .db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        try:
            # Get all APIs
            apis = await db_manager.get_all_apis()
            stats = await db_manager.get_statistics()
            
            # Prepare export data
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "total_apis": len(apis),
                    "statistics": stats,
                    "format": "json",
                    "version": "1.0"
                },
                "apis": apis
            }
            
            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"📄 Exported {len(apis)} APIs to JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"❌ JSON export failed: {e}")
            raise
    
    async def export_csv(self, filename: str = None) -> str:
        """Export APIs to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_apis_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        from .db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        try:
            # Get all APIs
            apis = await db_manager.get_all_apis()
            
            if not apis:
                self.logger.warning("⚠️ No APIs found for CSV export")
                return str(filepath)
            
            # Prepare CSV headers
            headers = ["name", "desc", "url", "source", "category", "auth", "region", "layer", "timestamp"]
            
            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                
                for api in apis:
                    # Clean up data for CSV
                    row = {}
                    for header in headers:
                        value = api.get(header, "")
                        # Handle special cases
                        if header == "metadata" and isinstance(value, dict):
                            value = json.dumps(value)
                        elif value is None:
                            value = ""
                        row[header] = str(value)
                    
                    writer.writerow(row)
            
            self.logger.info(f"📊 Exported {len(apis)} APIs to CSV: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"❌ CSV export failed: {e}")
            raise
    
    async def export_xlsx(self, filename: str = None) -> str:
        """Export APIs to Excel format with multiple sheets"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_apis_{timestamp}.xlsx"
        
        filepath = self.export_dir / filename
        
        from .db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        try:
            # Get all APIs and statistics
            apis = await db_manager.get_all_apis()
            stats = await db_manager.get_statistics()
            
            if not apis:
                self.logger.warning("⚠️ No APIs found for Excel export")
                return str(filepath)
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Main APIs sheet
                df_apis = pd.DataFrame(apis)
                
                # Clean up data for Excel
                for col in df_apis.columns:
                    if col == "metadata":
                        # Convert metadata dict to string
                        df_apis[col] = df_apis[col].apply(
                            lambda x: json.dumps(x) if isinstance(x, dict) else str(x)
                        )
                    elif df_apis[col].dtype == 'object':
                        # Convert object columns to string, handle None values
                        df_apis[col] = df_apis[col].fillna("").astype(str)
                
                df_apis.to_excel(writer, sheet_name='All APIs', index=False)
                
                # Statistics sheet
                stats_data = []
                for key, value in stats.items():
                    if isinstance(value, dict):
                        # Flatten nested dictionaries
                        for subkey, subvalue in value.items():
                            stats_data.append({
                                "Category": f"{key}.{subkey}",
                                "Value": subvalue
                            })
                    else:
                        stats_data.append({
                            "Category": key,
                            "Value": value
                        })
                
                df_stats = pd.DataFrame(stats_data)
                df_stats.to_excel(writer, sheet_name='Statistics', index=False)
                
                # Layer breakdown sheet
                layer_data = []
                for layer in range(1, 13):
                    layer_apis = [api for api in apis if api.get("layer") == layer]
                    if layer_apis:
                        layer_data.append({
                            "Layer": layer,
                            "Name": f"Layer {layer}",
                            "Count": len(layer_apis),
                            "Sample APIs": ", ".join([api.get("name", "")[:50] for api in layer_apis[:5]])
                        })
                
                if layer_data:
                    df_layers = pd.DataFrame(layer_data)
                    df_layers.to_excel(writer, sheet_name='Layer Breakdown', index=False)
                
                # Category breakdown sheet
                category_data = {}
                for api in apis:
                    category = api.get("category", "Unknown")
                    if category not in category_data:
                        category_data[category] = []
                    category_data[category].append(api.get("name", ""))
                
                category_summary = []
                for category, api_names in category_data.items():
                    category_summary.append({
                        "Category": category,
                        "Count": len(api_names),
                        "Sample APIs": ", ".join(api_names[:5])
                    })
                
                df_categories = pd.DataFrame(category_summary)
                df_categories = df_categories.sort_values("Count", ascending=False)
                df_categories.to_excel(writer, sheet_name='Categories', index=False)
            
            self.logger.info(f"📋 Exported {len(apis)} APIs to Excel: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"❌ Excel export failed: {e}")
            raise
    
    async def export_filtered(self, filter_criteria: Dict[str, Any], format_type: str = "json") -> str:
        """Export filtered APIs based on criteria"""
        from .db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        try:
            # Apply filters
            if "category" in filter_criteria:
                apis = await db_manager.get_apis_by_category(filter_criteria["category"])
            elif "layer" in filter_criteria:
                apis = await db_manager.get_apis_by_layer(filter_criteria["layer"])
            elif "search" in filter_criteria:
                apis = await db_manager.search_apis(filter_criteria["search"])
            else:
                apis = await db_manager.get_all_apis()
            
            # Generate filename
            filter_name = "_".join([f"{k}_{v}" for k, v in filter_criteria.items()])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"filtered_apis_{filter_name}_{timestamp}.{format_type}"
            
            # Export based on format
            if format_type.lower() == "json":
                return await self.export_json(filename)
            elif format_type.lower() == "csv":
                return await self.export_csv(filename)
            elif format_type.lower() == "xlsx":
                return await self.export_xlsx(filename)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Filtered export failed: {e}")
            raise
    
    async def export_summary_report(self) -> str:
        """Export comprehensive summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_collection_report_{timestamp}.xlsx"
        filepath = self.export_dir / filename
        
        from .db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        try:
            stats = await db_manager.get_statistics()
            all_apis = await db_manager.get_all_apis()
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Executive Summary
                summary_data = [
                    {"Metric": "Total APIs Collected", "Value": stats.get("total_apis", 0)},
                    {"Metric": "Unique URLs", "Value": stats.get("unique_urls", 0)},
                    {"Metric": "Categories", "Value": stats.get("categories", 0)},
                    {"Metric": "Data Sources", "Value": stats.get("sources", 0)},
                    {"Metric": "Database Size (MB)", "Value": round(stats.get("database_size", 0) / (1024*1024), 2)},
                    {"Metric": "Collection Date", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                ]
                
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
                
                # Layer Performance
                layer_performance = []
                from . import TARGET_APIS, LAYER_DESCRIPTIONS
                
                for layer in range(1, 13):
                    layer_key = f"layer_{layer}"
                    actual_count = stats.get("layer_breakdown", {}).get(layer_key, 0)
                    target_count = TARGET_APIS.get(f"layer{layer}", 0)
                    completion = (actual_count / target_count * 100) if target_count > 0 else 0
                    
                    layer_performance.append({
                        "Layer": layer,
                        "Description": LAYER_DESCRIPTIONS.get(layer, f"Layer {layer}"),
                        "Target": target_count,
                        "Collected": actual_count,
                        "Completion %": round(completion, 1),
                        "Status": "✅ Complete" if completion >= 100 else "🔄 In Progress" if completion > 50 else "⏳ Starting"
                    })
                
                df_layers = pd.DataFrame(layer_performance)
                df_layers.to_excel(writer, sheet_name='Layer Performance', index=False)
                
                # Top Categories
                top_categories = list(stats.get("top_categories", {}).items())[:20]
                df_top_cats = pd.DataFrame(top_categories, columns=["Category", "Count"])
                df_top_cats.to_excel(writer, sheet_name='Top Categories', index=False)
                
                # Auth Types
                auth_types = list(stats.get("auth_types", {}).items())
                df_auth = pd.DataFrame(auth_types, columns=["Auth Type", "Count"])
                df_auth.to_excel(writer, sheet_name='Auth Types', index=False)
            
            self.logger.info(f"📈 Exported summary report: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"❌ Summary report export failed: {e}")
            raise
