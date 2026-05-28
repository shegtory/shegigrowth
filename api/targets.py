import os
import json
from supabase import create_client
from datetime import date
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
    user_id = user.data[0]["id"]
    today = date.today().isoformat()
    daily = supabase.table("daily_targets")\
        .select("*, targets(*)")\
        .eq("user_id", user_id)\
        .eq("date", today)\
        .execute()
    return {"statusCode": 200, "body": json.dumps({"targets": daily.data})}
