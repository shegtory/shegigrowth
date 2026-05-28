import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from database import get_all_active_users, get_targets_for_user, save_daily_targets, get_weekly_streak
from models import CATEGORY_META
load_dotenv()
async def send_daily():
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    users = get_all_active_users()
    for user in users:
        try:
            targets = get_targets_for_user(user)
            if not targets:
                continue
            save_daily_targets(user.id, [t.id for t in targets])
            streak = get_weekly_streak(user.id)
            text = "Good morning! Here are today targets:\n\n"
            for t in targets:
                meta = CATEGORY_META.get(t.category, {})
                emoji = meta.get("emoji", "-")
                text += f"{emoji} @{t.handle} - {t.follower_count:,} followers\n"
            text += f"\nStreak: {streak} days - keep it going!"
            await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send to {user.telegram_id}: {e}")
def handler(request):
    secret = request.args.get("secret")
    if secret != os.getenv("CRON_SECRET"):
        return {"error": "unauthorized"}, 401
    asyncio.run(send_daily())
    return {"status": "sent"}