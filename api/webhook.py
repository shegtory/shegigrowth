import os
import asyncio
from dotenv import load_dotenv
from telegram import Update

load_dotenv()

def handler(request):
    from telegram.ext import Application
    from bot import build_app
    import asyncio

    if request.method == "POST":
        async def process():
            app = build_app()
            await app.initialize()
            update = Update.de_json(request.json, app.bot)
            await app.process_update(update)
            await app.shutdown()
        asyncio.run(process())
        return {"status": "ok"}
    return {"status": "ok"}
