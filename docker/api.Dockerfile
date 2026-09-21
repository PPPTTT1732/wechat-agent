FROM python:3.12-slim

# Empêche Python de bufferiser les logs (pratique pour voir les erreurs en temps réel)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances (directement via pip pour le MVP)
RUN pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy alembic pgvector psycopg2-binary openai anthropic celery redis

# Copie du code source
COPY . .

EXPOSE 8000

# Commande de lancement de l'API
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
