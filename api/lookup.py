from http.server import BaseHTTPRequestHandler
import json
import httpx
import asyncio
GUEST_TOKEN_BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAAiZH5r9I6t9W3yZCLYHNLkFmm1U%3DUGpBkQkBLrAsTbJdaqKBrx1cO7s6GBSmhXfJlLAMkFgCGK"
async def get_guest_token():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={
                "Authorization": f"Bearer {GUEST_TOKEN_BEARER}",
                "User-Agent": "Mozilla/5.0"
            }
        )
        return r.json().get("guest_token")
async def get_user_info(handle):
    guest_token = await get_guest_token()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.twitter.com/1.1/users/show.json?screen_name={handle}",
            headers={
                "Authorization": f"Bearer {GUEST_TOKEN_BEARER}",
                "x-guest-token": guest_token,
                "User-Agent": "Mozilla/5.0"
            }
        )
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        "name": data.get("name"),
        "handle": handle,
        "followers_count": data.get("followers_count", 0),
        "following_count": data.get("friends_count", 0),
        "tweet_count": data.get("statuses_count", 0),
        "description": data.get("description", "")
    }
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        handle = params.get("handle", [""])[0].replace("@", "").strip()
        if not handle:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "handle required"}).encode())
            return
        data = asyncio.run(get_user_info(handle))
        if not data:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "user not found"}).encode())
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
