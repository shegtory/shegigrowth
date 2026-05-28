import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application
from bot import build_app
load_dotenv()
app = build_app()
async def process_update(update_data):
    await app.initialize()
    update = Update.de_json(update_data, app.bot)
    await app.process_update(update)
def handler(request):
    if request.method == "POST":
        update_data = request.json
        asyncio.run(process_update(update_data))
        return {"status": "ok"}
    return {"status": "ok"}
