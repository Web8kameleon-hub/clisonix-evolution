"""
EXTERNAL APIs INTEGRATION
=========================
Open source knowledge sources:
- Wikipedia
- Arxiv (research papers)
- PubMed (medical/science)
- DBpedia (structured data)
- GitHub (open source info)
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import httpx

logger = logging.getLogger("ocean_external_apis")

# Default timeout for external API calls
DEFAULT_TIMEOUT = 10


class ExternalSource(str, Enum):
    """External open source integrations"""
    WIKIPEDIA = "wikipedia"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    DBPEDIA = "dbpedia"
    GITHUB = "github"


class WikipediaConnector:
    """Connects to Wikipedia API for general knowledge"""
    
    BASE_URL = "https://en.wikipedia.org/w/api.php"
    
    @staticmethod
    async def search(query: str, limit: int = 5) -> Dict[str, Any]:
        """Search Wikipedia"""
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": limit,
                    "format": "json"
                }
                response = await client.get(WikipediaConnector.BASE_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get("query", {}).get("search", []):
                    results.append({
                        "title": item.get("title"),
                        "snippet": item.get("snippet"),
                        "timestamp": item.get("timestamp")
                    })
                
                return {
                    "source": ExternalSource.WIKIPEDIA.value,
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return {"error": str(e), "source": ExternalSource.WIKIPEDIA.value}
    
    @staticmethod
    async def get_page_summary(title: str) -> Dict[str, Any]:
        """Get Wikipedia page summary"""
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                params = {
                    "action": "query",
                    "titles": title,
                    "prop": "extracts",
                    "explaintext": True,
                    "exintro": True,
                    "format": "json"
                }
                response = await client.get(WikipediaConnector.BASE_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                summaries = []
                for page_id, page_data in pages.items():
                    if "extract" in page_data:
                        summaries.append({
                            "title": page_data.get("title"),
                            "extract": page_data.get("extract")[:500] + "...",  # Limit to 500 chars
                            "pageid": page_id
                        })
                
                return {
                    "source": ExternalSource.WIKIPEDIA.value,
                    "title": title,
                    "summaries": summaries
                }
        except Exception as e:
            logger.error(f"Wikipedia page error: {e}")
            return {"error": str(e)}


class ArxivConnector:
    """Connects to Arxiv for research papers"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    @staticmethod
    async def search(query: str, limit: int = 5) -> Dict[str, Any]:
        """Search Arxiv for research papers"""
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                params = {
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": limit,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                }
                response = await client.get(ArxivConnector.BASE_URL, params=params)
                response.raise_for_status()
                
                # Parse Atom XML feed
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                results = []
                namespace = {"atom": "http://www.w3.org/2005/Atom"}
                
                for entry in root.findall("atom:entry", namespace):
                    title_elem = entry.find("atom:title", namespace)
                    summary_elem = entry.find("atom:summary", namespace)
                    published_elem = entry.find("atom:published", namespace)
                    authors_elem = entry.findall("atom:author", namespace)
                    
                    authors = [author.find("atom:name", namespace).text 
                             for author in authors_elem if author.find("atom:name", namespace) is not None]
                    
                    if title_elem is not None:
                        results.append({
                            "title": title_elem.text,
                            "summary": summary_elem.text[:300] if summary_elem is not None else "",
                            "published": published_elem.text if published_elem is not None else "",
                            "authors": authors
                        })
                
                return {
                    "source": ExternalSource.ARXIV.value,
                    "query": query,
                    "results": results[:limit],
                    "count": len(results)
                }
        except Exception as e:
            logger.error(f"Arxiv search error: {e}")
            return {"error": str(e), "source": ExternalSource.ARXIV.value}


class PubMedConnector:
    """Connects to PubMed for medical/scientific literature"""
    
    BASE_URL = "https://pubmed.ncbi.nlm.nih.gov/api/citmatch"
    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    @staticmethod
    async def search(query: str, limit: int = 5) -> Dict[str, Any]:
        """Search PubMed"""
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": limit,
                    "retmode": "json"
                }
                response = await client.get(PubMedConnector.SEARCH_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for pmid in data.get("esearchresult", {}).get("idlist", [])[:limit]:
                    results.append({
                        "pmid": pmid,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    })
                
                return {
                    "source": ExternalSource.PUBMED.value,
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return {"error": str(e), "source": ExternalSource.PUBMED.value}


class DBpediaConnector:
    """Connects to DBpedia for structured data"""
    
    BASE_URL = "https://dbpedia.org/sparql"
    
    @staticmethod
    async def search(query: str, limit: int = 5) -> Dict[str, Any]:
        """Search DBpedia using SPARQL"""
        try:
            sparql_query = f"""
            SELECT ?resource ?label WHERE {{
                ?resource rdfs:label ?label .
                ?label bif:contains "{query}" .
                FILTER (lang(?label) = "en")
            }} LIMIT {limit}
            """
            
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                params = {
                    "query": sparql_query,
                    "format": "json"
                }
                response = await client.get(DBpediaConnector.BASE_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for binding in data.get("results", {}).get("bindings", []):
                    results.append({
                        "resource": binding.get("resource", {}).get("value"),
                        "label": binding.get("label", {}).get("value")
                    })
                
                return {
                    "source": ExternalSource.DBPEDIA.value,
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
        except Exception as e:
            logger.warning(f"DBpedia search warning: {e}")
            # DBpedia may not always be available
            return {"error": str(e), "source": ExternalSource.DBPEDIA.value}


class GitHubConnector:
    """Connects to GitHub for open source information"""
    
    BASE_URL = "https://api.github.com/search/repositories"
    
    @staticmethod
    async def search_repositories(query: str, limit: int = 5) -> Dict[str, Any]:
        """Search GitHub repositories"""
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": limit
                }
                response = await client.get(GitHubConnector.BASE_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for repo in data.get("items", [])[:limit]:
                    results.append({
                        "name": repo.get("name"),
                        "url": repo.get("html_url"),
                        "description": repo.get("description"),
                        "stars": repo.get("stargazers_count"),
                        "language": repo.get("language")
                    })
                
                return {
                    "source": ExternalSource.GITHUB.value,
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
            return {"error": str(e), "source": ExternalSource.GITHUB.value}


class ExternalAPIsManager:
    """Central manager for external API sources"""
    
    def __init__(self):
        self.wikipedia = WikipediaConnector()
        self.arxiv = ArxivConnector()
        self.pubmed = PubMedConnector()
        self.dbpedia = DBpediaConnector()
        self.github = GitHubConnector()
    
    async def search_all(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """Search across all external sources in parallel"""
        logger.info(f"🔍 Searching all external sources for: '{query}'")
        
        results = await asyncio.gather(
            self.wikipedia.search(query, limit),
            self.arxiv.search(query, limit),
            self.pubmed.search(query, limit),
            self.github.search_repositories(query, limit),
            return_exceptions=True
        )
        
        aggregated = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        source_names = ["wikipedia", "arxiv", "pubmed", "github"]
        for source_name, result in zip(source_names, results):
            if isinstance(result, Exception):
                aggregated["sources"][source_name] = {"error": str(result)}
            else:
                aggregated["sources"][source_name] = result
        
        return aggregated
    
    async def search_specific(self, source: ExternalSource, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search specific external source"""
        if source == ExternalSource.WIKIPEDIA:
            return await self.wikipedia.search(query, limit)
        elif source == ExternalSource.ARXIV:
            return await self.arxiv.search(query, limit)
        elif source == ExternalSource.PUBMED:
            return await self.pubmed.search(query, limit)
        elif source == ExternalSource.GITHUB:
            return await self.github.search_repositories(query, limit)
        else:
            return {"error": f"Unknown source: {source}"}


# Global singleton
_external_apis_manager: Optional[ExternalAPIsManager] = None


async def get_external_apis_manager() -> ExternalAPIsManager:
    """Get or create global external APIs manager"""
    global _external_apis_manager
    
    if _external_apis_manager is None:
        _external_apis_manager = ExternalAPIsManager()
        logger.info("✅ External APIs Manager initialized")
    
    return _external_apis_manager
