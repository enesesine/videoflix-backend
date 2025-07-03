# Videoflix — Back‑End

A Django 5 / Django REST Framework API that powers the Videoflix streaming platform. It handles user management (token‑based auth with e‑mail verification), video catalogue endpoints and background transcoding via **Redis + RQ**/FFmpeg.

> **Goal** Expose a secure, stateless REST API to the Angular front‑end and automate heavy video tasks in the background.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Folder Structure](#folder-structure)
4. [Quick Start](#quick-start)
5. [Environment Variables](#environment-variables)
6. [Running Background Workers](#running-background-workers)
7. [API Overview](#api-overview)
8. [Testing & Coverage](#testing--coverage)
9. [Deployment Notes](#deployment-notes)
10. [License](#license)

---

## Features

- **Token authentication** (DRF) with custom `User` model (e‑mail = username).
- **Registration flow** with e‑mail confirmation and automatic token issuance.
- **Password reset**: request → mail with secure UID/token → choose new password.
- **Video catalogue**\
  `GET /api/categories/` & `GET /api/videos/` (read‑only, ordered by `created_at`).
- **Automatic transcoding**\
  On upload, a **django‑RQ task** invokes FFmpeg to render 120p/360p/720p/1080p variants.
- **Media storage** on disk (can be switched to S3 / GCS via `DEFAULT_FILE_STORAGE`).
- Swagger / ReDoc can be added via `drf‑spectacular` (optional).

---

## Tech Stack

| Layer         | Library / Service              | Purpose                               |
| ------------- | ------------------------------ | ------------------------------------- |
| Web Framework | **Django 5.2**                 | ORM, auth, admin                      |
| API           | **Django REST Framework 3.16** | Serializers, viewsets, token auth     |
| Auth helper   | **django‑rest‑authemail 2.1**  | Signup, confirm, reset via e‑mail     |
| DB            | **PostgreSQL 15**              | Relational store for users & metadata |
| Cache / RQ    | **Redis 6**                    | Task queue + cache potential          |
| Worker        | **django‑RQ 3 / rq 2.4**       | Background jobs                       |
| Transcode     | **FFmpeg** (system package)    | Render multiple resolutions           |
| Static Svc    | **Whitenoise 6**               | Serve static files in production      |

---

## Folder Structure

```
core/              ← project settings, urls, wsgi
├─ accounts/       ← custom user model & auth views
├─ videos/         ← Category & Video models, tasks, API views
└─ templates/      ← authemail e‑mail templates (HTML + txt)
```

---

## Quick Start

```bash
# 1 Clone & create venv
$ git clone https://github.com/<your-org>/videoflix-backend.git
$ cd videoflix-backend && python -m venv venv && source venv/bin/activate

# 2 Install dependencies
$ pip install -r requirements.txt

# 3 Copy example env and adjust
$ cp .env.example .env  # set DB creds, SECRET_KEY, FRONTEND_URL …

# 4 Run migrations & create superuser
$ python manage.py migrate
$ python manage.py createsuperuser

# 5 Start dev server (http://localhost:8000)
$ python manage.py runserver
```

### Optional: Docker Compose

```bash
$ docker compose up --build
```

Creates containers for **web** (gunicorn), **db** (Postgres) and **redis** (task queue) plus an **rq‑worker** service.

---

## Environment Variables

| Key                  | Default / Example                      | Notes                        |
| -------------------- | -------------------------------------- | ---------------------------- |
| `SECRET_KEY`         | *required*                             | Django secret                |
| `DB_NAME`            | `videoflix`                            | Postgres DB                  |
| `DB_USER`            | `videoflix`                            |                              |
| `DB_PASSWORD`        | `***`                                  |                              |
| `DB_HOST`            | `db` (docker) / `localhost`            |                              |
| `DB_PORT`            | `5432`                                 |                              |
| `REDIS_HOST`         | `redis`                                | Redis container hostname     |
| `FRONTEND_URL`       | `http://localhost:4200`                | Used in mail links           |
| `EMAIL_BACKEND`      | `django.core.mail.backends.console...` | Switch to SMTP in production |
| `DEFAULT_FROM_EMAIL` | `Videoflix Support <no-reply@...>`     | Sender address               |

All keys are read in `core/settings.py` via `python‑dotenv`.

---

## Running Background Workers

```bash
# with docker compose
$ docker compose exec web python manage.py rqworker default

# or locally
$ python manage.py rqworker default
```

Processes FFmpeg tasks queued by the `enqueue_transcoding` signal.

---

## API Overview

| Method | Endpoint                                 | Description               |
| ------ | ---------------------------------------- | ------------------------- |
| POST   | `/api/accounts/signup/`                  | Register; returns token   |
| POST   | `/api/accounts/login/`                   | Login; returns token      |
| POST   | `/api/accounts/password/reset/`          | Send reset mail           |
| POST   | `/api/accounts/password/reset/verified/` | Confirm new password      |
| GET    | `/api/categories/`                       | List all categories       |
| GET    | `/api/videos/`                           | List videos, newest first |

HTTP 401 if token missing / invalid. Include `Authorization: Token <token>`.

---

## Testing & Coverage

```bash
$ pip install -r requirements-dev.txt  # pytest, coverage, factory_boy …
$ pytest --cov=.
# target: ≥80 % statements
```

`pytest.ini` includes markers for unit vs integration (DB).

---

## Deployment Notes

- Use **gunicorn** + **whitenoise** for serving static files.
- Put Nginx (or Caddy) in front for TLS termination and media files.
- Set `DEBUG=0` and a strong `SECRET_KEY`.
- Configure `CACHES` with Redis for query‑level caching if desired.

---

## License

MIT © 2025 Videoflix Team

