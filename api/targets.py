import os
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from database import get_or_create_user, get_targets_for_user, save_daily_targets
        from models import CATEGORY_META
        from urllib.parse import urlparse, parse_qs

        query = parse_qs(urlparse(self.path).query)
        telegram_id = query.get("telegram_id", [None])[0]

        if not telegram_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "telegram_id required"}).encode())
            return

        user = get_or_create_user(int(telegram_id))
        targets = get_targets_for_user(user)
        save_daily_targets(user.id, [t.id for t in targets])

        color_map = {"fellow": "green", "one_up": "purple", "hidden_gem": "amber", "leader": "blue"}
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

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"targets": result}).encode())
