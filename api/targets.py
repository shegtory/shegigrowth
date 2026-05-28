from database import get_or_create_user, get_targets_for_user, save_daily_targets
from models import CATEGORY_META
def handler(request):
    telegram_id = request.args.get("telegram_id")
    if not telegram_id:
        return {"error": "telegram_id required"}, 400
    user = get_or_create_user(int(telegram_id))
    targets = get_targets_for_user(user)
    save_daily_targets(user.id, [t.id for t in targets])
    color_map = {
        "fellow": "green",
        "one_up": "purple",
        "hidden_gem": "amber",
        "leader": "blue",
    }
    result = []
    for t in targets:
        meta = CATEGORY_META.get(t.category, {})
        result.append({
            "id": t.id,
            "handle": t.handle,
            "follower_count": t.follower_count,
            "category": t.category,
            "emoji": meta.get("emoji", "•"),
            "label": meta.get("label", t.category),
            "color": color_map.get(t.category, "green"),
            "engagement_rate": t.engagement_rate or 0,
        })
    return {"targets": result}
