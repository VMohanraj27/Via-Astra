import asyncio
import logging
from typing import Dict, List
from .tavily_client import search as tavily_search
from .research_queries import build_queries

logger = logging.getLogger(__name__)


async def run_query(query: str) -> Dict:
    """
    Execute a single Tavily search query.
    
    Args:
        query: The search query string
        
    Returns:
        Filtered Tavily response or error dict
    """
    logger.info(f"Running query: {query}")
    
    try:
        response = await tavily_search(query)
        logger.info(f"Query completed successfully: {query}")
        return response

    except Exception as e:
        logger.error(f"Query failed: {query}. Error: {str(e)}", exc_info=True)
        return {"error": str(e), "query": query}


async def run_metric_queries(queries: List[str]) -> List[Dict]:
    """
    Execute multiple queries in parallel for a single metric.
    
    Args:
        queries: List of search queries to execute
        
    Returns:
        List of cleaned responses
    """
    logger.info(f"Starting metric queries batch with {len(queries)} queries")
    
    tasks = [run_query(q) for q in queries]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    cleaned = []
    error_count = 0
    
    for i, r in enumerate(responses):
        if isinstance(r, Exception):
            logger.warning(f"Exception in response {i}: {str(r)}")
            error_count += 1
            continue
        
        if isinstance(r, dict) and "error" in r:
            logger.warning(f"Error response {i}: {r.get('error')}")
            error_count += 1
            continue
            
        cleaned.append(r)
    
    logger.info(f"Metric queries batch completed: {len(cleaned)} successful, {error_count} failed out of {len(queries)}")
    return cleaned


async def run_company_research(company: str, role: str, salary: str) -> Dict[str, List]:
    """
    Execute full company research across all metrics using parallel queries.
    
    Args:
        company: Company name
        role: Job role
        salary: Salary range
        
    Returns:
        Dictionary with metric names as keys and research results as values
    """
    logger.info(f"Starting company research for: {company} | Role: {role} | Salary: {salary}")
    
    query_map = build_queries(company, role, salary)
    logger.info(f"Built query map with {len(query_map)} metrics")
    
    total_queries = sum(len(queries) for queries in query_map.values())
    logger.info(f"Total queries to execute: {total_queries}")

    results: Dict[str, List] = {}
    tasks = {}

    # Start all metric tasks in parallel
    for metric, queries in query_map.items():
        logger.info(f"Launching metric task: {metric} with {len(queries)} queries")
        tasks[metric] = asyncio.create_task(
            run_metric_queries(queries)
        )

    # Gather all results as they complete
    for metric, task in tasks.items():
        try:
            results[metric] = await task
            logger.info(f"Metric '{metric}' completed: {len(results[metric])} result sets collected")
        except Exception as e:
            logger.error(f"Metric '{metric}' failed: {str(e)}", exc_info=True)
            results[metric] = []
    
    logger.info(f"Company research completed for {company}. Metrics processed: {len(results)}")

    return results