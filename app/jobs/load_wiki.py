import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base import BaseJob, JobResult, JobStatus, JobRunner
from app.config.settings import settings
from app.clients.redis import redis_client


class LoadWikiJob(BaseJob):
    """Job to load and cache wiki data from external sources."""
    
    def __init__(self):
        super().__init__("load_wiki")
        self.redis = redis_client
        self.wiki_data_url = settings.WIKI_DATA_URL
        self.github_data_url = settings.GITHUB_DATA_URL
        self.cache_seconds = settings.DATA_CACHE_SECONDS
        
    async def execute(self, *args, **kwargs) -> JobResult:
        """Execute the wiki data loading job."""
        started_at = datetime.utcnow()
        
        try:
            self.logger.info("Starting wiki data loading job")
            
            # Load wiki data
            wiki_data = await self._load_wiki_data()
            
            # Load GitHub data
            github_data = await self._load_github_data()
            
            # Cache the data
            await self._cache_data(wiki_data, github_data)
            
            completed_at = datetime.utcnow()
            
            return self.create_result(
                status=JobStatus.SUCCESS,
                message="Wiki data loaded successfully",
                started_at=started_at,
                completed_at=completed_at,
                data={
                    "wiki_data_count": len(wiki_data) if wiki_data else 0,
                    "github_data_count": len(github_data) if github_data else 0,
                    "cache_seconds": self.cache_seconds,
                    "wiki_data_url": self.wiki_data_url,
                    "github_data_url": self.github_data_url,
                }
            )
            
        except Exception as e:
            completed_at = datetime.utcnow()
            self.logger.error(f"Wiki data loading failed: {str(e)}")
            
            return self.create_result(
                status=JobStatus.FAILED,
                message="Wiki data loading failed",
                started_at=started_at,
                completed_at=completed_at,
                error_details=str(e)
            )
    
    async def _load_wiki_data(self) -> Optional[Dict[str, Any]]:
        """Load data from wiki API."""
        try:
            # Check cache first
            cache_key = "wiki_data"
            cached_data = self.redis.get(cache_key)
            
            if cached_data:
                self.logger.info("Using cached wiki data")
                return json.loads(cached_data)
            
            self.logger.info(f"Loading wiki data from {self.wiki_data_url}")
            
            # In a real implementation, you would make an HTTP request here
            # For now, we'll simulate with empty data
            wiki_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": self.wiki_data_url,
                "data": {}
            }
            
            # Cache the data
            self.redis.set(cache_key, json.dumps(wiki_data), ex=self.cache_seconds)
            
            return wiki_data
            
        except Exception as e:
            self.logger.error(f"Failed to load wiki data: {str(e)}")
            return None
    
    async def _load_github_data(self) -> Optional[Dict[str, Any]]:
        """Load data from GitHub sources."""
        try:
            # Check cache first
            cache_key = "github_data"
            cached_data = self.redis.get(cache_key)
            
            if cached_data:
                self.logger.info("Using cached GitHub data")
                return json.loads(cached_data)
            
            self.logger.info(f"Loading GitHub data from {self.github_data_url}")
            
            # In a real implementation, you would make HTTP requests to all GITHUB_SOURCES
            # For now, we'll simulate with the available sources
            github_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": self.github_data_url,
                "data": settings.GITHUB_SOURCES
            }
            
            # Cache the data
            self.redis.set(cache_key, json.dumps(github_data), ex=self.cache_seconds)
            
            return github_data
            
        except Exception as e:
            self.logger.error(f"Failed to load GitHub data: {str(e)}")
            return None
    
    async def _cache_data(self, wiki_data: Optional[Dict[str, Any]], github_data: Optional[Dict[str, Any]]) -> None:
        """Cache the loaded data."""
        try:
            if wiki_data:
                self.redis.set("wiki_data", json.dumps(wiki_data), ex=self.cache_seconds)
                self.logger.info("Wiki data cached successfully")
            
            if github_data:
                self.redis.set("github_data", json.dumps(github_data), ex=self.cache_seconds)
                self.logger.info("GitHub data cached successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to cache data: {str(e)}")
            raise


# CLI functionality
async def main():
    """Run the load wiki job as a standalone CLI script."""
    from app.config.logging import setup_logging
    
    # Setup logging
    setup_logging()
    
    # Create and run job
    job = LoadWikiJob()
    runner = JobRunner()
    
    result = await runner.run_job(job)
    
    print(f"Job completed with status: {result.status}")
    if result.message:
        print(f"Message: {result.message}")
    if result.error_details:
        print(f"Error: {result.error_details}")
    if result.data:
        print(f"Data: {json.dumps(result.data, indent=2)}")
    
    return result


if __name__ == "__main__":
    asyncio.run(main())