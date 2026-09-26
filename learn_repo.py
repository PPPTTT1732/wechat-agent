import psycopg2, os, sys
from sentence_transformers import SentenceTransformer

# === CONFIGURATION ===
DB_URL = "postgresql://neondb_owner:npg_B2kebzUrd6Nv@ep-dry-butterfly-b5d2o7tf-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require"
EXTENSIONS_TO_READ = ['.js', '.ts', '.wxml', '.wxss', '.json', '.md', '.wxs']

def ingest_directory(directory_path, project_id):
    if not os.path.exists(directory_path):
        print(f"❌ Dossier introuvable : {directory_path}")
        return

    print(f"🚀 Chargement du modèle IA local pour {project_id}...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    total_chunks = 0

    print(f"📂 Analyse du dossier : {directory_path}")
    for root, dirs, files in os.walk(directory_path):
        # Ignorer les dossiers inutiles
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.vscode', 'miniprogram_npm']]
        
        for fname in files:
            ext = os.path.splitext(fname)[1]
            if ext not in EXTENSIONS_TO_READ:
                continue
            
            filepath = os.path.join(root, fname)
            try:
                with open(filepath, encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                
                if len(content) < 30:
                    continue
                
                # Contextualisation
                parent_dir = os.path.basename(os.path.dirname(filepath))
                enriched = f"[{parent_dir}] {fname}\n{content}"
                
                # Découpage (Chunks de 800 caractères)
                chunks = [enriched[i:i+900] for i in range(0, len(enriched), 800)]
                
                for chunk in chunks:
                    vec = model.encode(chunk).tolist()
                    vec_str = '[' + ','.join(str(round(x, 6)) for x in vec) + ']'
                    
                    cur.execute("""
                        INSERT INTO knowledge_chunks (project_id, content, embedding, status, metadata_json)
                        VALUES (%s, %s, %s::vector, 'TRUSTED', %s::jsonb)
                    """, (project_id, chunk, vec_str, f'{{"source": "{fname}", "path": "{filepath}"}}'))
                    total_chunks += 1
                
                conn.commit()
                print(f"  ✅ {fname} — {len(chunks)} chunks")
            except Exception as e:
                print(f"  ⚠️ Erreur sur {fname}: {e}")

    print(f"\n🎉 TERMINÉ ! {total_chunks} nouveaux chunks ajoutés au projet '{project_id}'.")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 learn_repo.py <PROJECT_ID> <CHEMIN_DU_DOSSIER>")
        print("Exemple: python3 learn_repo.py mp-orange-money /chemin/vers/le/code")
        sys.exit(1)
        
    project = sys.argv[1]
    folder = sys.argv[2]
    ingest_directory(folder, project)
