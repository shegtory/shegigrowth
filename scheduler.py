import logging
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from database import get_all_active_users, get_targets_for_user, save_daily_targets, get_weekly_streak
from models import CATEGORY_META

load_dotenv()
logger = logging.getLogger(__name__)

WEBAPP_URL = os.getenv("WEBAPP_URL", "")
DAILY_SEND_HOUR = int(os.getenv("DAILY_SEND_HOUR", 9))
DAILY_SEND_MINUTE = int(os.getenv("DAILY_SEND_MINUTE", 0))


async def send_daily_targets(bot: Bot):
    """Send daily target list to all active users every morning."""
    users = get_all_active_users()
    logger.info(f"[scheduler] Sending daily targets to {len(users)} users")

    for user in users:
        try:
            targets = get_targets_for_user(user)
            if not targets:
                continue

            save_daily_targets(user.id, [t.id for t in targets])
            streak = get_weekly_streak(user.id)

            text = "🌅 *Good morning! Here are today's targets:*\n\n"
            for t in targets:
                meta = CATEGORY_META.get(t.category, {})
                emoji = meta.get("emoji", "•")
                text += f"{emoji} @{t.handle} — {t.follower_count:,} followers\n"

            text += f"\n🔥 Streak: *{streak} days* — keep it going!"

            keyboard = [[
                InlineKeyboardButton(
                    "📱 Open App",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await bot.send_message(
                chat_id=user.telegram_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

        except Exception as e:
            logger.error(f"[scheduler] Failed to send to user {user.telegram_id}: {e}")


def build_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_targets,
        trigger="cron",
        hour=DAILY_SEND_HOUR,
        minute=DAILY_SEND_MINUTE,
        args=[bot],
        id="daily_targets",
        replace_existing=True,
    )
    return scheduler
