import os
import json
import httpx
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
async def handler(request):
    params = request.query_params
    handle = params.get("handle", "").replace("@", "").strip()
    if not handle:
        return {"statusCode": 400, "body": json.dumps({"error": "handle required"})}
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.twitter.com/2/users/by/username/" + handle,
            headers=headers,
            params={
                "user.fields": "public_metrics,description,profile_image_url,created_at"
            }
        )
    if res.status_code != 200:
        return {"statusCode": 404, "body": json.dumps({"error": "user not found"})}
    data = res.json().get("data", {})
    metrics = data.get("public_metrics", {})
    followers = metrics.get("followers_count", 0)
    tweets = metrics.get("tweet_count", 0)
    following = metrics.get("following_count", 0)
    eng_rate = round((metrics.get("like_count", 0) / max(tweets, 1)) / max(followers, 1) * 100, 2) if tweets > 0 else 0.0
    return {
        "statusCode": 200,
        "body": json.dumps({
            "name": data.get("name"),
            "handle": handle,
            "description": data.get("description", ""),
            "followers_count": followers,
            "following_count": following,
            "tweet_count": tweets,
            "engagement_rate": eng_rate
        })
    }
