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

### Validations
- Cannot order your own service
- Cannot order an inactive service
- Cannot review an uncompleted order
- Cannot review the same order twice
- Cannot favourite the same service twice
- Cannot create duplicate worker profile
- Cannot send message to a conversation you don't belong to

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
| Deployment | Railway |

---

## Architecture

```
kasblink/
├── apps/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── users.py        # User, WorkerProfile, Portfolio
│   │   ├── catalog.py      # Category, Service
│   │   ├── orders.py       # Order, OrderImage
│   │   ├── chats.py        # Conversation, Message
│   │   ├── reviews.py      # Review, ReviewImage
│   │   └── favourites.py   # Favourite
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
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

**Filtered querysets** — Every viewset overrides `get_queryset()` to return only data belonging to the authenticated user. No user can access another user's orders, conversations, or portfolio items.

**Mixin-based viewsets** — Instead of `ModelViewSet` everywhere, each viewset explicitly declares only the actions it needs, preventing unintended endpoints from being exposed.

**Async email notifications** — All emails are sent via Celery background tasks. The HTTP response returns instantly without waiting for email delivery.

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
| PATCH | `/api/v1/orders/{id}/accept/` | ✅ Worker | Accept order |
| PATCH | `/api/v1/orders/{id}/complete/` | ✅ Worker | Complete order |
| PATCH | `/api/v1/orders/{id}/cancel/` | ✅ Client | Cancel order |

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
- [x] Deployed to Railway — live URL
- [ ] Tests with pytest — target 80%+ coverage
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