from sqlalchemy import text
from packages.database.session import engine
from packages.database.models import Base

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS knowledge_chunks CASCADE;"))
    
Base.metadata.create_all(bind=engine)
print("Base de données réinitialisée avec les vecteurs de 384 dimensions !")
