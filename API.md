# API Documentation

## Authentication
- `POST /api/auth/login` - Telegram `init_data` orqali JWT olish

## User
- `GET /api/user/profile`

## Plans
- `GET /api/plans/today`
- `GET /api/plans/history`
- `POST /api/plans/create`
- `PUT /api/plans/{plan_id}/update`
- `DELETE /api/plans/{plan_id}`
- `PUT /api/plans/{plan_id}/complete`

## Statistics
- `GET /api/statistics/daily`
- `GET /api/statistics/weekly`
- `GET /api/statistics/monthly`
- `GET /api/statistics/yearly`

## Goals
- `POST /api/goals/create`
- `GET /api/goals/list`
- `PUT /api/goals/{goal_id}/update`
- `DELETE /api/goals/{goal_id}`
- `GET /api/goals/progress`

## Reports
- `GET /api/reports/daily`
- `GET /api/reports/weekly`
- `GET /api/reports/monthly`
- `GET /api/reports/yearly`

## Service
- `GET /health`
