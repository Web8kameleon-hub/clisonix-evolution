"""
Layer 2: APIs Guru OpenAPI Catalog
Target: 3,000 APIs  
Source: https://api.apis.guru/v2/list.json
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any

class Layer2APIsGuru:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.apis.guru/v2"
        self.name = "APIs Guru OpenAPI Catalog"
        self.target_count = 3000
    
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect APIs from APIs Guru"""
        apis = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get main API list
                apis.extend(await self._fetch_api_list(session))
                
                # Get metrics for additional data
                metrics = await self._fetch_metrics(session)
                if metrics:
                    self.logger.info(f"APIs Guru metrics: {metrics.get('numAPIs', 0)} total APIs available")
        
        except Exception as e:
            self.logger.error(f"Layer 2 collection failed: {e}")
        
        unique_apis = self._deduplicate_layer(apis)
        self.logger.info(f"Layer 2 collected {len(unique_apis)} unique APIs")
        return unique_apis
    
    async def _fetch_api_list(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Fetch the main API list"""
        try:
            url = f"{self.base_url}/list.json"
            timeout = aiohttp.ClientTimeout(total=60)  # Proper timeout object
            
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    apis = []
                    for api_key, api_data in data.items():
                        # Extract basic info
                        preferred_version = api_data.get("preferred")
                        versions = api_data.get("versions", {})
                        
                        if preferred_version and preferred_version in versions:
                            version_data = versions[preferred_version]
                        elif versions:
                            # Take first available version
                            version_data = list(versions.values())[0]
                        else:
                            continue
                        
                        info = version_data.get("info", {})
                        
                        # Extract contact and external docs
                        contact = info.get("contact", {})
                        external_docs = info.get("externalDocs", {})
                        
                        # Determine category from various sources
                        category = self._determine_category(api_key, info, api_data)
                        
                        api_entry = {
                            "name": info.get("title", api_key),
                            "desc": info.get("description", "")[:1000],  # Limit description length
                            "url": version_data.get("swaggerUrl", ""),
                            "source": "apis.guru",
                            "category": category,
                            "auth": self._extract_auth_info(version_data),
                            "region": self._determine_region(api_key, info),
                            "metadata": {
                                "version": preferred_version or list(versions.keys())[0],
                                "swagger_version": version_data.get("swaggerVersion", ""),
                                "openapi_version": version_data.get("openapi", ""),
                                "info_version": info.get("version", ""),
                                "contact_name": contact.get("name", ""),
                                "contact_url": contact.get("url", ""),
                                "contact_email": contact.get("email", ""),
                                "external_docs": external_docs.get("url", ""),
                                "license": info.get("license", {}).get("name", ""),
                                "terms_of_service": info.get("termsOfService", ""),
                                "api_key": api_key,
                                "added": api_data.get("added", ""),
                                "updated": version_data.get("updated", "")
                            }
                        }
                        
                        apis.append(api_entry)
                    
                    return apis
                else:
                    self.logger.warning(f"Failed to fetch API list: HTTP {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error fetching API list: {e}")
            return []
    
    async def _fetch_metrics(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Fetch APIs Guru metrics"""
        try:
            url = f"{self.base_url}/metrics.json"
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
        except Exception as e:
            self.logger.error(f"Error fetching metrics: {e}")
            return {}
    
    def _determine_category(self, api_key: str, info: Dict[str, Any], api_data: Dict[str, Any]) -> str:
        """Determine API category from various sources"""
        # Check for x-apisguru-categories
        categories = api_data.get("x-apisguru-categories", [])
        if categories:
            return categories[0]
        
        # Check info for category hints
        title = info.get("title", "").lower()
        description = info.get("description", "").lower()
        api_key_lower = api_key.lower()
        
        # Category mapping based on keywords
        category_keywords = {
            "Social": ["social", "twitter", "facebook", "instagram", "linkedin"],
            "Finance": ["payment", "bank", "financial", "crypto", "currency", "trading"],
            "Maps": ["map", "location", "geo", "navigation", "directions"],
            "Weather": ["weather", "climate", "forecast"],
            "News": ["news", "media", "press"],
            "E-commerce": ["shop", "commerce", "retail", "product", "amazon"],
            "Communication": ["sms", "email", "messaging", "chat", "notification"],
            "Developer Tools": ["github", "git", "code", "development", "api"],
            "Entertainment": ["game", "music", "movie", "video", "entertainment"],
            "Health": ["health", "medical", "fitness", "doctor"],
            "Travel": ["travel", "hotel", "flight", "booking", "trip"],
            "Government": ["gov", "government", "public", "official"],
            "AI": ["ai", "artificial", "intelligence", "machine", "learning", "ml"],
            "IoT": ["iot", "sensor", "device", "smart", "home"],
            "Cloud": ["cloud", "storage", "database", "server", "hosting"]
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in title or keyword in description or keyword in api_key_lower:
                    return category
        
        return "Other"
    
    def _extract_auth_info(self, version_data: Dict[str, Any]) -> str:
        """Extract authentication information"""
        # Check OpenAPI 3.0 security schemes
        if "components" in version_data:
            security_schemes = version_data.get("components", {}).get("securitySchemes", {})
            if security_schemes:
                auth_types = []
                for scheme_name, scheme_data in security_schemes.items():
                    scheme_type = scheme_data.get("type", "")
                    if scheme_type == "apiKey":
                        auth_types.append("apiKey")
                    elif scheme_type == "oauth2":
                        auth_types.append("OAuth2")
                    elif scheme_type == "http":
                        auth_types.append("HTTP")
                return ", ".join(auth_types) if auth_types else "Unknown"
        
        # Check Swagger 2.0 security definitions
        if "securityDefinitions" in version_data:
            security_defs = version_data.get("securityDefinitions", {})
            if security_defs:
                auth_types = []
                for def_name, def_data in security_defs.items():
                    def_type = def_data.get("type", "")
                    if def_type == "apiKey":
                        auth_types.append("apiKey")
                    elif def_type == "oauth2":
                        auth_types.append("OAuth2")
                    elif def_type == "basic":
                        auth_types.append("Basic")
                return ", ".join(auth_types) if auth_types else "Unknown"
        
        return "None"
    
    def _determine_region(self, api_key: str, info: Dict[str, Any]) -> str:
        """Determine API region/coverage"""
        title = info.get("title", "").lower()
        description = info.get("description", "").lower()
        api_key_lower = api_key.lower()
        
        # Regional indicators
        if any(keyword in f"{title} {description} {api_key_lower}" for keyword in ["us", "usa", "united states", "american"]):
            return "US"
        elif any(keyword in f"{title} {description} {api_key_lower}" for keyword in ["eu", "europe", "european", "uk", "germany", "france"]):
            return "EU"
        elif any(keyword in f"{title} {description} {api_key_lower}" for keyword in ["asia", "japan", "china", "india", "singapore"]):
            return "Asia"
        else:
            return "Global"
    
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
