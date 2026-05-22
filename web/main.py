import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, date, timezone
from typing import Optional
from urllib.parse import parse_qsl

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import BOT_TOKEN, JWT_SECRET_KEY, TIMEZONE, WEBAPP_URL
from bot.models.goal import Goal, GoalType
from bot.models.plan import Plan, PlanStatus
from bot.models.user import User
from bot.models.score_log import ScoreLog
from database.db import get_db

app = FastAPI(title="IntizomAI Web API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBAPP_URL] if WEBAPP_URL else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "7"))


class LoginRequest(BaseModel):
    init_data: str


class PlanCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    scheduled_time: Optional[str] = None
    score_value: int = 5
    plan_date: Optional[date] = None


class PlanUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    scheduled_time: Optional[str] = None
    score_value: Optional[int] = None
    plan_date: Optional[date] = None
    status: Optional[str] = None


class GoalCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    goal_type: str
    target_value: int = 1
    current_value: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class GoalUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    goal_type: Optional[str] = None
    target_value: Optional[int] = None
    current_value: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_completed: Optional[bool] = None


def _parse_telegram_init_data(init_data: str) -> dict:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    hash_value = parsed.pop("hash", None)
    if not hash_value:
        raise HTTPException(status_code=401, detail="InitData hash topilmadi")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated, hash_value):
        raise HTTPException(status_code=401, detail="InitData noto'g'ri")

    auth_date = parsed.get("auth_date")
    if auth_date:
        auth_time = datetime.fromtimestamp(int(auth_date), tz=timezone.utc)
        if datetime.now(timezone.utc) - auth_time > timedelta(hours=24):
            raise HTTPException(status_code=401, detail="Session eskirgan")

    user_json = parsed.get("user")
    if not user_json:
        raise HTTPException(status_code=401, detail="User ma'lumoti topilmadi")
    return json.loads(user_json)


async def _get_or_create_user(session: AsyncSession, tg_user: dict) -> User:
    result = await session.execute(select(User).where(User.telegram_id == tg_user["id"]))
    user = result.scalar_one_or_none()
    if user:
        user.full_name = tg_user.get("first_name") or user.full_name
        user.username = tg_user.get("username") or user.username
        await session.commit()
        return user

    user = User(
        telegram_id=tg_user["id"],
        full_name=tg_user.get("first_name", "Telegram User"),
        username=tg_user.get("username", ""),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def _token_for_user(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "telegram_id": user.telegram_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    session: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
) -> User:
    if not JWT_SECRET_KEY:
        raise HTTPException(status_code=500, detail="JWT_SECRET_KEY sozlanmagan")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token talab qilinadi")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Token yaroqsiz") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token yaroqsiz")

    result = await session.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user


def _serialize_plan(plan: Plan) -> dict:
    return {
        "id": plan.id,
        "title": plan.title,
        "description": plan.description,
        "scheduled_time": plan.scheduled_time,
        "plan_date": str(plan.plan_date),
        "status": plan.status.value,
        "score_value": plan.score_value,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
    }


def _serialize_goal(goal: Goal) -> dict:
    return {
        "id": goal.id,
        "title": goal.title,
        "description": goal.description,
        "goal_type": goal.goal_type.value,
        "target_value": goal.target_value,
        "current_value": goal.current_value,
        "start_date": str(goal.start_date) if goal.start_date else None,
        "end_date": str(goal.end_date) if goal.end_date else None,
        "is_completed": goal.is_completed,
        "progress": round((goal.current_value / goal.target_value) * 100, 2) if goal.target_value else 0,
    }


async def _plans_by_range(session: AsyncSession, user_id: int, start: date, end: date) -> list[Plan]:
    result = await session.execute(
        select(Plan).where(
            and_(
                Plan.user_id == user_id,
                Plan.plan_date >= start,
                Plan.plan_date <= end,
            )
        )
    )
    return result.scalars().all()


