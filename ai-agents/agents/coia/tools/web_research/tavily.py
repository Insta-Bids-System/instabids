"""
Tavily API Tool for COIA
EXTRACTED FROM LEGACY tools.py - REAL IMPLEMENTATION
"""

import logging
import os
import asyncio
from typing import Dict, Any, Optional

from ..base import BaseTool

logger = logging.getLogger(__name__)


class TavilySearchTool(BaseTool):
    """Tavily API web research tool - REAL IMPLEMENTATION"""
    
    def __init__(self):
        super().__init__()
        # Initialize Tavily API from environment
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.use_tavily = bool(self.tavily_api_key)
        
        if self.use_tavily:
            logger.info("TavilySearchTool initialized with API key")
        else:
            logger.warning("TavilySearchTool initialized without API key - disabled")

    async def discover_contractor_pages(self, company_name: str, website_url: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        🧠 PURE TAVILY INTELLIGENCE: Discover contractor pages using real Tavily API
        EXTRACTED FROM LEGACY tools.py
        """
        logger.info(f"Using REAL Tavily API to discover pages for {company_name}")
        
        try:
            # Import Tavily Python SDK
            try:
                from tavily import TavilyClient
            except ImportError:
                logger.warning("Tavily SDK not installed - THIS IS NOT A WORKING INTEGRATION")
                return {"error": "Tavily SDK not installed", "discovered_pages": []}
            
            # Initialize REAL Tavily client via env (no hard-coded keys)
            if not self.use_tavily or not self.tavily_api_key:
                logger.warning("Tavily disabled or TAVILY_API_KEY missing; skipping discovery")
                return {"error": "Tavily disabled or no API key", "discovered_pages": []}
            client = TavilyClient(api_key=self.tavily_api_key)
            
            discovery_data = {
                "main_website": website_url,
                "discovered_pages": [],
                "content_sources": [],
                "extraction_priority": [],
                "api_used": "REAL_TAVILY_API"  # Proof this is real
            }
            
            # REAL search queries
            search_queries = [
                f"{company_name} about us team",
                f"{company_name} services specialties",
                f"{company_name} projects gallery portfolio",
                f"{company_name} licenses insurance certifications",
                f"{company_name} contact information phone email",
                f"{company_name} {location} contractor reviews testimonials" if location else f"{company_name} reviews"
            ]
            
            discovered_urls = set()
            
            for query in search_queries:
                logger.info(f"Making REAL Tavily API call: {query}")
                
                try:
                    # Search for pages AND get their content
                    response = client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=10,
                        include_domains=[website_url.replace("http://", "").replace("https://", "").split("/")[0]] if website_url else None,
                        include_raw_content=True  # GET THE ACTUAL CONTENT
                    )
                    
                    if response and 'results' in response:
                        for result in response['results']:
                            url = result.get('url', '')
                            score = result.get('score', 0)
                            if url and url not in discovered_urls and score > 0.5:  # Filter by relevance score
                                discovered_urls.add(url)
                                discovery_data["discovered_pages"].append({
                                    "url": url,
                                    "title": result.get('title', ''),
                                    "score": score,
                                    "content": result.get('content', ''),  # Actual content from page
                                    "raw_content": result.get('raw_content', ''),  # Full raw content if available
                                    "type": self._categorize_page_type(url, result.get('title', '')),
                                    "priority": "high" if any(kw in url.lower() for kw in ['about', 'team', 'services', 'contact']) else "medium"
                                })
                        
                except Exception as api_error:
                    logger.error(f"REAL Tavily API error: {api_error}")
                    continue
                
                # Rate limiting for real API
                await asyncio.sleep(1)
            
            # Prioritize discovered pages
            discovery_data["extraction_priority"] = sorted(
                discovery_data["discovered_pages"],
                key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x.get("priority", "low"), 1),
                reverse=True
            )[:10]
            
            logger.info(f"REAL Tavily API discovered {len(discovery_data['discovered_pages'])} pages")
            
            # STEP 2: Extract full content from the best URLs using Extract API
            if discovery_data["discovered_pages"]:
                await self._extract_page_content(client, discovery_data)
            
            return discovery_data
            
        except Exception as e:
            logger.error(f"Tavily MCP discovery error: {e}")
            return {"error": str(e), "discovered_pages": []}

    async def _extract_page_content(self, client, discovery_data: Dict[str, Any]):
        """
        Extract full content from top URLs using Tavily Extract API
        EXTRACTED FROM LEGACY tools.py
        """
        logger.info("🔍 STEP 2: Using Tavily Extract API for full content extraction")
        
        # Get top 5 most relevant URLs
        top_urls = sorted(discovery_data["discovered_pages"], 
                        key=lambda x: x.get('score', 0), reverse=True)[:5]
        
        for page in top_urls:
            url = page["url"]
            try:
                # REAL EXTRACT API CALL
                extract_response = client.extract(
                    url,
                    extract_depth="advanced",  # Get tables, structured data
                    format="markdown"  # Better structured content
                )
                
                if extract_response and 'results' in extract_response:
                    for extract_result in extract_response['results']:
                        if extract_result.get('url') == url:
                            page["full_content"] = extract_result.get('raw_content', '')
                            logger.info(f"✅ Extracted {len(page['full_content'])} chars from {url}")
                            break
                
            except Exception as extract_error:
                logger.warning(f"Extract API error for {url}: {extract_error}")
                continue
            
            # Rate limiting
            await asyncio.sleep(0.5)

    def _categorize_page_type(self, url: str, title: str) -> str:
        """Helper to categorize page types from URL and title"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if 'about' in url_lower or 'team' in url_lower or 'about' in title_lower:
            return 'about'
        elif 'service' in url_lower or 'service' in title_lower:
            return 'services'
        elif 'project' in url_lower or 'gallery' in url_lower or 'portfolio' in url_lower:
            return 'portfolio'
        elif 'contact' in url_lower or 'contact' in title_lower:
            return 'contact'
        elif 'license' in url_lower or 'insurance' in url_lower or 'certification' in url_lower:
            return 'credentials'
        else:
            return 'other'