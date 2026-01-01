import asyncio
import json
from datetime import datetime
from typing import Any

from pytz import UTC

from app.clients.redis import redis_client
from app.config.settings import settings
from app.utils.http import http_client

from .base import BaseJob, JobResult, JobRunner, JobStatus


class LoadWikiJob(BaseJob):
    """Job to load and cache wiki data from external sources."""

    def __init__(self):
        super().__init__("load_wiki")
        self.redis = redis_client
        self.sources = settings.GITHUB_SOURCES
        self.cache_version = settings.CACHE_VERSION

    async def execute(self, *args, **kwargs) -> JobResult:
        started_at = datetime.now(tz=UTC)

        try:
            self.logger.info("Loading wiki data from github sources")

            result_data = {}
            async with http_client.get_session() as session:
                for key, url in self.sources.items():
                    result_started_at = datetime.now(tz=UTC)

                    async with session.get(url) as response:
                        if response.status == 200:
                            try:
                                data = await response.json(content_type=None)
                                redis_client.set(f"{key}:{self.cache_version}", data)
                            except Exception as e:
                                self.logger.error(
                                    f"Failed to parse JSON data from {url}: {e}"
                                )
                        else:
                            self.logger.warning(
                                f"Failed to load wiki data from {url}: {response.status}"
                            )
                    result_data[key] = {
                        "url": url,
                        "status": "success",
                        "started_at": result_started_at,
                        "completed_at": datetime.now(tz=UTC),
                    }

            completed_at = datetime.now(tz=UTC)

            return self.create_result(
                status=JobStatus.SUCCESS,
                message="Wiki data loaded successfully",
                started_at=started_at,
                completed_at=completed_at,
                data=result_data,
            )

        except Exception as e:
            completed_at = datetime.now(tz=UTC)
            self.logger.error(f"Wiki data loading failed: {str(e)}")

            return self.create_result(
                status=JobStatus.FAILED,
                message="Wiki data loading failed",
                started_at=started_at,
                completed_at=completed_at,
                error_details=str(e),
            )


async def execute():
    from app.config.logging import setup_logging

    setup_logging()

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
    asyncio.run(execute())
