FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

CMD ["uv", "run", "python3", "manage.py", "runserver", "0:8001"]