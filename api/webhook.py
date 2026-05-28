import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from http.server import BaseHTTPRequestHandler

load_dotenv()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        from bot import build_app
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        import json
        update_data = json.loads(body)

        async def process():
            app = build_app()
            await app.initialize()
            update = Update.de_json(update_data, app.bot)
            await app.process_update(update)
            await app.shutdown()

        asyncio.run(process())
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')
