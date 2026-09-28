# Demo Login Accounts

Every account below uses the same password: **`password123`**

All of these accounts, plus 20 sample applications (approved / rejected /
under review / submitted, with some overdue items), are created automatically
by `seed_data.py` on startup whenever the database is empty — locally and on
Render. Deleting `backend/udyogsetu.db` and restarting resets to that state.

## Core accounts

| Role | Email | Notes |
|---|---|---|
| Entrepreneur | `entrepreneur@demo.com` | Owns all the demo applications |
| Admin | `admin@demo.com` | Full analytics dashboard, Rules Engine, Schemes |

## Department officers

Each officer can only review checklist items for **their own department**
(that's how the review-queue scoping works). One login per department:

| Department | Email |
|---|---|
| Maharashtra Pollution Control Board | `officer@demo.com` |
| Directorate of Industrial Safety & Health | `dish.officer@demo.com` |
| Maharashtra Fire Services | `fire.officer@demo.com` |
| Food Safety Department | `fssai.officer@demo.com` |
| GST Department | `gst.officer@demo.com` |
| Ministry of MSME | `msme.officer@demo.com` |
| Labour Department | `labour.officer@demo.com` |
| Municipal Corporation / Gram Panchayat | `municipal.officer@demo.com` |
| Municipal Corporation (Trade License) | `trade.officer@demo.com` |
| MSEDCL | `msedcl.officer@demo.com` |
| Legal Metrology Department | `metrology.officer@demo.com` |
| SEIAA Maharashtra | `seiaa.officer@demo.com` |

Departments with no officer above (e.g. Directorate of Steam Boilers,
Software Technology Parks of India) only ever generate **optional**
checklist items, so nothing is blocked on them — sign in as `admin@demo.com`
to view or act on anything platform-wide instead.

## For day-to-day use

In practice you'll mostly want just three tabs open:
- `entrepreneur@demo.com` — file applications, upload documents
- `officer@demo.com` — review MPCB items (the most active department in the seed data)
- `admin@demo.com` — see the full analytics picture

The rest are there so every department in the Rules Engine has *someone*
who can approve/reject its items, in case you want to exercise a specific
department's queue.
