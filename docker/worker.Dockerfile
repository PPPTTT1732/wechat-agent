FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des mêmes dépendances
RUN pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy alembic pgvector psycopg2-binary openai anthropic celery redis sentence-transformers>=2.2.2

COPY . .

# Commande de lancement du Worker Celery
CMD ["celery", "-A", "apps.worker.celery_app", "worker", "--loglevel=info"]
