from packages.database.session import SessionLocal
from packages.database.models import KnowledgeChunk

db = SessionLocal()
try:
    db.query(KnowledgeChunk).filter(KnowledgeChunk.project_id == "mp-afritrips").update({"status": "TRUSTED"})
    db.commit()
    print("✅ Le code local est validé par le Lead Dev (TRUSTED). L'IA peut l'utiliser.")
except Exception as e:
    print(e)
finally:
    db.close()
