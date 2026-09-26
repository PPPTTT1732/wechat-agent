#!/bin/bash
echo "🚀 [RENDER HACK] Démarrage du système 2-en-1..."

# Brider l'IA pour économiser la mémoire (Mode "Régime")
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export PYTORCH_OPENMP_THREADS=1

# On lance Celery en arrière-plan en mode "Solo" (0 clonage de RAM)
echo "👷 Démarrage du Worker Celery..."
celery -A apps.worker.celery_app worker --pool=solo --loglevel=info &

# On lance l'API FastAPI au premier plan
echo "🌐 Démarrage de l'API FastAPI..."
exec uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
