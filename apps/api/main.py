from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routers import memory
from packages.database.models import Base
from packages.database.session import engine
from sqlalchemy import text
import os

app = FastAPI(title="WeChat AgentOps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            conn.execute(text("""
                ALTER TABLE knowledge_chunks 
                ADD COLUMN IF NOT EXISTS metadata_json JSON DEFAULT '{}'::json
            """))
        print("✅ Tables Neon vérifiées")
    except Exception as e:
        print(f"❌ Erreur DB: {e}")

app.include_router(memory.router)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except:
        pass
    return {"status": "ok", "database": "connected" if db_ok else "error"}
