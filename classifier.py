from models import CATEGORY_META

# ── Thresholds ─────────────────────────────────────────
# Based on user's own follower count, classify target accounts

FELLOW_RATIO_MIN = 0.5      # at least 50% of user's followers
FELLOW_RATIO_MAX = 2.0      # at most 200% of user's followers

ONE_UP_RATIO_MIN = 2.0      # 2x to 10x user's followers
ONE_UP_RATIO_MAX = 10.0

HIDDEN_GEM_MAX_FOLLOWERS = 1000     # small account
HIDDEN_GEM_MIN_ENGAGEMENT = 5.0    # but high engagement %

LEADER_MIN_FOLLOWERS = 10000       # big account in niche


def classify_account(target_followers: int, target_engagement: float, user_followers: int) -> str:
    """
    Classify a target account into one of 4 categories
    based on the user's own follower count.

    Returns: "fellow" | "one_up" | "hidden_gem" | "leader"
    """

    if user_followers == 0:
        user_followers = 1  # avoid division by zero

    ratio = target_followers / user_followers

    # Hidden gem: small but punches above its weight
    if target_followers <= HIDDEN_GEM_MAX_FOLLOWERS and target_engagement >= HIDDEN_GEM_MIN_ENGAGEMENT:
        return "hidden_gem"

    # Leader: big account in the niche
    if target_followers >= LEADER_MIN_FOLLOWERS:
        return "leader"

    # One level up: bigger but reachable
    if ONE_UP_RATIO_MIN <= ratio < ONE_UP_RATIO_MAX:
        return "one_up"

    # Fellow traveler: similar size
    if FELLOW_RATIO_MIN <= ratio <= FELLOW_RATIO_MAX:
        return "fellow"

    # Fallback: if smaller than user, still fellow
    return "fellow"


def get_category_meta(category: str) -> dict:
    """Return display info for a category."""
    return CATEGORY_META.get(category, CATEGORY_META["fellow"])


def classify_and_enrich(account_data: dict, user_followers: int) -> dict:
    """
    Takes raw account data from twitter.py,
    adds category and category meta.

    account_data keys: twitter_id, handle, display_name,
                       follower_count, following_count,
                       tweet_count, engagement_rate, niche
    """
    category = classify_account(
        target_followers=account_data.get("follower_count", 0),
        target_engagement=account_data.get("engagement_rate", 0.0),
        user_followers=user_followers,
    )

    account_data["category"] = category
    account_data["category_label"] = get_category_meta(category)["label"]
    account_data["category_emoji"] = get_category_meta(category)["emoji"]

    return account_data