def _stats_payload(plans: list[Plan]) -> dict:
    total = len(plans)
    done = len([p for p in plans if p.status == PlanStatus.done])
    failed = len([p for p in plans if p.status == PlanStatus.failed])
    pending = len([p for p in plans if p.status == PlanStatus.pending])
    total_score = sum(p.score_value for p in plans if p.status == PlanStatus.done)
    return {
        "total_plans": total,
        "completed_plans": done,
        "failed_plans": failed,
        "pending_plans": pending,
        "success_rate": round((done / total) * 100, 2) if total else 0,
        "total_score": total_score,
    }


@app.get("/")
async def web_ui():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.post("/api/auth/login")
async def auth_login(payload: LoginRequest, session: AsyncSession = Depends(get_db)):
    if not BOT_TOKEN or not JWT_SECRET_KEY:
        raise HTTPException(status_code=500, detail="BOT_TOKEN yoki JWT_SECRET_KEY sozlanmagan")
    tg_user = _parse_telegram_init_data(payload.init_data)
    user = await _get_or_create_user(session, tg_user)
    token = _token_for_user(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "full_name": user.full_name,
            "username": user.username,
            "streak": user.streak,
            "total_score": user.total_score,
        },
    }


@app.get("/api/user/profile")
async def user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "streak": current_user.streak,
        "total_score": current_user.total_score,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@app.get("/api/plans/today")
async def plans_today(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    plans = await _plans_by_range(session, current_user.id, today, today)
    return {"items": [_serialize_plan(p) for p in plans]}


@app.get("/api/plans/history")
async def plans_history(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Plan).where(Plan.user_id == current_user.id).order_by(Plan.plan_date.desc(), Plan.id.desc())
    )
    return {"items": [_serialize_plan(p) for p in result.scalars().all()]}


@app.post("/api/plans/create")
async def plans_create(
    payload: PlanCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = Plan(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        scheduled_time=payload.scheduled_time,
        score_value=payload.score_value,
        plan_date=payload.plan_date or datetime.now(TIMEZONE).date(),
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return _serialize_plan(plan)


@app.put("/api/plans/{plan_id}/update")
async def plans_update(
    plan_id: int,
    payload: PlanUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Plan).where(and_(Plan.id == plan_id, Plan.user_id == current_user.id)))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Reja topilmadi")

    update_data = payload.model_dump(exclude_unset=True)
    if "status" in update_data:
        try:
            plan.status = PlanStatus(update_data["status"])
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Status noto'g'ri") from exc
        update_data.pop("status")

    for key, value in update_data.items():
        setattr(plan, key, value)

    await session.commit()
    await session.refresh(plan)
    return _serialize_plan(plan)


@app.delete("/api/plans/{plan_id}")
async def plans_delete(
    plan_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Plan).where(and_(Plan.id == plan_id, Plan.user_id == current_user.id)))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Reja topilmadi")
    await session.delete(plan)
    await session.commit()
    return {"ok": True}


@app.put("/api/plans/{plan_id}/complete")
async def plans_complete(
    plan_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Plan).where(and_(Plan.id == plan_id, Plan.user_id == current_user.id)))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Reja topilmadi")

    if plan.status != PlanStatus.done:
        plan.status = PlanStatus.done
        log = ScoreLog(
            user_id=current_user.id,
            plan_id=plan.id,
            score_change=plan.score_value,
            reason=f"✅ '{plan.title}' bajarildi (WebApp)",
        )
        session.add(log)
        current_user.total_score += plan.score_value
    await session.commit()
    await session.refresh(plan)
    return _serialize_plan(plan)


