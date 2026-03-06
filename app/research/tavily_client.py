import asyncio
import logging
from typing import Dict, Any
from tavily import AsyncTavilyClient
from app.config import TAVILY_API_KEY

logger = logging.getLogger(__name__)

# Initialize async Tavily client
tavily_client_connection = AsyncTavilyClient(api_key=TAVILY_API_KEY)


def _filter_tavily_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter Tavily response to keep only essential fields for LLM processing.
    Keeps: answer, and results with only url, title, content.
    
    Args:
        response: Raw Tavily API response
        
    Returns:
        Filtered response with only necessary fields
    """
    logger.debug(f"Filtering Tavily response with {len(response.get('results', []))} results")
    
    filtered_results = []
    for result in response.get('results', []):
        filtered_result = {
            'url': result.get('url'),
            'title': result.get('title'),
            'content': result.get('content')
        }
        filtered_results.append(filtered_result)
    
    filtered_response = {
        'answer': response.get('answer'),
        'results': filtered_results
    }
    
    logger.debug(f"Filtered response reduced to {len(filtered_results)} results with url, title, content only")
    return filtered_response


async def search(query: str) -> Dict[str, Any]:
    """
    Perform async search using Tavily API.
    
    Args:
        query: Search query string
        
    Returns:
        Filtered search results containing answer and results with url, title, content
    """
    logger.info(f"Starting Tavily search for query: {query}")
    
    try:
        response = await tavily_client_connection.search(
            query=query,
            include_answer="advanced",
            search_depth="advanced",
            include_raw_content="markdown"
        )
        
        logger.info(f"Tavily search completed for query: {query}. Response has {len(response.get('results', []))} results")
        
        # Filter the response to keep only essential fields
        filtered_response = _filter_tavily_response(response)
        
        logger.debug(f"Tavily response filtered successfully")
        return filtered_response
        
    except Exception as e:
        logger.error(f"Tavily search failed for query '{query}': {str(e)}", exc_info=True)
        raise