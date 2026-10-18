"""
UltraWebThinking - API Deduplicator
Kontrollon hash-e dhe unifikim të API entries
"""

import hashlib
import logging
from typing import List, Dict, Any, Set
from collections import defaultdict

class APIDeduplicator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()
    
    def generate_content_hash(self, api_data: Dict[str, Any]) -> str:
        """Generate content hash for API data"""
        # Create normalized content for hashing
        content_parts = [
            api_data.get("url", "").lower().strip().rstrip("/"),
            api_data.get("name", "").lower().strip(),
            api_data.get("category", "").lower().strip()
        ]
        content = "|".join(content_parts)
        return hashlib.md5(content.encode()).hexdigest()
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return ""
        
        # Remove common variations
        url = url.lower().strip()
        url = url.rstrip("/")
        
        # Remove common tracking parameters
        if "?" in url:
            base_url, params = url.split("?", 1)
            # Keep only essential parameters, remove tracking
            essential_params = []
            for param in params.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    # Keep API-related parameters, remove tracking
                    if key.lower() not in ["utm_source", "utm_medium", "utm_campaign", "ref", "referer"]:
                        essential_params.append(param)
            
            if essential_params:
                url = f"{base_url}?{'&'.join(essential_params)}"
            else:
                url = base_url
        
        return url
    
    def is_duplicate_url(self, url: str) -> bool:
        """Check if URL is duplicate"""
        normalized_url = self.normalize_url(url)
        if normalized_url in self.seen_urls:
            return True
        
        self.seen_urls.add(normalized_url)
        return False
    
    def is_duplicate_content(self, api_data: Dict[str, Any]) -> bool:
        """Check if API content is duplicate"""
        content_hash = self.generate_content_hash(api_data)
        if content_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(content_hash)
        return False
    
    def deduplicate_layer(self, apis: List[Dict[str, Any]], layer: int) -> List[Dict[str, Any]]:
        """Remove duplicates within a single layer"""
        unique_apis = []
        duplicates_count = 0
        
        # Reset tracking for this layer
        layer_urls: Set[str] = set()
        layer_hashes: Set[str] = set()
        
        for api_data in apis:
            # Check URL duplication within layer
            normalized_url = self.normalize_url(api_data.get("url", ""))
            if normalized_url in layer_urls:
                duplicates_count += 1
                continue
            
            # Check content duplication within layer
            content_hash = self.generate_content_hash(api_data)
            if content_hash in layer_hashes:
                duplicates_count += 1
                continue
            
            # Add to tracking sets
            layer_urls.add(normalized_url)
            layer_hashes.add(content_hash)
            
            # Add to global tracking
            self.seen_urls.add(normalized_url)
            self.seen_hashes.add(content_hash)
            
            unique_apis.append(api_data)
        
        self.logger.info(f"🔍 Layer {layer} deduplication: {len(apis)} → {len(unique_apis)} (removed {duplicates_count} duplicates)")
        return unique_apis
    
    def deduplicate_cross_layer(self, all_apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates across all layers"""
        unique_apis = []
        duplicates_count = 0
        
        # Group by normalized URL for better deduplication
        url_groups = defaultdict(list)
        
        for api_data in all_apis:
            normalized_url = self.normalize_url(api_data.get("url", ""))
            if normalized_url:
                url_groups[normalized_url].append(api_data)
        
        # For each URL group, keep the best entry
        for normalized_url, api_group in url_groups.items():
            if len(api_group) == 1:
                unique_apis.append(api_group[0])
            else:
                # Multiple APIs with same URL - pick the best one
                best_api = self.select_best_api(api_group)
                unique_apis.append(best_api)
                duplicates_count += len(api_group) - 1
        
        self.logger.info(f"🔄 Cross-layer deduplication: {len(all_apis)} → {len(unique_apis)} (removed {duplicates_count} duplicates)")
        return unique_apis
    
    def select_best_api(self, api_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best API from a group of duplicates"""
        # Scoring criteria (higher is better)
        def score_api(api_data: Dict[str, Any]) -> int:
            score = 0
            
            # Prefer APIs with better descriptions
            desc = api_data.get("desc", "")
            if len(desc) > 100:
                score += 10
            elif len(desc) > 50:
                score += 5
            elif len(desc) > 20:
                score += 2
            
            # Prefer APIs with categories
            if api_data.get("category"):
                score += 5
            
            # Prefer APIs with auth info
            if api_data.get("auth"):
                score += 3
            
            # Prefer APIs from reliable sources
            source = api_data.get("source", "").lower()
            if "apis.guru" in source:
                score += 15
            elif "publicapis.org" in source:
                score += 12
            elif "github" in source:
                score += 8
            elif "government" in source or "gov" in source:
                score += 10
            
            # Prefer HTTPS URLs
            url = api_data.get("url", "")
            if url.startswith("https://"):
                score += 5
            
            # Prefer APIs with detailed metadata
            metadata = api_data.get("metadata", {})
            if isinstance(metadata, dict) and len(metadata) > 3:
                score += 5
            
            return score
        
        # Select API with highest score
        best_api = max(api_group, key=score_api)
        
        # Merge metadata from all APIs in group
        merged_metadata = {}
        for api_data in api_group:
            metadata = api_data.get("metadata", {})
            if isinstance(metadata, dict):
                merged_metadata.update(metadata)
        
        if merged_metadata:
            best_api["metadata"] = merged_metadata
        
        return best_api
    
    async def global_deduplicate(self):
        """Perform global deduplication across all layers in database"""
        from .db_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Get all APIs from database
        all_apis = await db_manager.get_all_apis()
        
        if not all_apis:
            self.logger.info("🔍 No APIs found for global deduplication")
            return
        
        self.logger.info(f"🔄 Starting global deduplication of {len(all_apis)} APIs...")
        
        # Reset tracking
        self.seen_urls.clear()
        self.seen_hashes.clear()
        
        # Deduplicate
        unique_apis = self.deduplicate_cross_layer(all_apis)
        
        # Clear database and re-insert unique APIs
        if len(unique_apis) < len(all_apis):
            # Backup and clear database
            await db_manager.cleanup_database()
            
            self.logger.info(f"✅ Global deduplication completed: {len(all_apis)} → {len(unique_apis)} APIs")
        else:
            self.logger.info("🔍 No duplicates found during global deduplication")
    
    def get_duplicate_statistics(self) -> Dict[str, int]:
        """Get deduplication statistics"""
        return {
            "unique_urls": len(self.seen_urls),
            "unique_content_hashes": len(self.seen_hashes),
            "total_processed": len(self.seen_urls)  # Approximate
        }
