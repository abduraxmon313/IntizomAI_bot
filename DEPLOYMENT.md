# Deployment Guide

## Railway (single app: worker + web)

1. Set start commands via `Procfile`:
   - `worker: python -m bot.main`
   - `web: uvicorn web.main:app --host 0.0.0.0 --port ${PORT:-8000}`
2. Configure environment variables:
   - `BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`
   - `WEBAPP_URL` (Railway HTTPS domain)
   - `JWT_SECRET_KEY`
3. On deploy, bot creates DB tables automatically via `create_tables()`.
4. Optional frontend build:
   - `cd frontend && npm install && npm run build`
   - built assets are served from `frontend/dist` by `web/main.py`.

## Health check

- `GET /health` should return `{ "status": "ok" }`.
