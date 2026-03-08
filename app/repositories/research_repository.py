import logging
import asyncio
from typing import Dict, List, Any
from app.repositories.cache_repository import CacheRepository
from app.research.parallel_research import run_company_research as tavily_research

logger = logging.getLogger(__name__)

cache_repo = CacheRepository()


class ResearchRepository:
    """
    Repository layer for managing company research.
    Coordinates cache and Tavily API calls.
    """
    
    @staticmethod
    async def get_research(
        company: str,
        role: str,
        salary: str,
        use_cache: bool = True
    ) -> Dict[str, List]:
        """
        Get company research, using cache if available.
        Handles async Tavily calls within FastAPI event loop.
        
        Args:
            company: Company name
            role: Job role
            salary: Salary expectation
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary of research results by metric
        """
        logger.info(f"ResearchRepository: Fetching research for {company}")
        
        # Check cache first
        if use_cache:
            cached = cache_repo.get(company)
            if cached:
                logger.info(f"ResearchRepository: Using cached results for {company}")
                return cached.get("research_results", {})
        
        # Perform Tavily research (properly async)
        logger.info(f"ResearchRepository: Performing Tavily research for {company}")
        research_results = await tavily_research(company, role, salary)
        
        # Cache the results
        cache_repo.set(company, research_results)
        
        return research_results
    
    @staticmethod
    def clear_cache() -> None:
        """Clear entire research cache."""
        logger.info("ResearchRepository: Clearing cache")
        cache_repo.clear()
    
    @staticmethod
    def cleanup_expired_cache() -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        logger.info("ResearchRepository: Cleaning up expired entries")
        return cache_repo.cleanup_expired()
