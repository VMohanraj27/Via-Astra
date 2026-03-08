import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

logger = logging.getLogger(__name__)

CACHE_FILE = Path("cache/tavily_cache.json")
CACHE_EXPIRATION_DAYS = 30  # Default expiration (configurable)
FUZZY_MATCH_THRESHOLD = 85  # Threshold for fuzzy matching


class CacheRepository:
    """
    Manages in-memory cache for Tavily research results.
    Supports direct keyword search and fuzzy matching.
    """
    
    def __init__(self, expiration_days: int = CACHE_EXPIRATION_DAYS):
        """
        Initialize cache repository.
        
        Args:
            expiration_days: Number of days before cache entry expires
        """
        self.expiration_days = expiration_days
        self.cache = self._load_cache()
        logger.info(f"Cache initialized with {len(self.cache)} entries")
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from JSON file."""
        if not CACHE_FILE.exists():
            logger.info("Cache file not found, initializing empty cache")
            return {}
        
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
            logger.info(f"Loaded cache with {len(cache)} entries")
            return cache
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return {}
    
    def _save_cache(self) -> None:
        """Save cache to JSON file."""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2, default=str)
            logger.debug(f"Cache saved with {len(self.cache)} entries")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _is_expired(self, research_date: str) -> bool:
        """
        Check if cache entry has expired.
        
        Args:
            research_date: ISO format date string
            
        Returns:
            True if expired, False otherwise
        """
        try:
            research_datetime = datetime.fromisoformat(research_date)
            expiration_datetime = research_datetime + timedelta(days=self.expiration_days)
            is_expired = datetime.now() > expiration_datetime
            
            if is_expired:
                logger.debug(f"Cache entry expired: {research_date}")
            
            return is_expired
        except Exception as e:
            logger.warning(f"Error checking expiration: {e}")
            return True  # Treat as expired if we can't parse
    
    def _exact_match(self, company_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Perform exact keyword search in cache.
        
        Args:
            company_name: Company name to search
            
        Returns:
            Tuple of (cache_key, cache_entry) if found and not expired, None otherwise
        """
        cache_key = company_name.lower().strip()
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not self._is_expired(entry.get("research_date")):
                logger.info(f"Exact match found for: {company_name}")
                return cache_key, entry
            else:
                logger.info(f"Cache entry expired for: {company_name}")
                del self.cache[cache_key]
                self._save_cache()
                return None
        
        return None
    
    def _fuzzy_match(self, company_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Perform fuzzy search in cache for similar company names.
        
        Args:
            company_name: Company name to search
            
        Returns:
            Tuple of (cache_key, cache_entry) if found and not expired, None otherwise
        """
        search_name = company_name.lower().strip()
        
        if not self.cache:
            return None
        
        # Get all cache keys
        cache_keys = list(self.cache.keys())
        
        # Find best match using fuzzy matching
        matches = process.extract(search_name, cache_keys, scorer=fuzz.token_set_ratio, limit=1)
        
        if not matches:
            return None
        
        best_match, score = matches[0]
        
        if score >= FUZZY_MATCH_THRESHOLD:
            entry = self.cache[best_match]
            if not self._is_expired(entry.get("research_date")):
                logger.info(f"Fuzzy match found for: {company_name} (match: {best_match}, score: {score})")
                return best_match, entry
            else:
                logger.info(f"Fuzzy matched but expired: {best_match}")
                del self.cache[best_match]
                self._save_cache()
                return None
        
        return None
    
    def get(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cached research results for company.
        Tries exact match first, then fuzzy match.
        
        Args:
            company_name: Company name to search
            
        Returns:
            Cache entry if found and valid, None otherwise
        """
        logger.info(f"Searching cache for: {company_name}")
        
        # Try exact match first
        result = self._exact_match(company_name)
        if result:
            return result[1]
        
        # Try fuzzy match
        result = self._fuzzy_match(company_name)
        if result:
            return result[1]
        
        logger.info(f"No cache match found for: {company_name}")
        return None
    
    def set(
        self,
        company_name: str,
        research_results: Dict[str, Any],
        research_date: Optional[str] = None
    ) -> None:
        """
        Cache research results for company.
        
        Args:
            company_name: Company name
            research_results: Research results to cache
            research_date: Date of research (defaults to now)
        """
        if research_date is None:
            research_date = datetime.now().isoformat()
        
        cache_key = company_name.lower().strip()
        expiration_date = (
            datetime.fromisoformat(research_date) + timedelta(days=self.expiration_days)
        ).isoformat()
        
        self.cache[cache_key] = {
            "company_name": company_name,
            "research_results": research_results,
            "research_date": research_date,
            "expiration_date": expiration_date
        }
        
        self._save_cache()
        logger.info(f"Cached results for: {company_name} (expires: {expiration_date})")
    
    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        self._save_cache()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self.cache.items()
            if self._is_expired(entry.get("research_date"))
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)
