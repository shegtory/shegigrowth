import os
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from database import get_or_create_user, get_weekly_streak, get_weekly_growth
        from urllib.parse import urlparse, parse_qs

        query = parse_qs(urlparse(self.path).query)
        telegram_id = query.get("telegram_id", [None])[0]

        if not telegram_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "telegram_id required"}).encode())
            return

        user = get_or_create_user(int(telegram_id))
        streak = get_weekly_streak(user.id)
        growth = get_weekly_growth(user.id)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "handle": user.twitter_handle,
            "followers": user.follower_count,
            "streak": streak,
            "gain": growth["gain"],
        }).encode())
