import re

with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

# On remplace l'ancienne fonction prepare_context avec la nouvelle vraie logique IA
old_func_regex = re.compile(r'@router\.post\("/prepare"\)\ndef prepare_context.*?except Exception as e:\n\s+raise HTTPException\(status_code=500, detail=f"Erreur prepare: \{str\(e\)\}"\)', re.DOTALL)

new_func = """@router.post("/prepare")
def prepare_context(req: PrepareRequest, db: Session = Depends(get_db)):
    \"\"\"Recherche les solutions (Retrieval) puis génère via MISTRAL API (Generation).\"\"\"
    try:
        vector = get_huggingface_embedding(req.prompt)
        vector_literal = "[" + ",".join(str(round(x, 6)) for x in vector) + "]"

        query = text(\"\"\"
            SELECT content
            FROM knowledge_chunks
            WHERE project_id = :pid AND status = 'TRUSTED'
            ORDER BY embedding <=> CAST(:vec AS vector)
            LIMIT 5
        \"\"\")

        results = db.execute(query, {"pid": req.project_id, "vec": vector_literal}).fetchall()

        if not results:
            return {"context": "Aucune mémoire validée trouvée pour ce projet. Appliquez les règles d'architecture standard."}

        raw_context = "\\n---\\n".join([row[0] for row in results])
        
        # --- GENERATION VIA MISTRAL API ---
        import urllib.request
        import json
        
        api_key = "mstrl_A3Z8hbAXiDmyZwC58BZbyZqD370yJQS8_3cBZ7J"
        url = "https://api.mistral.ai/v1/chat/completions"
        
        system_msg = "Tu es AgentOps, le Tech Lead IA de l'équipe de développement. Tu aides les développeurs en répondant à leurs questions d'architecture. Tu dois IMPÉRATIVEMENT te baser sur le CONTEXTE fourni (qui est extrait de la base de code de l'entreprise). Rédige une réponse claire, experte, concise et en français, en utilisant le format Markdown. Si le contexte ne donne pas la réponse, utilise tes compétences globales en précisant que le code source interne ne détaille pas ce point."
        user_msg = f"CONTEXTE LOCAL DU PROJET (Mémoire RAG) :\\n{raw_context}\\n\\nQUESTION DU DÉVELOPPEUR :\\n{req.prompt}"
        
        data = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.1
        }
        
        request_obj = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        try:
            with urllib.request.urlopen(request_obj) as response:
                result = json.loads(response.read().decode("utf-8"))
                answer = result["choices"][0]["message"]["content"]
                final_response = f"🤖 **AgentOps (Propulsé par Mistral AI)**\\n\\n{answer}"
        except Exception as e:
            final_response = f"🤖 **AgentOps AI (Erreur Réseau Mistral)**\\n\\nImpossible de contacter l'API : {str(e)}\\n\\nVoici les données brutes que j'avais trouvées :\\n{raw_context[:300]}"

        return {"context": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prepare: {str(e)}")"""

if "@router.post(\"/prepare\")" in content:
    content = old_func_regex.sub(new_func, content)
    with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Mise à jour réussie avec Mistral API")
else:
    print("Fonction non trouvée")

