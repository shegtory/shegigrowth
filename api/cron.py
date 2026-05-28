import os
import json
import httpx
from supabase import create_client
from datetime import date
import random
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def handler(request):
    users = supabase.table("users").select("*").execute()
    today = date.today().isoformat()
    for user in users.data:
        if not user.get("twitter_handle"):
            continue
        all_targets = supabase.table("targets").select("*").execute()
        if not all_targets.data:
            continue
        selected = random.sample(all_targets.data, min(5, len(all_targets.data)))
        for target in selected:
            supabase.table("daily_targets").insert({
                "user_id": user["id"],
                "target_id": target["id"],
                "date": today,
                "is_done": False
            }).execute()
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": user["telegram_id"],
                    "text": "??? ????! ??\n????????? ?????? ????????.\n??? ???? ?? ? streak ?? ??? ??! ??",
                    "reply_markup": {
                        "inline_keyboard": [[{
                            "text": "?? Open App",
                            "web_app": {"url": WEBAPP_URL}
                        }]]
                    }
                }
            )
    return {"statusCode": 200, "body": json.dumps({"success": True})}
