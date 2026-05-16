from datetime import datetime

from pytz import UTC
from warframe_market.client import WarframeMarketClient
from warframe_market.common import Subtype

from app.clients.redis import redis_client
from app.config.settings import settings

from .base import BaseJob, JobResult, JobRunner, JobStatus


class LoadMarketItemsJob(BaseJob):
    def __init__(self):
        super().__init__("load_market_items")
        self.redis = redis_client
        self.cache_version = settings.CACHE_VERSION
        self.cache_ttl = settings.DATA_CACHE_SECONDS

    async def execute(self, *args, **kwargs) -> JobResult:
        started_at = datetime.now(tz=UTC)

        try:
            self.logger.info("Loading market items from Warframe Market API")
            client = WarframeMarketClient()
            items_response = await client.get_all_items()

            serialized = []
            for item in items_response.data:
                en_name = None
                if item.i18n:
                    for locale, i18n_model in item.i18n.items():
                        if locale.value == "en":
                            en_name = i18n_model.name
                            break
                    if not en_name:
                        en_name = next(iter(item.i18n.values())).name

                serialized.append(
                    {
                        "name": en_name,
                        "slug": item.slug,
                        "max_rank": item.max_rank,
                        "max_charges": item.max_charges,
                        "subtypes": item.subtypes,
                        "tags": item.tags,
                    }
                )

            import json

            redis_client.set(
                f"market_items:{self.cache_version}",
                json.dumps(serialized),
                ex=self.cache_ttl,
            )

            completed_at = datetime.now(tz=UTC)
            self.logger.info(
                f"Loaded {len(serialized)} market items into Redis cache"
            )

            return self.create_result(
                status=JobStatus.SUCCESS,
                message=f"Loaded {len(serialized)} market items",
                started_at=started_at,
                completed_at=completed_at,
                data={"item_count": len(serialized)},
            )

        except Exception as e:
            completed_at = datetime.now(tz=UTC)
            self.logger.error(f"Failed to load market items: {str(e)}")

            return self.create_result(
                status=JobStatus.FAILED,
                message="Failed to load market items",
                started_at=started_at,
                completed_at=completed_at,
                error_details=str(e),
            )


async def execute():
    from app.config.logging import setup_logging

    setup_logging()

    job = LoadMarketItemsJob()
    runner = JobRunner()

    result = await runner.run_job(job)

    print(f"Job completed with status: {result.status}")
    if result.message:
        print(f"Message: {result.message}")
    if result.error_details:
        print(f"Error: {result.error_details}")
    if result.data:
        print(f"Data: {result.data}")

    return result


if __name__ == "__main__":
    import asyncio

    asyncio.run(execute())
