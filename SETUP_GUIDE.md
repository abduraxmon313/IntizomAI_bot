# 🚀 Complete IntizomAI Dashboard Setup Guide

## 📋 Full Implementation Checklist

### **✅ PART 1: DATABASE MODELS**

Copy this to `bot/database/models.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    plans = relationship("Plan", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    statistics = relationship("DailyStatistics", back_populates="user", cascade="all, delete-orphan")

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    status = Column(String, default="pending")
    score_value = Column(Integer, default=5)
    scheduled_time = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    user = relationship("User", back_populates="plans")

class GoalType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    goal_type = Column(SQLEnum(GoalType), default=GoalType.MONTHLY)
    target_value = Column(Integer)
    current_value = Column(Integer, default=0)
    end_date = Column(DateTime)
    status = Column(String, default="active")
    user = relationship("User", back_populates="goals")

class DailyStatistics(Base):
    __tablename__ = "daily_statistics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    date = Column(DateTime, index=True)
    total_plans = Column(Integer, default=0)
    completed_plans = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    user = relationship("User", back_populates="statistics")
```

---

### **✅ PART 2: FASTAPI SERVER**

Create `web/main.py` with all API endpoints (bergan kodi yuqorida)

Create `web/__init__.py` (empty file)

---

### **✅ PART 3: BOT CONFIG UPDATE**

Update `bot/config.py`:

```python
import os
from dotenv import load_dotenv
import pytz

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
TIMEZONE = pytz.timezone("Asia/Tashkent")

# ✨ NEW
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-railway-domain.app")
API_URL = os.getenv("API_URL", "https://your-railway-domain.app/api")
```

---

### **✅ PART 4: BOT START HANDLER**

Create `bot/handlers/start.py`:

```python
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from bot.services.user_service import get_user_by_telegram_id
from bot.config import WEBAPP_URL

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.command("start"))
async def start_command(message: Message, state: FSMContext, session: AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📊 Dashboard",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={message.from_user.id}")
        )],
        [InlineKeyboardButton(text="➕ Reja qo'shish", callback_data="add_plan")],
        [InlineKeyboardButton(text="📋 Rejalarim", callback_data="my_plans")],
    ])
    
    await message.answer(
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        f"🧠 <b>IntizomAI - Your Second Brain</b>\n\n"
        f"Kundalik rejalarni boshqaring va statistikani ko'ring!",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.clear()
```

Add to `bot/main.py`:
```python
from bot.handlers import start
# ...
dp.include_router(start.router)
```

---

### **✅ PART 5: UPDATE BOT MAIN**

Update `bot/main.py` to include start handler va ensure database models are created

---

### **✅ PART 6: FRONTEND REACT PROJECT**

```bash
npm create vite@latest intizom-dashboard -- --template react
cd intizom-dashboard
npm install
npm install -D tailwindcss postcss autoprefixer
npm install axios react-router-dom zustand recharts lucide-react framer-motion
npx tailwindcss init -p
```

---

### **✅ PART 7: FRONTEND FILE STRUCTURE**

Yuqorida berilgan barcha React components-larni qo'ying:
- Header.jsx
- Navigation.jsx
- Dashboard.jsx
- Statistics.jsx
- Goals.jsx
- Plans.jsx
- Reports.jsx
- Settings.jsx
- ProgressBar.jsx
- useStore.js
- api.js

---

### **✅ PART 8: RAILWAY PROCFILE**

Update `Procfile`:

```
worker: python -m bot.main
web: uvicorn web.main:app --host 0.0.0.0 --port $PORT
```

---

### **✅ PART 9: BOTFATHER SETUP**

```
1. @BotFather ni oching
2. Botingizni tanlang (/mybots)
3. "Bot Settings" → "Menu Button"
4. "Configure menu button"
5. "Web App"
6. Enter URL: https://your-railway-domain.app
7. Enter label: 📊 Dashboard
```

---

### **✅ PART 10: ENVIRONMENT VARIABLES (.env)**

```
BOT_TOKEN=your_token
OPENAI_API_KEY=your_key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/intizom
WEBAPP_URL=https://your-railway-domain.app
API_URL=https://your-railway-domain.app/api
DEBUG=False
```

---

## 🚀 DEPLOYMENT STEPS

1. **Push to GitHub:**
```bash
git add .
git commit -m "Add complete dashboard + backend API"
git push
```

2. **Railway deployment:**
   - Link repository
   - Set environment variables
   - Deploy

3. **Verify:**
   - Bot /start command works
   - WebApp button shows dashboard
   - API endpoints respond
   - Charts display correctly

---

## ✨ COMPLETE FEATURES

✅ Telegram Bot (existing)
✅ AI Plan Extraction (existing)
✅ Daily Tasks Management (existing)
✅ **NEW: Web Dashboard**
✅ **NEW: Statistics (Daily/Weekly/Monthly/Yearly)**
✅ **NEW: Goals Management**
✅ **NEW: Plans History**
✅ **NEW: Reports**
✅ **NEW: Settings**
✅ **NEW: Modern Design (Dark/Light mode)**
✅ **NEW: Charts & Analytics**

---

## 🎯 ARCHITECTURE

```
┌─────────────────────────────────────────┐
│    Telegram Bot (@BotFather)            │
│  - Plans management                     │
│  - AI voice/text parsing                │
│  - Dashboard button                     │
└──────────────┬────��─────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     FastAPI Web Server (web/main.py)    │
│  - REST API endpoints                   │
│  - Statistics calculation               │
│  - Goals management                     │
│  - Authentication                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   PostgreSQL Database                   │
│  - Users, Plans, Goals, Statistics      │
└─────────────────────────────────────────┘
               
               ▼
┌─────────────────────────────────────────┐
│    React Dashboard (frontend)           │
│  - Beautiful UI                         │
│  - Charts & Analytics                   │
│  - Mobile responsive                    │
└─────────────────────────────────────────┘
```

---

## 📞 SUPPORT

**Agar errors bo'lsa:**

1. Check logs: `railway logs`
2. Database migrations: `alembic upgrade head`
3. Environment variables: verify .env file
4. Bot token: verify BotFather configuration

---

**ALL DONE! Your Second Brain is ready! 🧠✨**
