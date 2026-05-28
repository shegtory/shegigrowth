from http.server import BaseHTTPRequestHandler
import os
import json
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client
import urllib.parse
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TWITTER_CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
def get_twitter_auth_url(telegram_id):
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": TWITTER_CLIENT_ID,
        "redirect_uri": f"{WEBAPP_URL}/api/callback",
        "scope": "tweet.read users.read",
        "state": str(telegram_id),
        "code_challenge": "challenge",
        "code_challenge_method": "plain"
    })
    return f"https://twitter.com/i/oauth2/authorize?{params}"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing = supabase.table("users").select("*").eq("telegram_id", user.id).execute()
    if not existing.data:
        supabase.table("users").insert({"telegram_id": user.id}).execute()
    auth_url = get_twitter_auth_url(user.id)
    keyboard = [
        [InlineKeyboardButton("Connect Twitter", url=auth_url)],
        [InlineKeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    await update.message.reply_text(
        f"Welcome {user.first_name}!\nConnect your Twitter account to get started.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    auth_url = get_twitter_auth_url(user.id)
    keyboard = [[InlineKeyboardButton("Connect Twitter", url=auth_url)]]
    await update.message.reply_text(
        "Click below to connect your Twitter account:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text("See today's targets in the app", reply_markup=InlineKeyboardMarkup(keyboard))
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = supabase.table("users").select("*").eq("telegram_id", update.effective_user.id).execute()
    if not user.data:
        await update.message.reply_text("Please use /start first")
        return
    u = user.data[0]
    handle = u.get("twitter_handle", "not connected")
    await update.message.reply_text(
        f"@{handle}\nFollowers: {u.get('follower_count', 0)}\nStreak: {u.get('streak', 0)} days"
    )
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
