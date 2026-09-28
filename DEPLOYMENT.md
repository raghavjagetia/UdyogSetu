# Deploying to Render

The repo includes a `render.yaml` Blueprint that provisions both services in
one go. The only fiddly part is that the two services need to know each
other's URL, and Render only assigns those URLs once each service is created
— so there's a one-time "wire them together" step after the first deploy.

## 1. Push these changes

Render deploys from your GitHub repo, so these config changes
(`render.yaml`, the configurable CORS origin, the configurable frontend API
URL) need to be pushed before Render can use them.

## 2. Create the Blueprint on Render

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint**.
2. Connect your GitHub account and select the `raghavjagetia/UdyogSetu` repo.
3. Render reads `render.yaml` and proposes two services:
   - **udyogsetu-api** — Python web service (FastAPI backend)
   - **udyogsetu-web** — Static site (React frontend)
4. Click **Apply**. Both services deploy for the first time.

If either service name is already taken by someone else on Render, it'll ask
you to rename it — if you do, update the URLs in step 3 to match.

## 3. Wire the two services together (one-time)

`render.yaml` guesses the URLs will be `https://udyogsetu-api.onrender.com`
and `https://udyogsetu-web.onrender.com`. Once both services exist, confirm
the actual URLs on their dashboard pages, then:

- **On `udyogsetu-api`** → Environment → set `UDYOGSETU_ALLOWED_ORIGINS` to
  the frontend's real URL (e.g. `https://udyogsetu-web.onrender.com`).
- **On `udyogsetu-web`** → Environment → set `VITE_API_BASE_URL` to the
  backend's real URL + `/api` (e.g. `https://udyogsetu-api.onrender.com/api`).
- Trigger **Manual Deploy → Deploy latest commit** on whichever service you
  changed the env vars for (env var changes on a static site require a
  rebuild, since Vite bakes them in at build time).

If the guessed URLs in `render.yaml` already happened to be correct (likely,
since those names are unused), you can skip this step.

## 4. Verify

- Backend health check: `https://<your-api-url>/api/health` → `{"status":"ok"}`
- Open the frontend URL, log in with a demo account (see `DEMO_ACCOUNTS.md`),
  and confirm requests succeed (no CORS errors in the browser console).

## Known limitation: SQLite on Render's free tier

The backend uses a local SQLite file (`backend/udyogsetu.db`), matching this
project's zero-config, single-file philosophy. Render's **free** web service
plan has an ephemeral filesystem — the database resets whenever the service
restarts or redeploys (including the free tier's automatic spin-down after
15 minutes of inactivity).

This is *mostly* fine for a demo: `seed_data.py` re-seeds the rules library,
schemes, all demo accounts, and 20 sample applications automatically on every
startup, so dashboards are never empty — you just lose any applications or
documents you created yourself since the last restart.

If you want data to actually persist between restarts, you have two options:
1. **Add a Render Disk** (requires upgrading `udyogsetu-api` off the free
   plan) mounted at the backend's working directory, so the `.db` file and
   `uploads/` survive restarts.
2. **Migrate to a managed Postgres** — Render offers a free Postgres
   instance; point `UDYOGSETU_DATABASE_URL` at it and the app's SQLAlchemy
   setup will use it as-is (no code changes needed beyond installing
   `psycopg2-binary`).

Neither is required to get a working demo live — just something to know
going in.
