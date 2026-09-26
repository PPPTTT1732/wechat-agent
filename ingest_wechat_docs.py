import psycopg2
import os
import sys

# Connexion Neon
DB_URL = "postgresql://neondb_owner:npg_B2kebzUrd6Nv@ep-dry-butterfly-b5d2o7tf-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Dossiers sources
DOCS_DIRS = [
    "/home/pmt/Téléchargements/mp-afritrips (1)/mp-afritrips/repo1/ats-app/docs",
    "/home/pmt/Téléchargements/frontend-api-architecture-kit"
]
PROJECT_ID = "mp-afritrips"

# Import de la fonction d'embedding locale
sys.path.insert(0, '.')
from packages.providers.embeddings import get_huggingface_embedding

def chunk_text(text, max_chars=1200):
    """Découpe un texte en chunks de max_chars caractères en respectant les paragraphes."""
    paragraphs = text.split('\n\n')
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < max_chars:
            current += p + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = p + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

total = 0
for docs_dir in DOCS_DIRS:
    if not os.path.exists(docs_dir):
        print(f"⚠️  Dossier introuvable : {docs_dir}")
        continue
    
    files = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
    print(f"\n📂 {docs_dir} — {len(files)} fichiers trouvés")
    
    for filename in sorted(files):
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_text(content)
        for i, chunk in enumerate(chunks):
            try:
                vector = get_huggingface_embedding(chunk)
                vector_str = "[" + ",".join(str(round(x, 6)) for x in vector) + "]"
                cur.execute("""
                    INSERT INTO knowledge_chunks (project_id, content, embedding, status, metadata_json)
                    VALUES (%s, %s, %s::vector, 'TRUSTED', %s)
                """, (PROJECT_ID, chunk, vector_str, f'{{"source": "{filename}", "chunk": {i}}}'))
                total += 1
            except Exception as e:
                print(f"  ⚠️ Erreur chunk {i} de {filename}: {e}")
        
        conn.commit()
        print(f"  ✅ {filename} — {len(chunks)} chunks ingérés")

print(f"\n🎉 INGESTION TERMINÉE : {total} chunks dans la base Neon !")
conn.close()
