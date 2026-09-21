#!/bin/bash
echo "🚀 [RENDER HACK] Démarrage du système 2-en-1..."

# On lance Celery en arrière-plan (le & à la fin est crucial)
echo "👷 Démarrage du Worker Celery..."
celery -A apps.worker.celery_app worker --loglevel=info &

# On lance l'API FastAPI au premier plan (Render écoute le port via $PORT)
echo "🌐 Démarrage de l'API FastAPI..."
# Si Render ne donne pas de PORT, on utilise 8000 par défaut
exec uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
