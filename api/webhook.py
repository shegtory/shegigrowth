from http.server import BaseHTTPRequestHandler
import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing = supabase.table("users").select("*").eq("telegram_id", user.id).execute()
    if not existing.data:
        supabase.table("users").insert({"telegram_id": user.id}).execute()
    keyboard = [[InlineKeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        f"Welcome {user.first_name}!\nConnect your Twitter:\n/setup @handle",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setup @handle")
        return
    handle = context.args[0].replace("@", "")
    supabase.table("users").update({"twitter_handle": handle}).eq("telegram_id", update.effective_user.id).execute()
    await update.message.reply_text(f"Twitter handle @{handle} saved!")
async def targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text("See today's targets in the app", reply_markup=InlineKeyboardMarkup(keyboard))
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = supabase.table("users").select("*").eq("telegram_id", update.effective_user.id).execute()
    if not user.data:
        await update.message.reply_text("Please use /start first")
        return
    u = user.data[0]
    await update.message.reply_text(f"Followers: {u.get('follower_count', 0)}\nStreak: {u.get('streak', 0)} days")
async def process(body):
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup))
    app.add_handler(CommandHandler("targets", targets))
    app.add_handler(CommandHandler("stats", stats))
    update = Update.de_json(body, app.bot)
    await app.initialize()
    await app.process_update(update)
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        asyncio.run(process(body))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"ok": true}')
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"ok": true}')
