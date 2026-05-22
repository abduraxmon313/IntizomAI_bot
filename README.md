# Intizom AI Bot

Telegram bot for daily task management with AI-powered plan extraction.

## Features
- Voice and text plan input
- AI plan extraction (Whisper + GPT)
- Automatic reminders
- Daily reports
- Gamification system
- Telegram WebApp dashboard (FastAPI + React UI)

## Web Dashboard (Railway)

This repository now includes a web process:

- `worker`: Telegram bot (`python -m bot.main`)
- `web`: FastAPI app (`uvicorn web.main:app ...`)

### Railway domain qayerdan olinadi?

Railway deploy qilingandan keyin:
1. Railway project → **Service** ni oching
2. **Settings** → **Networking / Domains**
3. `*.up.railway.app` domain chiqadi (auto generated)
4. Shu domainni `WEBAPP_URL` sifatida env ga qo'ying

Example:
```env
WEBAPP_URL=https://your-service-name.up.railway.app
JWT_SECRET_KEY=strong-random-secret
```

### BotFather WebApp tugmasi

BotFather orqali:
1. `/setmenubutton`
2. Botni tanlang
3. `Web App` ni tanlang
4. Railway HTTPS URL kiriting (`WEBAPP_URL`)
5. Label: `📊 Dashboard`

Koddan ham avtomatik qo'llab-quvvatlanadi: bot startup vaqtida `WEBAPP_URL` bo'lsa chat menu tugmasi set qilinadi.

### API endpointlar

- `POST /api/auth/login` (Telegram InitData → JWT)
- `GET /api/user/profile`
- `GET /api/plans/today`
- `GET /api/plans/history`
- `POST /api/plans/create`
- `PUT /api/plans/{id}/update`
- `DELETE /api/plans/{id}`
- `PUT /api/plans/{id}/complete`
- `GET /api/statistics/daily|weekly|monthly|yearly`
- `POST /api/goals/create`
- `GET /api/goals/list`
- `PUT /api/goals/{id}/update`
- `DELETE /api/goals/{id}`
- `GET /api/goals/progress`
- `GET /api/reports/daily|weekly|monthly|yearly`
