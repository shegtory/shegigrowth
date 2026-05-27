from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, date
from typing import Optional
from models import Base, User, TargetAccount, DailyTarget, GrowthLog
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///growthradar.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create all tables on startup."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return SessionLocal()


# ── Users ──────────────────────────────────────────────

def get_or_create_user(telegram_id: int) -> User:
    db = get_session()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    return user


def update_user_twitter(telegram_id: int, handle: str, follower_count: int, niche: str):
    db = get_session()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.twitter_handle = handle.lstrip("@")
        user.follower_count = follower_count
        user.niche = niche
        user.last_seen = datetime.utcnow()
        db.commit()
    db.close()


def get_all_active_users() -> list[User]:
    db = get_session()
    users = db.query(User).filter(User.is_active == True, User.twitter_handle != None).all()
    db.close()
    return users


# ── Target Accounts ────────────────────────────────────

def upsert_target_account(data: dict) -> TargetAccount:
    """Insert or update a target account."""
    db = get_session()
    account = db.query(TargetAccount).filter(
        TargetAccount.twitter_id == data["twitter_id"]
    ).first()

    if account:
        for key, value in data.items():
            setattr(account, key, value)
        account.last_updated = datetime.utcnow()
    else:
        account = TargetAccount(**data)
        db.add(account)

    db.commit()
    db.refresh(account)
    db.close()
    return account


def get_targets_for_user(user: User, limit: int = 5) -> list[TargetAccount]:
    """Get today's target accounts for a user — one from each category."""
    db = get_session()
    today = date.today().isoformat()

    # Get account IDs already shown today
    shown_ids = [
        r.account_id for r in
        db.query(DailyTarget).filter(
            DailyTarget.user_id == user.id,
            DailyTarget.date == today
        ).all()
    ]

    results = []
    categories = ["fellow", "one_up", "hidden_gem", "leader"]

    for category in categories:
        account = (
            db.query(TargetAccount)
            .filter(
                TargetAccount.niche == user.niche,
                TargetAccount.category == category,
                TargetAccount.is_active == True,
                ~TargetAccount.id.in_(shown_ids) if shown_ids else True,
            )
            .order_by(TargetAccount.engagement_rate.desc())
            .first()
        )
        if account:
            results.append(account)

    # Fill remaining slots with "fellow" if needed
    while len(results) < limit:
        extra = (
            db.query(TargetAccount)
            .filter(
                TargetAccount.niche == user.niche,
                TargetAccount.is_active == True,
                ~TargetAccount.id.in_(shown_ids + [a.id for a in results]),
            )
            .order_by(TargetAccount.engagement_rate.desc())
            .first()
        )
        if extra:
            results.append(extra)
        else:
            break

    db.close()
    return results[:limit]


# ── Daily Targets ──────────────────────────────────────

def save_daily_targets(user_id: int, account_ids: list[int]):
    db = get_session()
    today = date.today().isoformat()
    for acc_id in account_ids:
        exists = db.query(DailyTarget).filter(
            DailyTarget.user_id == user_id,
            DailyTarget.account_id == acc_id,
            DailyTarget.date == today
        ).first()
        if not exists:
            db.add(DailyTarget(user_id=user_id, account_id=acc_id, date=today))
    db.commit()
    db.close()


def mark_target_done(user_id: int, account_id: int):
    db = get_session()
    today = date.today().isoformat()
    target = db.query(DailyTarget).filter(
        DailyTarget.user_id == user_id,
        DailyTarget.account_id == account_id,
        DailyTarget.date == today
    ).first()
    if target:
        target.is_done = True
        target.done_at = datetime.utcnow()
        db.commit()
    db.close()


def get_weekly_streak(user_id: int) -> int:
    """Count consecutive active days in last 7 days."""
    db = get_session()
    streak = 0
    for i in range(7):
        from datetime import timedelta
        check_date = (date.today() - timedelta(days=i)).isoformat()
        done = db.query(DailyTarget).filter(
            DailyTarget.user_id == user_id,
            DailyTarget.date == check_date,
            DailyTarget.is_done == True
        ).first()
        if done:
            streak += 1
        else:
            break
    db.close()
    return streak


# ── Growth Log ─────────────────────────────────────────

def log_growth(user_id: int, follower_count: int, engagement_rate: float = 0.0):
    db = get_session()
    db.add(GrowthLog(
        user_id=user_id,
        follower_count=follower_count,
        engagement_rate=engagement_rate
    ))
    db.commit()
    db.close()


def get_weekly_growth(user_id: int) -> dict:
    """Returns follower gain over last 7 days."""
    db = get_session()
    logs = (
        db.query(GrowthLog)
        .filter(GrowthLog.user_id == user_id)
        .order_by(GrowthLog.logged_at.desc())
        .limit(14)
        .all()
    )
    db.close()

    if len(logs) < 2:
        return {"gain": 0, "start": 0, "end": 0}

    return {
        "gain": logs[0].follower_count - logs[-1].follower_count,
        "start": logs[-1].follower_count,
        "end": logs[0].follower_count,
    }