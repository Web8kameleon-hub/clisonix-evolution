"""
Layer 1: Public APIs Directory (publicapis.org)
Target: 1,500 APIs
Source: https://api.publicapis.org/entries
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any

class Layer1PublicAPIs:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.publicapis.org"
        self.name = "Public APIs Directory"
        self.target_count = 1500
    
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect APIs from publicapis.org"""
        apis = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get all entries
                apis.extend(await self._fetch_all_entries(session))
                
                # Get entries by categories for comprehensive coverage
                categories = await self._fetch_categories(session)
                for category in categories[:20]:  # Limit to top 20 categories
                    category_apis = await self._fetch_by_category(session, category)
                    apis.extend(category_apis)
        
        except Exception as e:
            self.logger.error(f"Layer 1 collection failed: {e}")
        
        # Remove duplicates within layer
        unique_apis = self._deduplicate_layer(apis)
        
        self.logger.info(f"Layer 1 collected {len(unique_apis)} unique APIs")
        return unique_apis
    
    async def _fetch_all_entries(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Fetch all API entries"""
        try:
            url = f"{self.base_url}/entries"
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get("entries", [])
                    
                    apis = []
                    for entry in entries:
                        api_data = {
                            "name": entry.get("API", ""),
                            "desc": entry.get("Description", ""),
                            "url": entry.get("Link", ""),
                            "source": "publicapis.org",
                            "category": entry.get("Category", ""),
                            "auth": entry.get("Auth", "None"),
                            "region": "Global",
                            "metadata": {
                                "https": entry.get("HTTPS", False),
                                "cors": entry.get("Cors", "unknown"),
                                "original_category": entry.get("Category", "")
                            }
                        }
                        apis.append(api_data)
                    
                    return apis
                else:
                    self.logger.warning(f"Failed to fetch all entries: HTTP {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error fetching all entries: {e}")
            return []
    
    async def _fetch_categories(self, session: aiohttp.ClientSession) -> List[str]:
        """Fetch available categories"""
        try:
            url = f"{self.base_url}/categories"
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("categories", [])
                else:
                    return []
        except Exception as e:
            self.logger.error(f"Error fetching categories: {e}")
            return []
    
    async def _fetch_by_category(self, session: aiohttp.ClientSession, category: str) -> List[Dict[str, Any]]:
        """Fetch APIs by specific category"""
        try:
            url = f"{self.base_url}/entries"
            params = {"category": category}
            
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get("entries", [])
                    
                    apis = []
                    for entry in entries:
                        api_data = {
                            "name": entry.get("API", ""),
                            "desc": entry.get("Description", ""),
                            "url": entry.get("Link", ""),
                            "source": f"publicapis.org/{category}",
                            "category": category,
                            "auth": entry.get("Auth", "None"),
                            "region": "Global",
                            "metadata": {
                                "https": entry.get("HTTPS", False),
                                "cors": entry.get("Cors", "unknown"),
                                "search_category": category
                            }
                        }
                        apis.append(api_data)
                    
                    return apis
                else:
                    return []
        
        except Exception as e:
            self.logger.error(f"Error fetching category {category}: {e}")
            return []
    
    def _deduplicate_layer(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates within layer"""
        seen_urls = set()
        unique_apis = []
        
        for api in apis:
            url = api.get("url", "").strip().lower()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_apis.append(api)
        
        return unique_apis
