from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database.db import Base


class GoalType(enum.Enum):
    yearly = "yearly"
    monthly = "monthly"
    weekly = "weekly"
    daily = "daily"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    goal_type = Column(Enum(GoalType), nullable=False)
    target_value = Column(Integer, default=1, nullable=False)
    current_value = Column(Integer, default=0, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
