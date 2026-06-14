# FlowBill — Subscription Billing Engine

A production-grade subscription billing API modeled after Stripe Billing. Built to demonstrate backend engineering depth: automated billing cycles, dunning logic, webhook delivery with HMAC signatures, per-customer branding, and PDF invoice generation — all wired to a live cloud deployment.

**Live Demo:** [http://52.3.232.204:3000](http://52.3.232.204:3000) · **API Docs:** [http://52.3.232.204:8001/docs](http://52.3.232.204:8001/docs)
**Demo credentials:** `paul@flowbill.com` / `SecurePass123!`

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic, Pydantic v2, PyJWT |
| **Database** | PostgreSQL (AWS RDS) |
| **Infrastructure** | AWS EC2, Docker, Nginx, GitHub Actions CI |
| **Integrations** | Stripe, Resend (email), Sentry, Redis, APScheduler |
| **Frontend** | React 18 + Vite *(AI-generated — see note below)* |
| **Testing** | pytest + httpx — 17 tests passing |

---

## Features

- **Subscription lifecycle** — create, pause, cancel, and upgrade subscriptions with full state management
- **Automated billing engine** — APScheduler runs every 24 hours, invoices all due subscriptions automatically
- **Dunning engine** — automatic payment retry on failed charges with configurable backoff
- **Stripe payment processing** — charge customers and reconcile payment state via webhooks
- **PDF invoice generation** — per-customer branded invoices with logo, brand colors, and address (ReportLab)
- **Invoice email delivery** — send invoices directly to customers via Resend
- **Webhook system** — outbound webhooks with HMAC-SHA256 request signing and test delivery endpoint
- **Rate limiting** — SlowAPI + Redis, 5 requests/minute per endpoint
- **JWT authentication** — stateless auth with secure token issuance and validation
- **Per-customer branding** — each customer can upload a logo, set brand colors, and configure a billing address
- **Full test suite** — 17 passing tests covering auth, customers, plans, subscriptions, invoices, and billing cycle

---

## Architecture

Every module follows a strict three-layer pattern:

```
Router  →  Service  →  Repository
```

- **Router** — HTTP boundary. Validates input, calls the service, returns the response. No business logic.
- **Service** — Business rules, validation, orchestration. No direct DB queries.
- **Repository** — All database interaction. Pure SQLAlchemy. No business logic.

This separation makes every layer independently testable and swappable. A new data source means only the repository changes. A new API protocol means only the router changes.

```
app/
├── auth/           # JWT issuance, OAuth2 password flow
├── billing/        # Cycle runner, dunning engine, APScheduler setup
├── customers/      # Customer CRUD
├── invoices/       # Invoice lifecycle, PDF generation, email send
├── line_items/     # Per-invoice line items
├── payments/       # Payment attempt tracking
├── plans/          # Billing plan definitions
├── subscriptions/  # Subscription state machine
├── tenant_settings/# Per-customer logo, brand colors, address
├── webhooks/       # Endpoint registration, HMAC delivery, test trigger
└── core/           # Email, PDF, security, exceptions, enums
```

---

## Live Demo Flow

1. **Log in** at [http://52.3.232.204:3000](http://52.3.232.204:3000) with `paul@flowbill.com` / `SecurePass123!`
2. **Create a customer** — Customers → New Customer
3. **Create a billing plan** — Plans → New Plan (set price and interval)
4. **Create a subscription** — attach the customer to the plan
5. **Run a billing cycle** — Dashboard → Run Billing Cycle (manually triggers the scheduler)
6. **View the invoice** — Invoices → open the generated invoice, download the PDF, or send via email
7. **Register a webhook** — Webhooks → register an endpoint URL, then use Test Delivery to fire a live request
8. **Check branding** — Settings → upload a logo and set brand colors; regenerate the PDF to see it applied

---

## API Endpoints

| Group | Base Path | Description |
|---|---|---|
| Auth | `POST /auth/register`, `/auth/login` | Register users, issue JWT tokens |
| Customers | `GET/POST/PATCH/DELETE /customers` | Full customer CRUD |
| Plans | `GET/POST/PATCH/DELETE /plans` | Billing plan management |
| Subscriptions | `GET/POST/PATCH/DELETE /subscriptions` | Subscription lifecycle |
| Invoices | `GET/POST/PATCH /invoices` | Invoice management, PDF, email send |
| Line Items | `GET/POST/PATCH /line-items` | Per-invoice line item detail |
| Payments | `GET /payments/invoice/{id}` | Payment attempt history |
| Billing | `POST /billing/run` | Manually trigger a billing cycle |
| Webhooks | `GET/POST/PATCH/DELETE /webhooks`, `POST /webhooks/{id}/deliver` | Endpoint registration and test delivery |
| Tenant Settings | `GET/PUT /tenant-settings/{customer_id}` | Logo, brand colors, billing address |

Full interactive docs at [http://52.3.232.204:8001/docs](http://52.3.232.204:8001/docs).

---

## Architectural Decisions

**Single-tenant by design.**
The current schema uses `customer_id` as the top-level isolation key. The production path to full multi-tenancy is adding an `organization_id` column to all tables and enforcing it at the Row Level Security layer — a migration, not a rewrite.

**Stateless JWT.**
Tokens are validated cryptographically with no server-side session store. The documented next step is a Redis-backed token blacklist for immediate revocation on logout or compromise — the Redis connection is already configured in the environment.

**Scheduler-driven billing.**
APScheduler runs inside the FastAPI process and fires every 24 hours. The `POST /billing/run` endpoint lets you trigger it manually for demos. The production path is an external job queue (Celery + Redis or AWS EventBridge) to decouple billing from the API process and support retries with backoff.

---

## Note on the Frontend

The React/Vite frontend was generated entirely using **Claude Code** as a deliberate exercise in AI-driven, context-driven development.

The author's focus is backend engineering. The frontend exists to make the API visually navigable for demo purposes — it is not the primary artifact of this project.

This reflects a real-world augmented workflow: backend engineers can use AI to scaffold functional UIs quickly, stay in their domain, and ship something demonstrable without context-switching into frontend engineering.

---

## Known Limitations & Production Roadmap

| Limitation | Production Path |
|---|---|
| Single-tenant schema | Add `organization_id` to all tables; enforce via RLS |
| No token revocation | Redis blacklist on `POST /auth/logout` |
| Logo not rendered in PDF | Pass `customer_settings.logo_url` into ReportLab canvas |
| Plans with active subscribers cannot be hard-deleted | Add subscriber count guard in `deactivate_plan` service |
| Billing runs in-process | Move to Celery + Redis or AWS EventBridge |
| No idempotency keys | Add `idempotency_key` column to invoices to prevent duplicate billing on retry |

---

## Local Development

```bash
# Clone and enter the project
git clone https://github.com/CampsPA/Flowbill.git
cd Flowbill

# Copy and fill environment variables
cp .env.example .env.local

# Start the backend
docker-compose up --build

# Start the frontend
cd frontend
npm install
npm run dev
```

The backend runs on `http://localhost:8001`. The frontend proxies `/api/` to the backend via Vite's dev server config.
