from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from datetime import datetime, timezone
from database.db import Base


class DailyStatistics(Base):
    __tablename__ = "daily_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stat_date = Column(Date, nullable=False, index=True)
    total_plans = Column(Integer, default=0)
    completed_plans = Column(Integer, default=0)
    failed_plans = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class WeeklyStatistics(Base):
    __tablename__ = "weekly_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    week_start = Column(Date, nullable=False, index=True)
    total_plans = Column(Integer, default=0)
    completed_plans = Column(Integer, default=0)
    failed_plans = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MonthlyStatistics(Base):
    __tablename__ = "monthly_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    month_start = Column(Date, nullable=False, index=True)
    total_plans = Column(Integer, default=0)
    completed_plans = Column(Integer, default=0)
    failed_plans = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
