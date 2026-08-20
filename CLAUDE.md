# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FlowBill — a subscription billing API (FastAPI backend + React/Vite frontend) modeled after Stripe Billing. Backend engineering is the focus of this project; the frontend is a thin, mostly AI-generated demo UI over the API (see `README.md` for the full feature list, architecture rationale, and known limitations/production roadmap).

## Commands

**Backend (run from repo root, `.venv` already set up on Windows):**
```bash
# Run the API locally
uvicorn app.main:app --reload

# Run the full test suite
python -m pytest tests/
pytest tests/ -v

# Run a single test file
python -m pytest tests/test_billing_cycle.py

# Run a single test
python -m pytest tests/test_webhook_signature.py::test_valid_signature

# Apply DB migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Manually trigger a billing cycle (useful for debugging cycle_runner without waiting for APScheduler)
python -c "from app.billing.cycle_runner import run_billing_cycle; run_billing_cycle()"
```

Tests require a real Postgres connection (see `tests/conftest.py` — no mocked DB layer). Start Postgres via `docker-compose up db` or point `.env` at a reachable instance before running pytest. CI (`.github/workflows/ci.yml`) spins up Postgres as a service container and runs `alembic upgrade head` before `pytest tests/`.

**Frontend (run from `frontend/`):**
```bash
npm install
npm run dev       # Vite dev server, proxies /api -> VITE_API_URL (see vite.config.js)
npm run build
npm run lint
```

**Docker (full stack):**
```bash
docker-compose up --build          # app + db, local dev
docker-compose -f docker-compose.prod.yml up   # production topology
```

## Architecture

### Backend: strict three-layer pattern per domain module

Every domain under `app/` (`auth`, `customers`, `plans`, `subscriptions`, `invoices`, `line_items`, `payments`, `webhooks`, `tenant_settings`) follows:

```
router.py      → HTTP boundary. Validates input via Pydantic schemas, calls service, returns response. No business logic, no DB access.
service.py     → Business rules, validation, orchestration, raises domain exceptions. No direct SQL/ORM queries.
repository.py  → All DB interaction (SQLAlchemy 2.0 `select()` style). No business logic, no HTTP concerns.
model.py       → SQLAlchemy ORM model.
schemas.py     → Pydantic request/response models.
```

When adding a feature, follow this pattern: extend/add to `repository.py` first, then `service.py`, then wire the endpoint in `router.py`. Cross-domain operations go through the other domain's `repository` (or occasionally `service`) module directly — e.g. `customers/service.py` imports `subscriptions.repository` to cancel active subscriptions during a hard delete, and `tenant_settings.repository` to create a settings row on customer creation.

Domain exceptions (`app/core/exceptions.py`: `ResourceNotFound`, `DuplicateRecord`, `ExternalServiceError`, `PermissionDeniedError`) are raised in the service layer and translated to HTTP responses by exception handlers registered in `app/main.py` — routers should not raise `HTTPException` directly for these cases (auth's router is an exception/legacy pattern).

### Billing engine

- `app/billing/cycle_runner.py` — `run_billing_cycle()` is a plain function (not a FastAPI dependency) invoked both by APScheduler (every 24h, wired in `app/main.py`'s `lifespan`) and by the manual `POST /billing/run` endpoint (`app/billing/router.py`). It opens its own `SessionLocal()` DB session rather than using `get_db`, since it doesn't run inside a request. It finds due active subscriptions, creates invoices, charges via Stripe, generates a PDF (`app/core/pdf.py`), emails it (`app/core/email.py`), and advances the subscription period.
- `app/billing/dunning.py` — separate APScheduler job (also every 24h) for retrying failed payments.
- Both jobs share the same DB session pattern and log via the module logger, not `print`.

### Webhooks (two distinct systems — don't confuse them)

- `app/webhooks/stripe_receiver.py` — **inbound**: receives Stripe webhook events at `/stripe/webhook/`, verifies the signature via `stripe.Webhook.construct_event` using `STRIPE_WEBHOOK_SECRET`.
- `app/webhooks/router.py` / `service.py` / `repository.py` — **outbound**: customer-registered endpoints (`WebhookEndpoint`) that FlowBill delivers events to (`WebhookDelivery`), signed with HMAC-SHA256 so receivers can verify authenticity.

### Auth & rate limiting

- Stateless JWT via PyJWT (`app/core/security.py`), no server-side session store (see README's "Architectural Decisions" for the documented Redis-blacklist next step).
- SlowAPI (`app/limiter.py`) rate-limits per-route with `@limiter.limit(...)` decorators. There are two key functions: `get_remote_address` (IP-based, for unauthenticated routes like `/auth/*`) and `get_current_user_key` (JWT-subject-based, for authenticated routes) — pick the one matching the route's auth requirement when adding rate limits to a new endpoint.
- Redis backs the rate limiter's storage (`storage_uri=redis://...`), not just an optional cache.

### Single-tenant data model

Isolation key is `customer_id`, not an `organization_id`/tenant column — this is a deliberate scoping decision (see README "Architectural Decisions"), not an oversight. Don't introduce multi-tenant assumptions without discussing first.

### Config & environment

- `app/config.py`'s `Settings` (pydantic-settings) reads `.env` and is the single source of truth for required env vars — `extra="ignore"` lets `.env` carry test-only keys without breaking prod config. Any new required setting must be added here.
- `app/database.py` builds the Postgres URL from discrete `DATABASE_*` settings (not a single `DATABASE_URL`).
- `tests/conftest.py` builds its own engine/session from the same `Settings` object (real DB, transactional rollback per test via `db_session` fixture) — there is no separate test-only settings class, despite the commented-out `test_database_name` field in `config.py`.

### Frontend

Plain React + Vite (no TypeScript), Tailwind v4, React Router, Axios (`frontend/src/api/client.js`) for API calls, `AuthContext` for auth state. Structure is flat: `pages/` (one file per route), `components/{ui,layout}/`. Dev server proxies `/api` to `VITE_API_URL` (defaults to the deployed backend — set this env var to point at localhost:8000 for local full-stack dev).
