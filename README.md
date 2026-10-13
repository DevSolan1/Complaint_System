# Complaint Management System

A Django 5 web application for submitting, tracking, and resolving customer
complaints, with role-based access for Customers, Support Agents, and Managers.

## Features

- Role-based accounts (Customer / Agent / Manager) on a custom `User` model
- Complaint submission with category, priority, description, and a file attachment
- Auto-generated reference numbers (`COMP-2026-00001`, reset yearly)
- Full status lifecycle (Open → In Progress → Pending → Resolved / Closed / Rejected)
  with a tracked status-change history
- Assignment of complaints to agents (manager-only)
- Threaded comments, with internal notes visible only to staff
- Console (dev) or SMTP (prod) email notifications on submission, status change,
  comment, and assignment
- Search & filter by status, category, priority, assignee, date range, or keyword
- Role-specific dashboards, including a manager analytics view (counts, average
  resolution time, breakdown by category/priority)
- Fully customized Django admin (inline comments, status history, attachments)
- A minimal read-only REST API (Django REST Framework) scoped to the requester's role
- Unit tests for models, permissions, and views

## Tech stack

Django 5.x · Django Templates + Bootstrap 5 · SQLite (dev) / PostgreSQL-ready (prod) ·
Django REST Framework (optional API) · Python 3.12+

## Project layout

```
complaint_system/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                # project settings, root urls, wsgi/asgi
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── accounts/               # custom User model, auth views, role decorators
├── complaints/              # Category/Complaint/Comment/StatusHistory models,
│                             # views, forms, admin, signals (email), DRF API
├── dashboard/               # role-based dashboard views
├── templates/               # shared + per-app templates
└── static/css/style.css
```

## Setup

1. **Clone/unzip the project and enter it:**

   ```bash
   cd complaint_system
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env and set DJANGO_SECRET_KEY to a long random string.
   ```

4. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

   The project defaults to `config.settings.development` (SQLite, console
   email backend, `DEBUG=True`). To target production settings instead, set
   `DJANGO_SETTINGS_MODULE=config.settings.production` and provide a
   `DATABASE_URL` in `.env`.

5. **Load sample data (categories + demo accounts):**

   ```bash
   python manage.py loaddata categories demo_users
   ```

   Demo accounts (all use password `DemoPass123!`):

   | Username    | Role     |
   |-------------|----------|
   | `admin`     | Manager (superuser) |
   | `manager1`  | Manager  |
   | `agent1`    | Agent    |
   | `agent2`    | Agent    |
   | `customer1` | Customer |
   | `customer2` | Customer |

   Alternatively, create your own superuser with `python manage.py createsuperuser`.

6. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/`.

7. **Run the test suite:**

   ```bash
   python manage.py test
   ```

## Key URLs

| Path | Purpose |
|---|---|
| `/` | Landing page |
| `/accounts/register/` | Customer self-registration |
| `/accounts/login/`, `/accounts/logout/` | Authentication |
| `/dashboard/` | Role-based dashboard |
| `/complaints/` | List complaints (scoped to the logged-in user's role) |
| `/complaints/new/` | Submit a new complaint (customers) |
| `/complaints/<ref_number>/` | Complaint detail, comments, and timeline |
| `/complaints/<ref_number>/update/` | Update status/assignment (agents & managers only) |
| `/admin/` | Django admin |
| `/api/complaints/` | Read-only JSON API (session-authenticated, role-scoped) |

## Access control summary

- **Customers** can only see and comment on their own complaints.
- **Agents** can only see complaints assigned to them, and can only update
  complaints assigned to them.
- **Managers** (and superusers) can see, assign, and update all complaints.
- Attempting to view/update a complaint outside these rules returns `403 Forbidden`.
- File uploads are validated for both extension (`.pdf .png .jpg .jpeg .doc .docx`)
  and size (5MB max) — see `complaints/utils.py`.

## Notes on production readiness

- `config/settings/production.py` expects `DATABASE_URL` (e.g. Postgres via
  `postgres://user:pass@host:5432/dbname`) and enables HTTPS-related security
  settings (HSTS, secure cookies, SSL redirect).
- Static files are served via WhiteNoise; run `python manage.py collectstatic`
  before deploying.
- Swap `DJANGO_EMAIL_BACKEND` to an SMTP backend and fill in the `DJANGO_EMAIL_*`
  variables to send real emails.
- The DRF API currently exposes only read access; extend `complaints/api_views.py`
  and `serializers.py` if you need write endpoints.

## Extending

- Auto-assignment by category: hook into the `Complaint` `post_save` signal in
  `complaints/signals.py`, or add logic to `complaint_create` in `complaints/views.py`.
- Charts: `dashboard/views.py` already aggregates the data (`by_category`,
  `by_priority`, `avg_resolution`); swap the simple list rendering in
  `templates/dashboard/manager_dashboard.html` for a JS charting library if desired.
