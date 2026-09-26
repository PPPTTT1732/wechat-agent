FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances
# Installation des dépendances depuis pyproject.toml (source unique de vérité)
COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy alembic pgvector psycopg2-binary openai anthropic celery redis sentence-transformers>=2.2.2
RUN pip install --no-cache-dir setuptools wheel
RUN pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy alembic pgvector psycopg2-binary openai anthropic celery redis sentence-transformers>=2.2.2 requests typer sentence-transformers>=2.2.2

# Copie du code source
COPY . .

# Déplacement du script de démarrage et ajout des droits
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Render injecte la variable $PORT automatiquement
EXPOSE 8000

# Lancement du système unifié
CMD ["/start.sh"]
