import logging
import asyncio
from database import init_db
from bot import build_app
from scheduler import build_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting GrowthRadar...")

    # Init database
    init_db()
    logger.info("Database ready.")

    # Build bot
    app = build_app()

    # Build scheduler
    scheduler = build_scheduler(app.bot)
    scheduler.start()
    logger.info("Scheduler started.")

    # Start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("Bot is running.")

    # Keep alive
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
