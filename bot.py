import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from database import (
    get_or_create_user,
    update_user_twitter,
    get_targets_for_user,
    save_daily_targets,
    mark_target_done,
    get_weekly_streak,
    upsert_target_account,
    log_growth,
)
from twitter import get_user_by_handle, estimate_engagement_rate
from classifier import classify_and_enrich

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBAPP_URL = os.getenv("WEBAPP_URL", "")


# ── /start ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id)

    keyboard = [[
        InlineKeyboardButton(
            "🚀 Open GrowthRadar",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Hey {user.first_name}!\n\n"
        "Welcome to *GrowthRadar* — your daily Twitter growth engine.\n\n"
        "To get started, tell me your Twitter handle:\n"
        "Example: `/setup @yourhandle`",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── /setup @handle ─────────────────────────────────────

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide your Twitter handle.\n"
            "Example: `/setup @yourhandle`",
            parse_mode="Markdown",
        )
        return

    handle = context.args[0].lstrip("@")
    telegram_id = update.effective_user.id

    await update.message.reply_text(f"🔍 Looking up @{handle}...")

    data = get_user_by_handle(handle)
    if not data:
        await update.message.reply_text(
            "❌ Couldn't find that account. Check the handle and try again."
        )
        return

    engagement = estimate_engagement_rate(handle)
    followers = data["follower_count"]

    # Determine niche — default crypto, user can change later
    niche = "crypto"

    update_user_twitter(telegram_id, handle, followers, niche)
    log_growth(
        user_id=get_or_create_user(telegram_id).id,
        follower_count=followers,
        engagement_rate=engagement,
    )

    await update.message.reply_text(
        f"✅ *@{handle}* connected!\n\n"
        f"👥 Followers: *{followers:,}*\n"
        f"📊 Engagement: *{engagement}%*\n\n"
        "Now add target accounts with:\n"
        "`/add @targethandle`",
        parse_mode="Markdown",
    )


# ── /add @handle ───────────────────────────────────────

async def add_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide a Twitter handle.\n"
            "Example: `/add @someaccount`",
            parse_mode="Markdown",
        )
        return

    handle = context.args[0].lstrip("@")
    telegram_id = update.effective_user.id
    db_user = get_or_create_user(telegram_id)

    if not db_user.twitter_handle:
        await update.message.reply_text(
            "First set up your account with `/setup @yourhandle`",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(f"🔍 Fetching @{handle}...")

    data = get_user_by_handle(handle)
    if not data:
        await update.message.reply_text(
            "❌ Couldn't find that account. Check the handle and try again."
        )
        return

    engagement = estimate_engagement_rate(handle)
    data["engagement_rate"] = engagement
    data["niche"] = db_user.niche

    enriched = classify_and_enrich(data, db_user.follower_count)
    account = upsert_target_account(enriched)

    emoji = enriched["category_emoji"]
    label = enriched["category_label"]

    keyboard = [[
        InlineKeyboardButton("✅ Add to my targets", callback_data=f"add_target:{account.id}"),
        InlineKeyboardButton("❌ Skip", callback_data="skip"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"{emoji} *@{handle}*\n"
        f"Category: *{label}*\n\n"
        f"👥 Followers: *{enriched['follower_count']:,}*\n"
        f"📊 Engagement: *{engagement}%*\n\n"
        "Add this account to your targets?",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── /targets ───────────────────────────────────────────

async def show_targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    db_user = get_or_create_user(telegram_id)

    if not db_user.twitter_handle:
        await update.message.reply_text(
            "First set up your account with `/setup @yourhandle`",
            parse_mode="Markdown",
        )
        return

    targets = get_targets_for_user(db_user)
    if not targets:
        await update.message.reply_text(
            "No targets yet! Add some with `/add @handle`",
            parse_mode="Markdown",
        )
        return

    save_daily_targets(db_user.id, [t.id for t in targets])

    keyboard = [[
        InlineKeyboardButton(
            "📱 Open in App",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "🎯 *Today's Targets*\n\n"
    for t in targets:
        from models import CATEGORY_META
        meta = CATEGORY_META.get(t.category, {})
        emoji = meta.get("emoji", "•")
        text += f"{emoji} @{t.handle} — {t.follower_count:,} followers\n"

    streak = get_weekly_streak(db_user.id)
    text += f"\n🔥 Streak: *{streak} days*"

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


# ── /stats ─────────────────────────────────────────────

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    db_user = get_or_create_user(telegram_id)

    if not db_user.twitter_handle:
        await update.message.reply_text(
            "First set up your account with `/setup @yourhandle`",
            parse_mode="Markdown",
        )
        return

    from database import get_weekly_growth
    growth = get_weekly_growth(db_user.id)
    streak = get_weekly_streak(db_user.id)

    gain = growth["gain"]
    sign = "+" if gain >= 0 else ""

    await update.message.reply_text(
        f"📈 *Your Stats*\n\n"
        f"🐦 Handle: @{db_user.twitter_handle}\n"
        f"👥 Followers: *{db_user.follower_count:,}*\n"
        f"📊 7-day growth: *{sign}{gain}*\n"
        f"🔥 Streak: *{streak} days*",
        parse_mode="Markdown",
    )


# ── Callback: add_target / skip ────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "skip":
        await query.edit_message_text("Skipped.")
        return

    if data.startswith("add_target:"):
        account_id = int(data.split(":")[1])
        telegram_id = update.effective_user.id
        db_user = get_or_create_user(telegram_id)
        save_daily_targets(db_user.id, [account_id])
        await query.edit_message_text("✅ Added to your targets! Use /targets to see today's list.")
        return

    if data.startswith("done:"):
        parts = data.split(":")
        user_id = int(parts[1])
        account_id = int(parts[2])
        mark_target_done(user_id, account_id)
        await query.edit_message_text("✅ Marked as done!")
        return


# ── Build application ──────────────────────────────────

def build_app() -> Application:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup))
    app.add_handler(CommandHandler("add", add_target))
    app.add_handler(CommandHandler("targets", show_targets))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(handle_callback))

    return app