@app.get("/api/statistics/daily")
async def statistics_daily(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    plans = await _plans_by_range(session, current_user.id, today, today)
    return _stats_payload(plans)


@app.get("/api/statistics/weekly")
async def statistics_weekly(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    start = today - timedelta(days=today.weekday())
    plans = await _plans_by_range(session, current_user.id, start, today)
    return _stats_payload(plans)


@app.get("/api/statistics/monthly")
async def statistics_monthly(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    start = today.replace(day=1)
    plans = await _plans_by_range(session, current_user.id, start, today)
    return _stats_payload(plans)


@app.get("/api/statistics/yearly")
async def statistics_yearly(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    start = today.replace(month=1, day=1)
    plans = await _plans_by_range(session, current_user.id, start, today)
    return _stats_payload(plans)


@app.post("/api/goals/create")
async def goals_create(
    payload: GoalCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        goal_type = GoalType(payload.goal_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="goal_type noto'g'ri") from exc

    goal = Goal(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        goal_type=goal_type,
        target_value=max(payload.target_value, 1),
        current_value=max(payload.current_value, 0),
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    goal.is_completed = goal.current_value >= goal.target_value
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return _serialize_goal(goal)


@app.get("/api/goals/list")
async def goals_list(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.id.desc()))
    return {"items": [_serialize_goal(g) for g in result.scalars().all()]}


@app.put("/api/goals/{goal_id}/update")
async def goals_update(
    goal_id: int,
    payload: GoalUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id)))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Maqsad topilmadi")

    update_data = payload.model_dump(exclude_unset=True)
    if "goal_type" in update_data and update_data["goal_type"]:
        try:
            goal.goal_type = GoalType(update_data["goal_type"])
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="goal_type noto'g'ri") from exc
        update_data.pop("goal_type")

    for key, value in update_data.items():
        setattr(goal, key, value)

    goal.target_value = max(goal.target_value, 1)
    goal.current_value = max(goal.current_value, 0)
    goal.is_completed = goal.current_value >= goal.target_value
    await session.commit()
    await session.refresh(goal)
    return _serialize_goal(goal)


@app.delete("/api/goals/{goal_id}")
async def goals_delete(
    goal_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id)))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Maqsad topilmadi")
    await session.delete(goal)
    await session.commit()
    return {"ok": True}


@app.get("/api/goals/progress")
async def goals_progress(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Goal).where(Goal.user_id == current_user.id))
    goals = result.scalars().all()
    by_type: dict[str, dict] = {}
    for goal in goals:
        key = goal.goal_type.value
        by_type.setdefault(key, {"count": 0, "completed": 0, "avg_progress": 0.0})
        by_type[key]["count"] += 1
        by_type[key]["completed"] += 1 if goal.is_completed else 0
        progress = (goal.current_value / goal.target_value) * 100 if goal.target_value else 0
        by_type[key]["avg_progress"] += progress

    for item in by_type.values():
        item["avg_progress"] = round(item["avg_progress"] / item["count"], 2) if item["count"] else 0

    return {
        "total_goals": len(goals),
        "completed_goals": len([g for g in goals if g.is_completed]),
        "by_type": by_type,
    }


@app.get("/api/reports/daily")
async def report_daily(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    plans = await _plans_by_range(session, current_user.id, today, today)
    return {"period": str(today), "statistics": _stats_payload(plans), "plans": [_serialize_plan(p) for p in plans]}


@app.get("/api/reports/weekly")
async def report_weekly(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    start = today - timedelta(days=today.weekday())
    plans = await _plans_by_range(session, current_user.id, start, today)
    return {
        "period": f"{start} - {today}",
        "statistics": _stats_payload(plans),
        "plans": [_serialize_plan(p) for p in plans],
    }


@app.get("/api/reports/monthly")
async def report_monthly(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    start = today.replace(day=1)
    plans = await _plans_by_range(session, current_user.id, start, today)
    return {
        "period": f"{start} - {today}",
        "statistics": _stats_payload(plans),
        "plans": [_serialize_plan(p) for p in plans],
    }


@app.get("/api/reports/yearly")
async def report_yearly(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(TIMEZONE).date()
    start = today.replace(month=1, day=1)
    plans = await _plans_by_range(session, current_user.id, start, today)
    return {
        "period": f"{start} - {today}",
        "statistics": _stats_payload(plans),
        "plans": [_serialize_plan(p) for p in plans],
    }
