import os
import asyncio
import json
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length))

        token = os.getenv("TELEGRAM_BOT_TOKEN")

        async def process():
            from telegram import Update, Bot
            from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
            from database import get_or_create_user, update_user_twitter, get_targets_for_user, save_daily_targets, mark_target_done, get_weekly_streak, upsert_target_account, log_growth, get_weekly_growth
            from models import CATEGORY_META

            app = Application.builder().token(token).build()

            async def start(update, context):
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
                webapp_url = os.getenv("WEBAPP_URL", "")
                user = update.effective_user
                get_or_create_user(user.id)
                keyboard = [[InlineKeyboardButton("🚀 Open ShegiGrowth", web_app=WebAppInfo(url=webapp_url))]]
                await update.message.reply_text(
                    f"👋 Hey {user.first_name}!\n\nWelcome to *ShegiGrowth*\n\n"
                    "Connect your Twitter:\n`/setup @yourhandle`",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

            async def setup(update, context):
                if not context.args:
                    await update.message.reply_text("Example: `/setup @yourhandle`", parse_mode="Markdown")
                    return
                handle = context.args[0].lstrip("@")
                telegram_id = update.effective_user.id
                await update.message.reply_text(f"🔍 Looking up @{handle}...")
                from twitter import get_user_by_handle, estimate_engagement_rate
                data = get_user_by_handle(handle)
                if not data:
                    await update.message.reply_text("❌ Account not found.")
                    return
                engagement = estimate_engagement_rate(handle)
                update_user_twitter(telegram_id, handle, data["follower_count"], "crypto")
                log_growth(user_id=get_or_create_user(telegram_id).id, follower_count=data["follower_count"], engagement_rate=engagement)
                await update.message.reply_text(f"✅ @{handle} connected!\n👥 Followers: *{data['follower_count']:,}*", parse_mode="Markdown")

            async def targets_cmd(update, context):
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
                webapp_url = os.getenv("WEBAPP_URL", "")
                telegram_id = update.effective_user.id
                db_user = get_or_create_user(telegram_id)
                targets = get_targets_for_user(db_user)
                if not targets:
                    await update.message.reply_text("No targets yet! Add with `/add @handle`", parse_mode="Markdown")
                    return
                save_daily_targets(db_user.id, [t.id for t in targets])
                streak = get_weekly_streak(db_user.id)
                text = "🎯 *Today's Targets*\n\n"
                for t in targets:
                    meta = CATEGORY_META.get(t.category, {})
                    text += f"{meta.get('emoji','•')} @{t.handle} — {t.follower_count:,} followers\n"
                text += f"\n🔥 Streak: *{streak} days*"
                keyboard = [[InlineKeyboardButton("📱 Open App", web_app=WebAppInfo(url=webapp_url))]]
                await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

            async def stats_cmd(update, context):
                telegram_id = update.effective_user.id
                db_user = get_or_create_user(telegram_id)
                growth = get_weekly_growth(db_user.id)
                streak = get_weekly_streak(db_user.id)
                gain = growth["gain"]
                sign = "+" if gain >= 0 else ""
                await update.message.reply_text(
                    f"📈 *Your Stats*\n\n🐦 @{db_user.twitter_handle}\n👥 Followers: *{db_user.follower_count:,}*\n📊 7-day: *{sign}{gain}*\n🔥 Streak: *{streak} days*",
                    parse_mode="Markdown"
                )

            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("setup", setup))
            app.add_handler(CommandHandler("targets", targets_cmd))
            app.add_handler(CommandHandler("stats", stats_cmd))

            await app.initialize()
            update = Update.de_json(body, app.bot)
            await app.process_update(update)
            await app.shutdown()

        asyncio.run(process())
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')
