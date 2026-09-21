import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# L'URL Neon (Serverless Postgres) est injectée via Docker ou le fichier .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/wechat_agent")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dépendance FastAPI pour obtenir une session de base de données par requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
