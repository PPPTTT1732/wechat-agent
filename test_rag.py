from packages.database.session import SessionLocal
from sqlalchemy import text
from packages.providers.embeddings import get_huggingface_embedding

# On simule la question du stagiaire
question = "Pourquoi ma page déborde et ne respecte pas la grille sur iPhone ?"
print(f"QUESTION DU STAGIAIRE : '{question}'\n")

vector = get_huggingface_embedding(question)
vector_literal = "[" + ",".join(str(round(x, 6)) for x in vector) + "]"

db = SessionLocal()
try:
    query = text("""
        SELECT content 
        FROM knowledge_chunks 
        WHERE project_id = 'mp-afritrips' 
        ORDER BY embedding <=> CAST(:vec AS vector) 
        LIMIT 2
    """)
    results = db.execute(query, {"vec": vector_literal}).fetchall()
    
    if results:
        print("✅ TROUVÉ PAR LE MOTEUR RAG DANS LA BASE DE DONNÉES :\n")
        for i, row in enumerate(results):
            print(f"--- DOCUMENT {i+1} SÉLECTIONNÉ POUR L'IA ---")
            print(row[0][:400] + "...\n")
    else:
        print("❌ RIEN TROUVÉ.")
finally:
    db.close()
