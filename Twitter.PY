import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

# ── Client setup ───────────────────────────────────────

def get_client() -> tweepy.Client:
    return tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
        wait_on_rate_limit=True,
    )


# ── User lookup ────────────────────────────────────────

def get_user_by_handle(handle: str) -> dict | None:
    """Fetch basic info for a Twitter handle."""
    client = get_client()
    handle = handle.lstrip("@")

    try:
        response = client.get_user(
            username=handle,
            user_fields=["public_metrics", "description", "created_at"],
        )
        if not response.data:
            return None

        user = response.data
        metrics = user.public_metrics

        return {
            "twitter_id": str(user.id),
            "handle": handle,
            "display_name": user.name,
            "follower_count": metrics["followers_count"],
            "following_count": metrics["following_count"],
            "tweet_count": metrics["tweet_count"],
        }
    except Exception as e:
        print(f"[twitter] get_user error: {e}")
        return None


# ── Search accounts by niche ───────────────────────────

NICHE_KEYWORDS = {
    "defi":    "DeFi yield liquidity protocol",
    "nft":     "NFT collection mint art",
    "solana":  "Solana SOL ecosystem",
    "trading": "crypto trading TA chart",
    "layer2":  "Layer2 ARB OP rollup",
    "crypto":  "crypto blockchain web3",
}


def search_accounts_by_niche(niche: str, max_results: int = 20) -> list[dict]:
    """
    Search for active accounts in a given niche.
    Returns list of dicts with account data.

    Note: Free tier allows ~500k tweet reads/month.
    We search tweets and extract unique authors.
    """
    client = get_client()
    query_term = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["crypto"])

    # Build query: recent tweets in niche, exclude retweets and replies
    query = f"{query_term} -is:retweet -is:reply lang:en"

    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["author_id", "public_metrics", "created_at"],
            expansions=["author_id"],
            user_fields=["public_metrics", "description"],
        )

        if not response.data or not response.includes:
            return []

        users = {u.id: u for u in response.includes.get("users", [])}
        results = []

        for tweet in response.data:
            user = users.get(tweet.author_id)
            if not user:
                continue

            m = user.public_metrics
            followers = m["followers_count"]
            tweets_total = m["tweet_count"]

            # Calculate rough engagement rate from tweet metrics
            tm = tweet.public_metrics
            total_engagement = (
                tm["like_count"] + tm["retweet_count"] + tm["reply_count"]
            )
            engagement_rate = (
                round((total_engagement / followers) * 100, 2)
                if followers > 0 else 0.0
            )

            results.append({
                "twitter_id": str(user.id),
                "handle": user.username,
                "display_name": user.name,
                "follower_count": followers,
                "following_count": m["following_count"],
                "tweet_count": tweets_total,
                "engagement_rate": engagement_rate,
                "niche": niche,
            })

        return results

    except Exception as e:
        print(f"[twitter] search_accounts error: {e}")
        return []


# ── Engagement rate helper ─────────────────────────────

def estimate_engagement_rate(handle: str) -> float:
    """
    Fetch last 5 tweets and calculate average engagement rate.
    Uses tweet public_metrics / follower_count.
    """
    client = get_client()
    handle = handle.lstrip("@")

    try:
        user_resp = client.get_user(
            username=handle,
            user_fields=["public_metrics"]
        )
        if not user_resp.data:
            return 0.0

        user = user_resp.data
        followers = user.public_metrics["followers_count"]
        if followers == 0:
            return 0.0

        tweets_resp = client.get_users_tweets(
            id=user.id,
            max_results=5,
            tweet_fields=["public_metrics"],
            exclude=["retweets", "replies"],
        )

        if not tweets_resp.data:
            return 0.0

        total = 0
        count = 0
        for tweet in tweets_resp.data:
            m = tweet.public_metrics
            eng = m["like_count"] + m["retweet_count"] + m["reply_count"]
            total += eng
            count += 1

        avg_eng = total / count if count > 0 else 0
        return round((avg_eng / followers) * 100, 2)

    except Exception as e:
        print(f"[twitter] engagement_rate error: {e}")
        return 0.0