import os
import json
from supabase import create_client
from datetime import date
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def handler(request):
    body = await request.json()
    telegram_id = body.get("telegram_id")
    target_id = body.get("target_id")
    if not telegram_id or not target_id:
        return {"statusCode": 400, "body": json.dumps({"error": "missing fields"})}
    user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    if not user.data:
        return {"statusCode": 404, "body": json.dumps({"error": "user not found"})}
    user_id = user.data[0]["id"]
    today = date.today().isoformat()
    supabase.table("daily_targets")\
        .update({"is_done": True})\
        .eq("user_id", user_id)\
        .eq("target_id", target_id)\
        .eq("date", today)\
        .execute()
    done_today = supabase.table("daily_targets")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("date", today)\
        .eq("is_done", True)\
        .execute()
    if len(done_today.data) >= 5:
        current_streak = user.data[0].get("streak", 0)
        supabase.table("users")\
            .update({"streak": current_streak + 1})\
            .eq("id", user_id)\
            .execute()
    return {"statusCode": 200, "body": json.dumps({"success": True})}
