from fastapi import FastAPI
from apps.api.routers import memory
from packages.database.models import Base
from packages.database.session import engine
from sqlalchemy import text
import os

app = FastAPI(title="WeChat AgentOps API")

# Création automatique des tables au démarrage (si elles n'existent pas)
@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        # Migration douce : ajout des colonnes manquantes sans perdre les données
        with engine.begin() as conn:
            conn.execute(text("""
                ALTER TABLE knowledge_chunks 
                ADD COLUMN IF NOT EXISTS metadata_json JSON DEFAULT '{}'::json
            """))
        print("✅ Tables Neon créées/migrées avec succès")
    except Exception as e:
        print(f"❌ Erreur de migration DB: {e}")

app.include_router(memory.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Le Cerveau d'Équipe AgentOps est en ligne !"}

@app.get("/health")
def health_check():
    """Endpoint de diagnostic complet."""
    db_ok = False
    hf_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_ok = True
    except Exception as e:
        pass
    return {
        "status": "ok",
        "database": "connected" if db_ok else "error",
        "env": {
            "DATABASE_URL": "set" if os.getenv("DATABASE_URL") else "MISSING",
            "REDIS_URL": "set" if os.getenv("REDIS_URL") else "MISSING",
        }
    }
