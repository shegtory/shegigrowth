from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    twitter_handle = Column(String, nullable=True)
    niche = Column(String, default="crypto")          # crypto / defi / nft / solana / trading
    follower_count = Column(Integer, default=0)
    plan = Column(String, default="free")             # free / builder / pro
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)


class TargetAccount(Base):
    __tablename__ = "target_accounts"

    id = Column(Integer, primary_key=True)
    twitter_id = Column(String, unique=True, nullable=False)
    handle = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    tweet_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    niche = Column(String, default="crypto")
    category = Column(String, default="fellow")      # fellow / one_up / hidden_gem / leader
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


class DailyTarget(Base):
    __tablename__ = "daily_targets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("target_accounts.id"), nullable=False)
    date = Column(String, nullable=False)             # YYYY-MM-DD
    is_done = Column(Boolean, default=False)
    done_at = Column(DateTime, nullable=True)


class GrowthLog(Base):
    __tablename__ = "growth_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    follower_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    logged_at = Column(DateTime, default=datetime.utcnow)


# Category display info
CATEGORY_META = {
    "fellow": {
        "label": "🌱 Fellow Traveler",
        "emoji": "🌱",
        "description": "Same size as you — grow together",
    },
    "one_up": {
        "label": "🎯 One Level Up",
        "emoji": "🎯",
        "description": "Bigger but still reachable",
    },
    "hidden_gem": {
        "label": "💎 Hidden Gem",
        "emoji": "💎",
        "description": "Small account, huge engagement",
    },
    "leader": {
        "label": "👑 Niche Leader",
        "emoji": "👑",
        "description": "Know your space — watch them",
    },
}