"""
Layer 3: GitHub Repositories Scanner
Target: 50,000 APIs
Source: GitHub API search for repositories with OpenAPI specs
"""

import aiohttp
import asyncio
import logging
import base64
from typing import List, Dict, Any
import json

class Layer3GitHubCrawler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.github.com"
        self.name = "GitHub Repositories Scanner"
        self.target_count = 50000
        
        # Search queries for finding API repositories
        self.search_queries = [
            "openapi.yaml OR openapi.yml OR swagger.yaml OR swagger.yml",
            "api documentation openapi",
            "rest api swagger",
            "graphql api schema",
            "api endpoints documentation",
            "postman collection",
            "api specification",
            "microservice api",
            "web api rest",
            "json api specification"
        ]
    
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect APIs from GitHub repositories"""
        apis = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Search repositories
                for query in self.search_queries[:5]:  # Limit queries to avoid rate limits
                    repo_apis = await self._search_repositories(session, query)
                    apis.extend(repo_apis)
                    
                    # Add delay to respect rate limits
                    await asyncio.sleep(2)
                
                # Search for specific API-related files
                file_apis = await self._search_api_files(session)
                apis.extend(file_apis)
        
        except Exception as e:
            self.logger.error(f"Layer 3 collection failed: {e}")
        
        unique_apis = self._deduplicate_layer(apis)
        self.logger.info(f"Layer 3 collected {len(unique_apis)} unique APIs")
        return unique_apis
    
    async def _search_repositories(self, session: aiohttp.ClientSession, query: str) -> List[Dict[str, Any]]:
        """Search GitHub repositories"""
        try:
            url = f"{self.base_url}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": 100  # Maximum allowed
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with session.get(url, params=params, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    repos = data.get("items", [])
                    
                    apis = []
                    for repo in repos:
                        # Extract API information from repository
                        api_data = await self._extract_repo_api_info(session, repo)
                        if api_data:
                            apis.extend(api_data)
                    
                    return apis
                
                elif response.status == 403:
                    self.logger.warning("GitHub API rate limit exceeded")
                    return []
                else:
                    self.logger.warning(f"GitHub search failed: HTTP {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error searching repositories with query '{query}': {e}")
            return []
    
    async def _search_api_files(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Search for specific API specification files"""
        file_queries = [
            "filename:openapi.yaml",
            "filename:swagger.yaml", 
            "filename:api.yaml",
            "filename:openapi.json",
            "filename:swagger.json"
        ]
        
        apis = []
        
        for query in file_queries:
            try:
                url = f"{self.base_url}/search/code"
                params = {
                    "q": query,
                    "sort": "indexed",
                    "per_page": 50
                }
                
                timeout = aiohttp.ClientTimeout(total=30)
                
                async with session.get(url, params=params, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        files = data.get("items", [])
                        
                        for file_info in files:
                            api_data = await self._extract_file_api_info(session, file_info)
                            if api_data:
                                apis.append(api_data)
                    
                    # Respect rate limits
                    await asyncio.sleep(1)
            
            except Exception as e:
                self.logger.error(f"Error searching files with query '{query}': {e}")
                continue
        
        return apis
    
    async def _extract_repo_api_info(self, session: aiohttp.ClientSession, repo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract API information from a repository"""
        try:
            repo_name = repo.get("full_name", "")
            repo_url = repo.get("html_url", "")
            description = repo.get("description", "")
            
            # Determine if this is likely an API repository
            if not self._is_likely_api_repo(repo):
                return []
            
            # Try to find API documentation or spec files
            api_files = await self._find_api_files_in_repo(session, repo_name)
            
            apis = []
            
            if api_files:
                # Found specific API files
                for file_path in api_files:
                    api_data = {
                        "name": f"{repo.get('name', '')} API",
                        "desc": description[:500],
                        "url": f"{repo_url}/blob/main/{file_path}",
                        "source": f"github/{repo_name}",
                        "category": self._determine_category_from_repo(repo),
                        "auth": "Unknown",
                        "region": "Global",
                        "metadata": {
                            "github_repo": repo_name,
                            "github_url": repo_url,
                            "stars": repo.get("stargazers_count", 0),
                            "forks": repo.get("forks_count", 0),
                            "language": repo.get("language", ""),
                            "created_at": repo.get("created_at", ""),
                            "updated_at": repo.get("updated_at", ""),
                            "api_file": file_path,
                            "license": repo.get("license", {}).get("name", "") if repo.get("license") else "",
                            "topics": repo.get("topics", [])
                        }
                    }
                    apis.append(api_data)
            else:
                # General API repository without specific files found
                api_data = {
                    "name": f"{repo.get('name', '')} API",
                    "desc": description[:500],
                    "url": repo_url,
                    "source": f"github/{repo_name}",
                    "category": self._determine_category_from_repo(repo),
                    "auth": "Unknown",
                    "region": "Global",
                    "metadata": {
                        "github_repo": repo_name,
                        "github_url": repo_url,
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language", ""),
                        "created_at": repo.get("created_at", ""),
                        "updated_at": repo.get("updated_at", ""),
                        "license": repo.get("license", {}).get("name", "") if repo.get("license") else "",
                        "topics": repo.get("topics", [])
                    }
                }
                apis.append(api_data)
            
            return apis
        
        except Exception as e:
            self.logger.error(f"Error extracting repo API info: {e}")
            return []
    
    async def _extract_file_api_info(self, session: aiohttp.ClientSession, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract API information from a specific file"""
        try:
            file_path = file_info.get("path", "")
            repo_info = file_info.get("repository", {})
            repo_name = repo_info.get("full_name", "")
            
            # Try to get file content for more details
            file_content = await self._get_file_content(session, repo_name, file_path)
            
            api_data = {
                "name": f"{repo_info.get('name', '')} API Spec",
                "desc": repo_info.get("description", "")[:500],
                "url": file_info.get("html_url", ""),
                "source": f"github/{repo_name}/spec",
                "category": self._determine_category_from_file(file_path, file_content),
                "auth": self._extract_auth_from_spec(file_content),
                "region": "Global",
                "metadata": {
                    "github_repo": repo_name,
                    "file_path": file_path,
                    "file_type": self._get_file_type(file_path),
                    "repo_language": repo_info.get("language", ""),
                    "stars": repo_info.get("stargazers_count", 0),
                    "spec_format": "OpenAPI" if "openapi" in file_path.lower() else "Swagger"
                }
            }
            
            return api_data
        
        except Exception as e:
            self.logger.error(f"Error extracting file API info: {e}")
            return None
    
    async def _find_api_files_in_repo(self, session: aiohttp.ClientSession, repo_name: str) -> List[str]:
        """Find API specification files in a repository"""
        api_files = []
        
        # Common API file patterns
        file_patterns = [
            "openapi.yaml", "openapi.yml", "openapi.json",
            "swagger.yaml", "swagger.yml", "swagger.json",
            "api.yaml", "api.yml", "api.json",
            "docs/openapi.yaml", "docs/swagger.yaml",
            "spec/openapi.yaml", "spec/swagger.yaml"
        ]
        
        for pattern in file_patterns:
            try:
                url = f"{self.base_url}/repos/{repo_name}/contents/{pattern}"
                timeout = aiohttp.ClientTimeout(total=10)
                
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        api_files.append(pattern)
            except:
                continue  # File doesn't exist or error occurred
        
        return api_files
    
    async def _get_file_content(self, session: aiohttp.ClientSession, repo_name: str, file_path: str) -> str:
        """Get file content from GitHub"""
        try:
            url = f"{self.base_url}/repos/{repo_name}/contents/{file_path}"
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("encoding") == "base64":
                        content = base64.b64decode(data.get("content", "")).decode("utf-8")
                        return content[:2000]  # Limit content size
        except:
            pass
        
        return ""
    
    def _is_likely_api_repo(self, repo: Dict[str, Any]) -> bool:
        """Determine if repository is likely an API"""
        name = repo.get("name", "").lower()
        description = repo.get("description", "").lower() if repo.get("description") else ""
        topics = repo.get("topics", [])
        
        api_indicators = [
            "api", "rest", "graphql", "swagger", "openapi", 
            "microservice", "service", "endpoint", "sdk"
        ]
        
        # Check name
        for indicator in api_indicators:
            if indicator in name:
                return True
        
        # Check description
        for indicator in api_indicators:
            if indicator in description:
                return True
        
        # Check topics
        for topic in topics:
            if any(indicator in topic.lower() for indicator in api_indicators):
                return True
        
        return False
    
    def _determine_category_from_repo(self, repo: Dict[str, Any]) -> str:
        """Determine category from repository information"""
        name = repo.get("name", "").lower()
        description = repo.get("description", "").lower() if repo.get("description") else ""
        language = repo.get("language", "").lower()
        topics = " ".join(repo.get("topics", [])).lower()
        
        text = f"{name} {description} {language} {topics}"
        
        # Category keywords
        categories = {
            "Web Development": ["web", "frontend", "backend", "fullstack", "react", "vue", "angular"],
            "Mobile": ["mobile", "android", "ios", "react-native", "flutter"],
            "AI/ML": ["ai", "ml", "machine-learning", "artificial-intelligence", "tensorflow", "pytorch"],
            "Database": ["database", "db", "sql", "nosql", "mongodb", "postgresql"],
            "Cloud": ["cloud", "aws", "azure", "gcp", "docker", "kubernetes"],
            "Finance": ["finance", "fintech", "payment", "trading", "blockchain", "crypto"],
            "Social": ["social", "chat", "messaging", "communication"],
            "E-commerce": ["ecommerce", "shop", "store", "payment", "cart"],
            "Developer Tools": ["devtools", "cli", "automation", "ci", "cd", "testing"],
            "IoT": ["iot", "sensor", "hardware", "embedded", "arduino", "raspberry"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "Other"
    
    def _determine_category_from_file(self, file_path: str, content: str) -> str:
        """Determine category from API specification file"""
        # Analyze file content for category hints
        if content:
            content_lower = content.lower()
            
            categories = {
                "Finance": ["payment", "bank", "currency", "trading", "financial"],
                "Social": ["user", "social", "friend", "message", "chat"],
                "E-commerce": ["product", "order", "cart", "payment", "shop"],
                "Content": ["content", "media", "blog", "cms", "article"],
                "Analytics": ["analytics", "metrics", "tracking", "event"],
                "Communication": ["email", "sms", "notification", "message"],
                "Storage": ["file", "storage", "upload", "download", "blob"]
            }
            
            for category, keywords in categories.items():
                if any(keyword in content_lower for keyword in keywords):
                    return category
        
        return "API"
    
    def _extract_auth_from_spec(self, content: str) -> str:
        """Extract authentication info from API specification"""
        if not content:
            return "Unknown"
        
        content_lower = content.lower()
        
        if "oauth" in content_lower:
            return "OAuth"
        elif "bearer" in content_lower:
            return "Bearer Token"
        elif "apikey" in content_lower or "api-key" in content_lower:
            return "API Key"
        elif "basic" in content_lower:
            return "Basic Auth"
        elif "jwt" in content_lower:
            return "JWT"
        else:
            return "Unknown"
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type from path"""
        if file_path.endswith(('.yaml', '.yml')):
            return "YAML"
        elif file_path.endswith('.json'):
            return "JSON"
        else:
            return "Unknown"
    
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
