from http.server import BaseHTTPRequestHandler
import os
import json
import httpx
import asyncio
import urllib.parse
from supabase import create_client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def lookup(handle, access_token):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.twitter.com/2/users/by/username/{handle}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"user.fields": "public_metrics,description"}
        )
    if r.status_code != 200:
        return None
    data = r.json().get("data", {})
    metrics = data.get("public_metrics", {})
    followers = metrics.get("followers_count", 0)
    tweets = metrics.get("tweet_count", 0)
    eng_rate = round((metrics.get("like_count", 0) / max(tweets, 1)) / max(followers, 1) * 100, 2)
    return {
        "name": data.get("name"),
        "handle": handle,
        "description": data.get("description", ""),
        "followers_count": followers,
        "following_count": metrics.get("following_count", 0),
        "tweet_count": tweets,
        "engagement_rate": eng_rate
    }
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        handle = params.get("handle", "").replace("@", "").strip()
        telegram_id = params.get("telegram_id")
        if not handle or not telegram_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "handle and telegram_id required"}).encode())
            return
        user = supabase.table("users").select("twitter_access_token").eq("telegram_id", int(telegram_id)).execute()
        if not user.data or not user.data[0].get("twitter_access_token"):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not_connected"}).encode())
            return
        access_token = user.data[0]["twitter_access_token"]
        data = asyncio.run(lookup(handle, access_token))
        if not data:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "user not found"}).encode())
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
