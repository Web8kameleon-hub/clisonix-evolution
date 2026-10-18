"""
Layer 4: Government Data Portals (data.gov)
Target: 5,000 APIs
Source: data.gov, EU Open Data, government APIs
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any

class Layer4DataGov:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = "Government Data Portals"
        self.target_count = 5000
        
        # Government data sources
        self.sources = {
            "data.gov": "https://catalog.data.gov/api/3/action/package_search",
            "eu_open_data": "https://data.europa.eu/api/hub/search/packages",
            "uk_gov": "https://ckan.publishing.service.gov.uk/api/3/action/package_search",
            "canada_gov": "https://open.canada.ca/data/api/3/action/package_search"
        }
    
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect APIs from government data portals"""
        apis = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for source_name, base_url in self.sources.items():
                    source_apis = await self._fetch_from_source(session, source_name, base_url)
                    apis.extend(source_apis)
                    
                    # Add delay between sources
                    await asyncio.sleep(2)
        
        except Exception as e:
            self.logger.error(f"Layer 4 collection failed: {e}")
        
        unique_apis = self._deduplicate_layer(apis)
        self.logger.info(f"Layer 4 collected {len(unique_apis)} unique APIs")
        return unique_apis
    
    async def _fetch_from_source(self, session: aiohttp.ClientSession, source_name: str, base_url: str) -> List[Dict[str, Any]]:
        """Fetch APIs from a specific government source"""
        apis = []
        
        try:
            # Fetch multiple pages
            for page in range(5):  # Limit to first 5 pages
                params = {
                    "rows": 100,
                    "start": page * 100,
                    "q": "api OR API OR rest OR REST OR json"
                }
                
                timeout = aiohttp.ClientTimeout(total=30)
                
                async with session.get(base_url, params=params, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Different response formats for different sources
                        if source_name == "data.gov":
                            packages = data.get("result", {}).get("results", [])
                        elif source_name == "eu_open_data":
                            packages = data.get("result", {}).get("results", [])
                        else:
                            packages = data.get("result", {}).get("results", [])
                        
                        for package in packages:
                            api_data = self._extract_api_from_package(package, source_name)
                            if api_data:
                                apis.append(api_data)
                    
                    else:
                        self.logger.warning(f"Failed to fetch from {source_name}: HTTP {response.status}")
                        break
                
                # Break if no more results
                if not packages:
                    break
                
                # Add delay between requests
                await asyncio.sleep(1)
        
        except Exception as e:
            self.logger.error(f"Error fetching from {source_name}: {e}")
        
        return apis
    
    def _extract_api_from_package(self, package: Dict[str, Any], source_name: str) -> Dict[str, Any]:
        """Extract API information from a data package"""
        try:
            title = package.get("title", "")
            name = package.get("name", "")
            notes = package.get("notes", "") or package.get("description", "")
            
            # Check if this package contains API data
            if not self._is_api_package(title, notes, package):
                return None
            
            # Extract URLs from resources
            resources = package.get("resources", [])
            api_url = self._find_api_url(resources)
            
            if not api_url:
                # Use package URL as fallback
                api_url = package.get("url", "") or f"https://catalog.data.gov/dataset/{name}"
            
            # Determine region based on source
            region = self._get_region_from_source(source_name)
            
            api_data = {
                "name": title or name,
                "desc": notes[:1000] if notes else "",
                "url": api_url,
                "source": f"gov/{source_name}",
                "category": self._determine_gov_category(package),
                "auth": "None",  # Most gov APIs are open
                "region": region,
                "metadata": {
                    "organization": package.get("organization", {}).get("title", ""),
                    "maintainer": package.get("maintainer", ""),
                    "maintainer_email": package.get("maintainer_email", ""),
                    "license": package.get("license_title", ""),
                    "created": package.get("metadata_created", ""),
                    "modified": package.get("metadata_modified", ""),
                    "tags": [tag.get("name", "") for tag in package.get("tags", [])],
                    "groups": [group.get("title", "") for group in package.get("groups", [])],
                    "num_resources": len(resources),
                    "package_id": package.get("id", ""),
                    "data_format": self._get_data_formats(resources)
                }
            }
            
            return api_data
        
        except Exception as e:
            self.logger.error(f"Error extracting API from package: {e}")
            return None
    
    def _is_api_package(self, title: str, notes: str, package: Dict[str, Any]) -> bool:
        """Determine if package contains API data"""
        text = f"{title} {notes}".lower()
        
        # API indicators
        api_keywords = [
            "api", "rest", "json", "xml", "endpoint", "web service",
            "data service", "web api", "restful", "json api"
        ]
        
        # Check title and description
        for keyword in api_keywords:
            if keyword in text:
                return True
        
        # Check resources for API-like formats
        resources = package.get("resources", [])
        for resource in resources:
            format_type = resource.get("format", "").lower()
            url = resource.get("url", "").lower()
            
            if format_type in ["json", "xml", "api", "rest"]:
                return True
            
            if "api" in url or "/json" in url or "/xml" in url:
                return True
        
        # Check tags
        tags = package.get("tags", [])
        for tag in tags:
            tag_name = tag.get("name", "").lower()
            if any(keyword in tag_name for keyword in api_keywords):
                return True
        
        return False
    
    def _find_api_url(self, resources: List[Dict[str, Any]]) -> str:
        """Find the best API URL from resources"""
        api_urls = []
        
        for resource in resources:
            url = resource.get("url", "")
            format_type = resource.get("format", "").lower()
            
            # Prefer JSON/XML/API resources
            if format_type in ["json", "xml", "api", "rest"]:
                api_urls.append(url)
            elif "api" in url.lower() or "/json" in url.lower():
                api_urls.append(url)
        
        # Return first API URL found
        return api_urls[0] if api_urls else ""
    
    def _get_region_from_source(self, source_name: str) -> str:
        """Get region based on source"""
        regions = {
            "data.gov": "US",
            "eu_open_data": "EU",
            "uk_gov": "UK",
            "canada_gov": "Canada"
        }
        return regions.get(source_name, "Global")
    
    def _determine_gov_category(self, package: Dict[str, Any]) -> str:
        """Determine category for government data"""
        title = package.get("title", "").lower()
        notes = package.get("notes", "").lower() if package.get("notes") else ""
        organization = package.get("organization", {}).get("title", "").lower()
        
        text = f"{title} {notes} {organization}"
        
        # Government data categories
        categories = {
            "Transportation": ["transport", "traffic", "road", "highway", "transit", "bus", "rail"],
            "Health": ["health", "medical", "hospital", "disease", "patient", "healthcare"],
            "Education": ["education", "school", "university", "student", "learning"],
            "Environment": ["environment", "weather", "climate", "air quality", "water", "pollution"],
            "Economics": ["economic", "economy", "budget", "finance", "spending", "tax"],
            "Demographics": ["census", "population", "demographic", "statistics", "survey"],
            "Public Safety": ["crime", "police", "fire", "emergency", "safety", "security"],
            "Energy": ["energy", "power", "electricity", "renewable", "oil", "gas"],
            "Housing": ["housing", "real estate", "property", "rent", "mortgage"],
            "Employment": ["employment", "job", "labor", "workforce", "unemployment"],
            "Agriculture": ["agriculture", "farm", "crop", "livestock", "food"],
            "Technology": ["technology", "digital", "broadband", "internet", "it"],
            "Legal": ["legal", "law", "regulation", "compliance", "court"],
            "Recreation": ["park", "recreation", "culture", "arts", "sports"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "Government Data"
    
    def _get_data_formats(self, resources: List[Dict[str, Any]]) -> List[str]:
        """Get list of data formats from resources"""
        formats = set()
        for resource in resources:
            format_type = resource.get("format", "")
            if format_type:
                formats.add(format_type.upper())
        return list(formats)
    
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
