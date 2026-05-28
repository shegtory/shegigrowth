from http.server import BaseHTTPRequestHandler
import os
import json
import urllib.parse
import httpx
import asyncio
from supabase import create_client
TWITTER_CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.environ.get("TWITTER_CLIENT_SECRET")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
async def handle_callback(code, state):
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{WEBAPP_URL}/api/callback",
                "code_verifier": "challenge"
            },
            auth=(TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET)
        )
    if r.status_code != 200:
        return None, None
    token_data = r.json()
    access_token = token_data.get("access_token")
    # Get user info
    async with httpx.AsyncClient() as client:
        r2 = await client.get(
            "https://api.twitter.com/2/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"user.fields": "public_metrics,description,profile_image_url"}
        )
    if r2.status_code != 200:
        return None, None
    user_data = r2.json().get("data", {})
    metrics = user_data.get("public_metrics", {})
    return access_token, {
        "handle": user_data.get("username"),
        "name": user_data.get("name"),
        "followers_count": metrics.get("followers_count", 0),
        "following_count": metrics.get("following_count", 0),
        "tweet_count": metrics.get("tweet_count", 0)
    }
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        code = params.get("code")
        state = params.get("state")  # telegram_id
        if not code or not state:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code or state")
            return
        access_token, info = asyncio.run(handle_callback(code, state))
        if not info:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Twitter auth failed")
            return
        # Update user in Supabase
        supabase.table("users").update({
            "twitter_handle": info["handle"],
            "follower_count": info["followers_count"],
            "twitter_access_token": access_token
        }).eq("telegram_id", int(state)).execute()
        # Redirect back to app
        self.send_response(302)
        self.send_header("Location", WEBAPP_URL + "?connected=1")
        self.end_headers()
