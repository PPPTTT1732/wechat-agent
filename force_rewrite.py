import re

with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

new_func = r'''@router.post("/prepare")
def prepare_context(req: PrepareRequest, db: Session = Depends(get_db)):
    """Recherche les solutions (Retrieval) puis génère via MISTRAL API (Generation)."""
    try:
        vector = get_huggingface_embedding(req.prompt)
        vector_literal = "[" + ",".join(str(round(x, 6)) for x in vector) + "]"

        query = text("""
            SELECT content
            FROM knowledge_chunks
            WHERE project_id = :pid AND status = 'TRUSTED'
            ORDER BY embedding <=> CAST(:vec AS vector)
            LIMIT 5
        """)

        results = db.execute(query, {"pid": req.project_id, "vec": vector_literal}).fetchall()

        if not results:
            return {"context": "Aucune mémoire validée trouvée pour ce projet. Appliquez les règles d'architecture standard."}

        raw_context = "\\n---\\n".join([row[0] for row in results])
        
        import urllib.request
        import json
        
        api_key = "mstrl_A3Z8hbAXiDmyZwC58BZbyZqD370yJQS8_3cBZ7J"
        url = "https://api.mistral.ai/v1/chat/completions"
        
        system_msg = "Tu es AgentOps, le Tech Lead IA de l'équipe de développement. Tu aides les développeurs en répondant à leurs questions d'architecture. Tu dois IMPÉRATIVEMENT te baser sur le CONTEXTE fourni (qui est extrait de la base de code de l'entreprise). Rédige une réponse claire, experte, concise et en français, en utilisant le format Markdown."
        user_msg = f"CONTEXTE LOCAL DU PROJET (Mémoire RAG) :\\n{raw_context}\\n\\nQUESTION DU DÉVELOPPEUR :\\n{req.prompt}"
        
        data = {
            "model": "open-mistral-7b",
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
            error_str = str(e)
            if "429" in error_str:
                final_response = f"🤖 **AgentOps (Mode Hors-Ligne Temporaire)**\\n\\n*(Note: Limite de requêtes IA atteinte pour cette démonstration. Basculement sur l'extraction d'architecture locale)*\\n\\nVoici les éléments que j'ai trouvés dans notre base de code (Trusted) :\\n\\n```text\\n{raw_context[:800]}\\n```"
            else:
                final_response = f"🤖 **AgentOps AI (Erreur Réseau Mistral)**\\n\\nImpossible de contacter l'API : {error_str}\\n\\nVoici les données brutes :\\n{raw_context[:300]}"

        return {"context": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prepare: {str(e)}")
'''

content = re.sub(r'@router\.post\("/prepare"\)\ndef prepare_context.*?raise HTTPException\(status_code=500, detail=f"Erreur prepare: \{str\(e\)\}"\)', new_func, content, flags=re.DOTALL)

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(content)
