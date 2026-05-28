from http.server import BaseHTTPRequestHandler
import os
import json
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def get_twitter_info(handle):
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.twitter.com/2/users/by/username/{handle}",
            headers=headers,
            params={"user.fields": "public_metrics,description"}
        )
    if res.status_code != 200:
        return None
    data = res.json().get("data", {})
    metrics = data.get("public_metrics", {})
    return {
        "followers_count": metrics.get("followers_count", 0),
        "following_count": metrics.get("following_count", 0),
        "tweet_count": metrics.get("tweet_count", 0)
    }
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
    telegram_id = update.effective_user.id
    await update.message.reply_text(f"Fetching Twitter info for @{handle}...")
    info = await get_twitter_info(handle)
    if not info:
        await update.message.reply_text("Could not find Twitter account. Check the handle and try again.")
        return
    supabase.table("users").update({
        "twitter_handle": handle,
        "follower_count": info["followers_count"]
    }).eq("telegram_id", telegram_id).execute()
    await update.message.reply_text(
        f"Connected @{handle}!\nFollowers: {info['followers_count']}\nFollowing: {info['following_count']}\nTweets: {info['tweet_count']}"
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
