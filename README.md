# Kanban Board — Backend

Django REST Framework backend for a Kanban task manager + image annotation tool.

## Tech Stack

Python 3.13 · Django 6.0 · Django REST Framework · SimpleJWT · SQLite · drf-yasg (Swagger/Redoc) · django-cors-headers

## Key Features

- **Auth:** Email + password login (no username), JWT access/refresh tokens
- **Class-based views:** Generic APIViews (`accounts`) + `ModelViewSet` + routers (`tasks`, `annotations`)
- **Global error handling:** Centralized exception handler — every error (validation, 404, auth, unhandled) returns one consistent JSON shape
- **Rate limiting:** Throttling on anonymous and authenticated requests
- **Pagination:** Default DRF pagination enabled globally in `settings.py` — all list endpoints (`/api/tasks/`, `/api/images/`, `/api/tags/`, etc.) return paginated responses (`count`, `next`, `previous`, `results`)
- **Django Admin:** Full CRUD on all models for manual inspection
- **API Docs:** Swagger UI (`/swagger/`) and Redoc (`/redoc/`)
- **Postman:** Ready-to-import collection + environment in `/postman`
- **ERD:** Database schema diagram added in `/docs` folder (drawn manually and exported as an image)

## Project Structure

| App           | Responsibility                                   |
| ------------- | ------------------------------------------------ |
| `accounts`    | Custom email-based user, registration, JWT login |
| `tasks`       | Kanban tasks, tags, drag-and-drop ordering       |
| `annotations` | Image upload, polygon annotations                |

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Runs at `http://127.0.0.1:8000`. Move `SECRET_KEY` to an environment variable before deploying.

## API Overview

All authenticated endpoints require `Authorization: Bearer <access_token>`.

| Endpoint                          | Methods                 | Notes                                                     |
| --------------------------------- | ----------------------- | --------------------------------------------------------- |
| `/api/auth/register/`             | POST                    | No auth                                                   |
| `/api/auth/login/`                | POST                    | Returns access + refresh tokens                           |
| `/api/auth/login/refresh/`        | POST                    | Rotates refresh token                                     |
| `/api/auth/me/`                   | GET                     | Current user profile                                      |
| `/api/tasks/`                     | GET, POST               | Paginated · `?due_date=YYYY-MM-DD` filter                 |
| `/api/tasks/{id}/`                | GET, PUT, PATCH, DELETE |                                                           |
| `/api/tasks/{id}/reorder/`        | PATCH                   | Drag-and-drop status/order update                         |
| `/api/tags/`                      | GET                     | Paginated · read-only, created implicitly via task `tags` |
| `/api/images/`                    | GET, POST               | Paginated · POST is `multipart/form-data`                 |
| `/api/images/{id}/`               | GET, PATCH, DELETE      | PATCH used for slider reordering                          |
| `/api/annotations/`               | GET, POST               | Paginated · `points`: list of `{x, y}`, min 3             |
| `/api/annotations/{id}/`          | GET, PATCH, DELETE      | Deletes one polygon, image untouched                      |
| `/swagger/`, `/redoc/`, `/admin/` | GET                     | Docs & admin panel                                        |
