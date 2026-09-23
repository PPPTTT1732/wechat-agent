import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/wechat_agent")

# NullPool = pas de recyclage de connexions (obligatoire pour Neon serverless)
# Chaque requête HTTP ouvre et ferme sa propre connexion DB
engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dépendance FastAPI pour obtenir une session de base de données par requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
