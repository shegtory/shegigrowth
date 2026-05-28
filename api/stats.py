import os
import json
from supabase import create_client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def handler(request):
    params = request.query_params
    telegram_id = params.get("telegram_id")
    if not telegram_id:
        return {"statusCode": 400, "body": json.dumps({"error": "telegram_id required"})}
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    if not user.data:
        return {"statusCode": 404, "body": json.dumps({"error": "user not found"})}
    u = user.data[0]
    logs = supabase.table("growth_logs")\
        .select("*")\
        .eq("user_id", u["id"])\
        .order("recorded_at", desc=True)\
        .limit(7)\
        .execute()
    return {"statusCode": 200, "body": json.dumps({
        "follower_count": u.get("follower_count", 0),
        "streak": u.get("streak", 0),
        "twitter_handle": u.get("twitter_handle"),
        "growth_logs": logs.data
    })}
