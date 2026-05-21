# KasbLink — Service Marketplace API

<div align="center">

**A production-grade REST API for a freelance service marketplace.**  
Clients discover and hire verified workers. Built with Django REST Framework.

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-green?logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.x-red)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[API Docs](#api-docs) · [Quick Start](#quick-start) · [Features](#features) · [Architecture](#architecture)

</div>

---

## What is KasbLink?

KasbLink is a service marketplace platform — similar to Fiverr or Upwork — built for the Central Asian market. Workers list their services (design, development, translation, repair, etc.), clients browse and place orders, communicate via chat, and leave reviews after completion.

This repository is the **backend API only**. It is designed to be consumed by a separate frontend (React / Next.js / mobile app).

---

## Features

### Core
- JWT authentication (access + refresh tokens)
- Role-based access control — `client`, `worker`, `admin`
- Worker profiles with portfolio showcase
- Service listings with category filtering and full-text search
- Order lifecycle management — `pending → accepted → completed / cancelled`
- Messaging system between order participants
- Star ratings and reviews (only on completed orders)
- Favourites / wishlist for services

### API & Developer Experience
- RESTful API with consistent JSON response structure
- Auto-generated Swagger / ReDoc documentation
- Filtering, searching, and ordering on all list endpoints
- Pagination on all list responses
- Detailed validation error messages

### Security
- JWT with short-lived access tokens (15 min) and refresh rotation
- Object-level permissions — users only access their own data
- Role-level permissions on every endpoint
- No sensitive data in responses (passwords, tokens stripped by serializers)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5, Django REST Framework |
| Database | PostgreSQL 16 |
| Auth | JWT via `djangorestframework-simplejwt` |
| API Docs | `drf-spectacular` (Swagger + ReDoc) |
| Filtering | `django-filter` |
| Environment | `django-environ` |

---

## Architecture

```
kasblink/
├── apps/
│   ├── models/
│   │   ├── users.py        # User, WorkerProfile, Portfolio
│   │   ├── catalog.py      # Category, Service
│   │   ├── orders.py       # Order, OrderImage
│   │   ├── chats.py        # Conversation, Message
│   │   ├── reviews.py      # Review, ReviewImage
│   │   ├── favourites.py   # Favourite
│   │   └── __init__.py
│   ├── serializers/
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
├── root/
│   ├── settings.py
│   └── urls.py
└── manage.py
```

### Design Decisions

**Single app, models package** — All models live in one Django app, split across files by domain. Chosen over multiple apps to reduce boilerplate for a single-developer project at this scale.

**Role-based permissions** — Three custom DRF permission classes (`IsWorker`, `IsClient`, `IsOwner`) applied at the viewset level. Public endpoints use `AllowAny`, all mutation endpoints require authentication and role verification.

**Filtered querysets** — Every viewset overrides `get_queryset()` to return only data belonging to the authenticated user. No user can access another user's orders, conversations, or portfolio items.

**Mixin-based viewsets** — Instead of `ModelViewSet` everywhere, each viewset explicitly declares only the actions it needs (`ListModelMixin`, `CreateModelMixin`, etc.), preventing unintended endpoints from being exposed.

---

## API Docs

Once running, interactive documentation is available at:

| Format | URL |
|---|---|
| Swagger UI | `http://localhost:8000/api/schema/swagger-ui/` |
| ReDoc | `http://localhost:8000/api/schema/redoc/` |
| OpenAPI JSON | `http://localhost:8000/api/schema/` |

---

## Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 16+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/asilbekusmonov-gh/kasblink.git
cd kasblink
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

### 5. Set up the database

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the server

```bash
python manage.py runserver
```

API is now running at `http://localhost:8000`  
Admin panel at `http://localhost:8000/admin/`  
API docs at `http://localhost:8000/api/schema/swagger-ui/`

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register/` | Register a new user |
| POST | `/api/v1/auth/login/` | Login — returns access + refresh token |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/users/me/` | ✅ | Get current user profile |
| PATCH | `/api/v1/users/{id}/` | ✅ Owner | Update profile |

### Workers

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/worker-profiles/` | ❌ | List all worker profiles |
| GET | `/api/v1/worker-profiles/{id}/` | ❌ | Worker profile detail |
| POST | `/api/v1/worker-profiles/` | ✅ Worker | Create worker profile |
| PATCH | `/api/v1/worker-profiles/{id}/` | ✅ Owner | Update worker profile |
| GET | `/api/v1/portfolio/` | ✅ | My portfolio items |
| POST | `/api/v1/portfolio/` | ✅ Worker | Add portfolio item |
| DELETE | `/api/v1/portfolio/{id}/` | ✅ Owner | Remove portfolio item |

### Services

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/services/` | ❌ | Browse all services |
| GET | `/api/v1/services/{id}/` | ❌ | Service detail |
| POST | `/api/v1/services/` | ✅ Worker | Create a service |
| PATCH | `/api/v1/services/{id}/` | ✅ Owner | Update service |
| DELETE | `/api/v1/services/{id}/` | ✅ Owner | Delete service |

### Orders

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/orders/` | ✅ | My orders (client or worker view) |
| POST | `/api/v1/orders/` | ✅ Client | Place an order |
| PATCH | `/api/v1/orders/{id}/accept/` | ✅ Worker | Accept order |
| PATCH | `/api/v1/orders/{id}/complete/` | ✅ Worker | Mark as completed |
| PATCH | `/api/v1/orders/{id}/cancel/` | ✅ Client | Cancel order |

### Conversations & Messages

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/conversations/` | ✅ | My conversations |
| GET | `/api/v1/conversations/{id}/` | ✅ | Conversation detail |
| GET | `/api/v1/messages/` | ✅ | My messages |
| POST | `/api/v1/messages/` | ✅ | Send a message |

### Reviews

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/reviews/` | ✅ | My reviews |
| POST | `/api/v1/reviews/` | ✅ Client | Leave a review (completed orders only) |

### Favourites

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/favourites/` | ✅ | My saved services |
| POST | `/api/v1/favourites/` | ✅ | Save a service |
| DELETE | `/api/v1/favourites/{id}/` | ✅ | Remove from favourites |

### Categories

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/categories/` | ❌ | List all categories |
| GET | `/api/v1/categories/{id}/` | ❌ | Category detail |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DEBUG` | ✅ | `True` for dev, `False` for production |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `ALLOWED_HOSTS` | ✅ | Comma-separated list of allowed hosts |
| `CORS_ALLOWED_ORIGINS` | ✅ | Frontend origin URLs |

See `.env.example` for a full template.

---

## Roadmap

- [ ] Celery + Redis for background tasks
- [ ] Email notifications (order updates, messages)
- [ ] Real-time chat with Django Channels (WebSocket)
- [ ] File uploads to AWS S3 / MinIO
- [ ] Payment integration (Payme, Click)
- [ ] Push notifications (Firebase FCM)
- [ ] Docker + Docker Compose setup
- [ ] CI/CD with GitHub Actions
- [ ] Elasticsearch for advanced search
- [ ] Test suite with pytest (target: 80%+ coverage)

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feat/your feature`)
5. Open a Pull Request

---

## License

[MIT](LICENSE)

---

<div align="center">
  Built by <a href="https://github.com/yourusername">Asilbek</a> · Tashkent, Uzbekistan
</div>