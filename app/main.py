import asyncio
import logging
import signal
import sys

from app.config.logging import setup_logging
from app.config.settings import settings
from app.jobs.load_wiki import JobRunner, LoadWikiJob


class JeffersonApp:
    def __init__(self):
        self.logger = logging.getLogger("jefferson_app")
        self.services = set()
        self.shutdown_requested = False

    async def setup_discord_bot(self):
        try:
            from app.bot.bot import create_bot

            self.logger.info("Starting Discord bot...")
            bot = await create_bot()
            bot_task = asyncio.create_task(bot.start(settings.DISCORD_TOKEN))

            def cleanup_bot():
                self.logger.info("Shutting down Discord bot...")
                asyncio.create_task(self._cleanup_bot_task(bot_task, bot))

            self.services.add((bot_task, cleanup_bot))
            self.logger.info("Discord bot service started")

        except Exception as e:
            self.logger.error(f"Failed to start Discord bot: {str(e)}")
            raise

    async def _cleanup_bot_task(self, bot_task, bot):
        """Helper method to clean up bot task."""
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
        await bot.close()

    async def setup_web_api(self):
        """Setup and run FastAPI web service."""
        try:
            import uvicorn

            from app.web.main import app

            self.logger.info(
                f"Starting web API on {settings.WEB_HOST}:{settings.WEB_PORT}..."
            )

            config = uvicorn.Config(
                app=app,
                host=settings.WEB_HOST,
                port=settings.WEB_PORT,
                reload=settings.WEB_DEBUG,
                log_level=settings.LOG_LEVEL.lower(),
                access_log=True,
            )
            server = uvicorn.Server(config)
            web_task = asyncio.create_task(server.serve())

            def cleanup_web():
                self.logger.info("Shutting down web API...")
                asyncio.create_task(self._cleanup_web_task(web_task, server))

            self.services.add((web_task, cleanup_web))
            self.logger.info("Web API service started")

        except Exception as e:
            self.logger.error(f"Failed to start web API: {str(e)}")
            raise

    async def _cleanup_web_task(self, web_task, server):
        """Helper method to clean up web task."""
        await server.shutdown()
        web_task.cancel()
        try:
            await web_task
        except asyncio.CancelledError:
            pass

    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers."""

        def signal_handler(signum, frame):
            self.logger.info(
                f"Received signal {signum}, initiating graceful shutdown..."
            )
            self.shutdown_requested = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def run(self):
        setup_logging()
        self.logger.info("Starting Jefferson application...")

        self.setup_signal_handlers()

        # Run job once on startup
        job = LoadWikiJob()
        runner = JobRunner()
        await runner.run_job(job)

        try:
            # Start Discord bot
            await self.setup_discord_bot()

            # Start FastAPI web service
            await self.setup_web_api()

            self.logger.info("All services started successfully")

            # Wait for services to complete or shutdown signal
            # Maybe there's a better way to do this later
            while self.services and not self.shutdown_requested:
                tasks = [service[0] for service in self.services]

                done, pending = await asyncio.wait(
                    tasks,
                    timeout=1.0,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in done:
                    if task.cancelled():
                        self.logger.info(f"Task was cancelled: {task}")
                    elif task.exception():
                        self.logger.error(
                            f"Task failed with exception: {task.exception()}"
                        )

                # If shutdown was requested, clean up remaining services
                if self.shutdown_requested:
                    break

            # Graceful cleanup of remaining services
            for task, cleanup in self.services:
                if not task.done():
                    task.cancel()
                    cleanup()

        except Exception as e:
            self.logger.error(f"Error running services: {str(e)}")
            raise
        finally:
            self.logger.info("Jefferson application shutting down...")


async def run_single_job(job_name: str):
    """Run a single job immediately and exit."""
    setup_logging()
    logger = logging.getLogger("jefferson_job_runner")

    logger.info(f"Running single job: {job_name}")

    if job_name == "load_wiki":
        from app.jobs.base import JobRunner
        from app.jobs.load_wiki import LoadWikiJob

        job = LoadWikiJob()
        runner = JobRunner()

        result = await runner.run_job(job)

        if result.status.value == "success":
            logger.info(f"Job completed successfully: {result.message}")
            sys.exit(0)
        else:
            logger.error(f"Job failed: {result.message}")
            if result.error_details:
                logger.error(f"Error details: {result.error_details}")
            sys.exit(1)
    else:
        logger.error(f"Unknown job: {job_name}")
        sys.exit(1)


def main():
    # For running jobs
    if len(sys.argv) >= 2 and sys.argv[1] == "job":
        if len(sys.argv) >= 3:
            job_name = sys.argv[2]
            asyncio.run(run_single_job(job_name))
        else:
            print("Usage: python -m app.main job <job_name>")
            print("Available jobs: load_wiki")
            sys.exit(1)

    app = JeffersonApp()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
