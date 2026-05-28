import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    existing = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    if not existing.data:
        supabase.table("users").insert({"telegram_id": telegram_id}).execute()
    keyboard = [[InlineKeyboardButton("?? Open App", web_app={"url": WEBAPP_URL})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"???? {user.first_name}! ??\n?? ShegiGrowth ??? ?????.\n\n??? ????? ??????? ?? ??? ??:\n/setup @handle",
        reply_markup=reply_markup
    )
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("??????? ?????: /setup @handle")
        return
    handle = context.args[0].replace("@", "")
    telegram_id = update.effective_user.id
    supabase.table("users").update({"twitter_handle": handle}).eq("telegram_id", telegram_id).execute()
    await update.message.reply_text(f"? ????? @{handle} ??? ??!")
async def targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("?? Open App", web_app={"url": WEBAPP_URL})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("????????? ?????? ?? ????? ???? ??", reply_markup=reply_markup)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    if not user.data:
        await update.message.reply_text("??? /start ???")
        return
    u = user.data[0]
    await update.message.reply_text(
        f"?? ???? ??:\n??????: {u.get('follower_count', 0)}\nStreak: {u.get('streak', 0)} ???"
    )
async def handler(request):
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup))
    app.add_handler(CommandHandler("targets", targets))
    app.add_handler(CommandHandler("stats", stats))
    body = await request.json()
    update = Update.de_json(body, app.bot)
    await app.initialize()
    await app.process_update(update)
    return {"statusCode": 200}
