# KasbLink — Service Marketplace API

<div align="center">

**A production-grade REST API for a freelance service marketplace.**  
Clients discover and hire verified workers. Built with Django REST Framework.

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-green?logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.x-red)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.x-red?logo=redis)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.x-green?logo=celery)](https://docs.celeryq.dev)
[![Tests](https://img.shields.io/badge/Tests-21%20passing-brightgreen)](https://github.com/asilbekusmonov-gh/KasbLinkUz)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🌐 Live Demo

| | URL |
|---|---|
| API Base | https://kasblinkuz-production.up.railway.app |
| Swagger Docs | https://kasblinkuz-production.up.railway.app/api/schema/swagger-ui/ |
| Admin Panel | https://kasblinkuz-production.up.railway.app/admin/ |

---

## What is KasbLink?

KasbLink is a service marketplace platform — similar to Fiverr or Upwork — built for the Central Asian market. Workers list their services (design, development, translation, repair, etc.), clients browse and place orders, communicate via chat, and leave reviews after completion.

This repository is the **backend API only**. Designed to be consumed by any frontend (React, Next.js, or mobile app).

---

## Features

### Core
- JWT authentication — register, login, token refresh
- Role-based access control — `client`, `worker`, `admin`
- Worker profiles with portfolio showcase
- Service listings with category filtering, full-text search, and ordering
- Order lifecycle — `pending → accepted → completed / cancelled`
- Messaging system between order participants
- Star ratings and reviews (only on completed orders)
- Favourites / wishlist for services
- City & district based worker discovery
- Auto-calculated worker rating and completed orders count via signals

### Background Tasks (Celery + Redis)
- Welcome email on registration
- Email notification when order is placed
- Email notification when order is accepted
- Email notification when order is completed
- Email notification when order is cancelled
- New message email notification

### API & Developer Experience
- RESTful API with versioning (`/api/v1/`)
- Auto-generated Swagger / ReDoc documentation
- Filtering, searching, and ordering on all list endpoints
- Pagination on all list responses
- Detailed validation error messages

### Security
- JWT with short-lived access tokens and refresh rotation
- Object-level permissions — users only access their own data
- Role-level permissions on every endpoint
- Passwords hashed with Django's PBKDF2 algorithm
- Sensitive fields stripped from all responses
- `HiddenField` used for user injection — clients cannot fake ownership

### Validations
- Cannot order your own service
- Cannot order an inactive service
- Cannot review an uncompleted order
- Cannot review the same order twice
- Cannot favourite the same service twice
- Cannot create duplicate worker profile
- Cannot send message to a conversation you don't belong to
- Cannot cancel a completed order

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5, Django REST Framework |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Background Tasks | Celery 5 + django-celery-results |
| Auth | JWT via `djangorestframework-simplejwt` |
| API Docs | `drf-spectacular` (Swagger + ReDoc) |
| Filtering | `django-filter` |
| Testing | pytest + pytest-django (21 tests) |
| Deployment | Railway |

---

## Architecture

```
kasblink/
├── apps/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── users.py        # User, WorkerProfile, Portfolio
│   │   ├── categories.py   # Category, Service
│   │   ├── orders.py       # Order, OrderImage, Review, Favourite
│   │   └── chats.py        # Conversation, Message
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py        # Register, login tests
│   │   ├── test_permissions.py # Role-based access tests
│   │   └── test_orders.py      # Full order lifecycle tests
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── signals.py          # Auto-update worker rating & order count
│   ├── filters.py
│   └── tasks.py            # Celery background tasks
├── root/
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
└── manage.py
```

### Key Design Decisions

**Single app, models package** — All models live in one Django app split across files by domain. Chosen over multiple apps to reduce boilerplate for a single-developer project at this scale.

**Role-based permissions** — Three custom DRF permission classes (`IsWorker`, `IsClient`, `IsOwner`) applied at the viewset level. Public endpoints use `AllowAny`, all mutation endpoints require authentication and role verification.

**Filtered querysets** — Every viewset overrides `get_queryset()` using `super().get_queryset()` pattern to return only data belonging to the authenticated user. No user can access another user's orders, conversations, or portfolio items.

**Mixin-based viewsets** — Instead of `ModelViewSet` everywhere, each viewset explicitly declares only the actions it needs, preventing unintended endpoints from being exposed.

**Async email notifications** — All emails are sent via Celery background tasks. The HTTP response returns instantly without waiting for email delivery.

**HiddenField for user injection** — User fields are automatically set from `request.user` via `HiddenField(default=CurrentUserDefault())`. Clients cannot fake ownership of resources.

**Signals for auto-calculated fields** — Worker `rating` and `completed_orders_count` are automatically updated via Django signals when orders complete and reviews are created.

---

## Testing

```bash
pytest
```

```
21 tests passing across 3 test files:

tests/test_auth.py        — register, login, token validation
tests/test_permissions.py — role-based access control (8 tests)
tests/test_orders.py      — full order lifecycle (9 tests)
```

Tests use `reverse()` for URL resolution and `status.HTTP_*` constants for clean, maintainable assertions.

---

## API Docs

| Format | URL |
|---|---|
| Swagger UI (Live) | https://kasblinkuz-production.up.railway.app/api/schema/swagger-ui/ |
| Swagger UI (Local) | http://localhost:8000/api/schema/swagger-ui/ |
| ReDoc (Local) | http://localhost:8000/api/schema/redoc/ |

---

## Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/asilbekusmonov-gh/KasbLinkUz.git
cd KasbLinkUz
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://postgres:password@localhost:5432/kasblink
```

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Start Redis

```bash
sudo systemctl start redis
redis-cli ping   # should return PONG
```

### 8. Run the server

```bash
# Terminal 1 — Django
python manage.py runserver

# Terminal 2 — Celery worker
celery -A root worker --loglevel=info
```

API running at `http://localhost:8000`  
Admin panel at `http://localhost:8000/admin/`  
API docs at `http://localhost:8000/api/schema/swagger-ui/`

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register/` | Register — returns access + refresh tokens |
| POST | `/api/v1/auth/login/` | Login — returns access + refresh tokens |
| POST | `/api/v1/auth/refresh/` | Get new access token |

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/users/me/` | ✅ | Get current user |
| PATCH | `/api/v1/users/{id}/` | ✅ Owner | Update profile |

### Workers

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/worker-profiles/` | ❌ | List all workers |
| GET | `/api/v1/worker-profiles/{id}/` | ❌ | Worker detail |
| POST | `/api/v1/worker-profiles/` | ✅ Worker | Create profile |
| PATCH | `/api/v1/worker-profiles/{id}/` | ✅ Owner | Update profile |
| GET | `/api/v1/portfolio/` | ✅ | My portfolio items |
| POST | `/api/v1/portfolio/` | ✅ Worker | Add portfolio item |
| DELETE | `/api/v1/portfolio/{id}/` | ✅ Owner | Remove portfolio item |

### Services

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/services/` | ❌ | Browse all services |
| GET | `/api/v1/services/{id}/` | ❌ | Service detail |
| POST | `/api/v1/services/` | ✅ Worker | Create service |
| PATCH | `/api/v1/services/{id}/` | ✅ Owner | Update service |
| DELETE | `/api/v1/services/{id}/` | ✅ Owner | Delete service |

### Orders

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/orders/` | ✅ | My orders |
| POST | `/api/v1/orders/` | ✅ Client | Place order |
| PATCH | `/api/v1/orders/{id}/accepted/` | ✅ Worker | Accept order |
| PATCH | `/api/v1/orders/{id}/completed/` | ✅ Worker | Complete order |
| PATCH | `/api/v1/orders/{id}/cancelled/` | ✅ Client | Cancel order |

### Conversations & Messages

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/conversations/` | ✅ | My conversations |
| GET | `/api/v1/conversations/{id}/` | ✅ | Conversation detail |
| GET | `/api/v1/messages/` | ✅ | My messages |
| POST | `/api/v1/messages/` | ✅ | Send message |

### Reviews

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/reviews/` | ✅ | My reviews |
| POST | `/api/v1/reviews/` | ✅ Client | Leave review |

### Favourites

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/favourites/` | ✅ | My saved services |
| POST | `/api/v1/favourites/` | ✅ | Save service |
| DELETE | `/api/v1/favourites/{id}/` | ✅ | Remove from favourites |

### Categories

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/categories/` | ❌ | List categories |
| GET | `/api/v1/categories/{id}/` | ❌ | Category detail |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DEBUG` | ✅ | `True` for dev, `False` for production |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `ALLOWED_HOSTS` | ✅ | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | ✅ | Frontend origin URLs |

See `.env.example` for full template.

---

## Roadmap

- [x] Models — User, WorkerProfile, Portfolio, Category, Service, Order, Chat, Review, Favourite
- [x] JWT Authentication — register, login, token refresh
- [x] Role-based permissions — IsWorker, IsClient, IsOwner
- [x] Serializer validations — business rules enforced at API layer
- [x] Filter, search, and ordering on all list endpoints
- [x] Swagger / ReDoc API documentation
- [x] Celery + Redis — async background tasks
- [x] Email notifications — order lifecycle + welcome email
- [x] File uploads — portfolio images, service cover, profile image
- [x] Django signals — auto-update worker rating and order count
- [x] Deployed to Railway — live URL
- [x] Tests with pytest — 21 tests passing
- [ ] Docker + Docker Compose
- [ ] GitHub Actions CI/CD
- [ ] Real-time chat — Django Channels + WebSocket
- [ ] Payment integration — Payme, Click

---

## License

[MIT](LICENSE)

---

<div align="center">
  Built by <a href="https://github.com/asilbekusmonov-gh">Asilbek Usmonov</a> · Tashkent, Uzbekistan
</div>