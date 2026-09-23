import os
from sqlalchemy import create_engine, text
from packages.database.models import Base

DB_URL = "postgresql://neondb_owner:npg_jv6Ome5nfQGZ@ep-crimson-snow-b4ya9bdd-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DB_URL)

with engine.begin() as conn:
    print("Vidage de l'ancienne table...")
    conn.execute(text("DROP TABLE IF EXISTS knowledge_chunks CASCADE;"))
    
Base.metadata.create_all(bind=engine)
print("✅ Table recréée avec succès avec le bon format !")

