import os
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        from database import mark_target_done

        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length))

        user_id = body.get("user_id")
        account_id = body.get("account_id")

        if not user_id or not account_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "missing fields"}).encode())
            return

        mark_target_done(user_id, account_id)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "done"}).encode())
