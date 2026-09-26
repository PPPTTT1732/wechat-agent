import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/wechat_agent")

# NullPool = pas de recyclage de connexions (obligatoire pour Neon serverless)
# Chaque requête HTTP ouvre et ferme sa propre connexion DB

# [RENDER HACK] Force psycopg2 no matter the environment variable
SAFE_DB_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://")
if SAFE_DB_URL.startswith("postgres://"):
    SAFE_DB_URL = SAFE_DB_URL.replace("postgres://", "postgresql+psycopg2://")
elif SAFE_DB_URL.startswith("postgresql://"):
    SAFE_DB_URL = SAFE_DB_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(SAFE_DB_URL, poolclass=NullPool)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dépendance FastAPI pour obtenir une session de base de données par requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
