# UdyogSetu

Single-window platform for industrial approvals, compliance tracking, and access
to government support services for entrepreneurs — built for **Smart India Hackathon 2026**,
Problem Statement 26130 (Maharashtra State Innovation Society).

This is a working MVP of the pitch in `KO_KRAKENS_26130_UdyogSetu.pdf`: a rules-as-code
checklist engine, an SLA-tracked application workflow, and role-based dashboards for
Entrepreneurs, Department Officers, and Admins.

## What's implemented

- **Rules-as-code checklist engine** — a library of approvals mapped by sector /
  location / unit size (modeled on Maharashtra's MAITRI single-window landscape:
  MPCB consents, Factory License, Fire NOC, FSSAI, Udyam, GST, etc). Filing a new
  application automatically generates the applicable checklist with clause
  references and per-item SLA due dates.
- **Application tracker** — entrepreneurs upload documents per checklist item;
  department officers approve/reject with remarks; application status rolls up
  automatically.
- **Role-based dashboards** — Entrepreneur (my applications + SLA countdowns),
  Department Officer (department review queue), Admin (state-wide analytics,
  CSV export, rules & schemes management).
- **JWT authentication** with three roles: `entrepreneur`, `officer`, `admin`.
- **Schemes directory** — government incentive schemes, sector-tagged.

Deliberately out of scope for this MVP (see the pitch's roadmap): NLP document
parsing, risk-based scrutiny, live MAITRI/NSWS/department-ERP integrations, and
the Flutter mobile app. The architecture (a rules engine sitting behind a REST
API) is built so those can be added without a rewrite.

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, SQLite, JWT auth (python-jose + passlib)
- **Frontend:** React 19 + TypeScript, Vite, Tailwind CSS v4, React Router, Recharts, Axios

(The original pitch names a JSON file store for the MVP; this build uses SQLite
instead — same zero-config, single-file simplicity, but with real relational
integrity and concurrent-write safety, which a hand-rolled JSON store doesn't
give you for free.)

## Running it locally

### Backend

```bash
cd backend
py -3 -m venv venv          # or: python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8001
```

The first run creates `backend/udyogsetu.db` and seeds it with the rules
library, sample schemes, and three demo accounts (password `password123`):

| Role | Email |
|---|---|
| Entrepreneur | `entrepreneur@demo.com` |
| Department Officer (MPCB) | `officer@demo.com` |
| Admin | `admin@demo.com` |

The current local database also has extra department-officer accounts and
sample applications seeded on top of that for demoing the dashboards — see
[DEMO_ACCOUNTS.md](DEMO_ACCOUNTS.md) for the full list of logins.

API docs: http://127.0.0.1:8001/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the dev server proxies `/api` to `http://127.0.0.1:8001`.

## Project structure

```
backend/
  app/
    main.py            FastAPI app, CORS, startup seed
    models.py           SQLAlchemy models
    schemas.py           Pydantic request/response models
    auth.py               JWT + password hashing
    rules_engine/engine.py  Checklist generation (sector/location/size matching)
    seed_data.py         Demo users, rules library, schemes
    routers/
      auth.py application.py rules.py schemes.py dashboard.py
frontend/
  src/
    api/                 Axios client + TS types
    context/AuthContext.tsx
    components/           Navbar, StatusBadge, SlaBadge, StatCard, ProtectedLayout
    pages/
      LoginPage, RegisterPage, DashboardPage, SchemesPage, ApplicationDetailPage
      entrepreneur/  EntrepreneurDashboard, NewApplicationPage
      officer/       OfficerDashboard
      admin/         AdminDashboard, RulesManager
```

## Extending the rules library

Every approval requirement is a row in the `rules` table (sector, location,
minimum unit size, approval name, department, clause reference, SLA days). Admins
can add/edit/deactivate rules from **Rules Engine** in the app — no code changes
needed to add a new approval or department mapping.
