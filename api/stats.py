from database import get_or_create_user, get_weekly_streak, get_weekly_growth
def handler(request):
    telegram_id = request.args.get("telegram_id")
    if not telegram_id:
        return {"error": "telegram_id required"}, 400
    user = get_or_create_user(int(telegram_id))
    streak = get_weekly_streak(user.id)
    growth = get_weekly_growth(user.id)
    return {
        "handle": user.twitter_handle,
        "followers": user.follower_count,
        "streak": streak,
        "gain": growth["gain"],
    }
