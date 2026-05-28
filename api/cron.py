import os
import asyncio
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from database import get_all_active_users, get_targets_for_user, save_daily_targets, get_weekly_streak
        from models import CATEGORY_META
        from telegram import Bot
        from urllib.parse import urlparse, parse_qs
        from dotenv import load_dotenv
        load_dotenv()

        query = parse_qs(urlparse(self.path).query)
        secret = query.get("secret", [None])[0]

        if secret != os.getenv("CRON_SECRET"):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "unauthorized"}).encode())
            return

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
                    print(f"Failed: {e}")

        asyncio.run(send_daily())
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "sent"}).encode())
