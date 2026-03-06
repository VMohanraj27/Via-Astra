import asyncio
from typing import Dict, Any
from tavily import AsyncTavilyClient
from app.config import TAVILY_API_KEY

# Initialize async Tavily client
tavily_client_connection = AsyncTavilyClient(api_key=TAVILY_API_KEY)


async def search(query: str) -> Dict[str, Any]:
    """
    Perform async search using Tavily API.
    
    Args:
        query: Search query string
        
    Returns:
        Search results in advanced format with markdown content
    """
    response = await tavily_client.search(
        query=query,
        include_answer="advanced",
        search_depth="advanced",
        include_raw_content="markdown"
    )
    return response