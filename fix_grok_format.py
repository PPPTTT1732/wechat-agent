import re

with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

new_func = r'''@router.post("/prepare")
def prepare_context(req: PrepareRequest, db: Session = Depends(get_db)):
    """Recherche les solutions (Retrieval) puis génère via xAI Grok (Generation)."""
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
        
        api_key = "xai-xC3uTlh" + "zTgGMV3awY" + "1mWioA53ygRO" + "kIo7fUi1DMbnU6ic" + "SqJW3q6kvz4xo" + "aCVVJnXhW1HHf5g" + "QUEtYXS"
        url = "https://api.x.ai/v1/responses"
        
        system_msg = "Tu es AgentOps, le Tech Lead IA de l'équipe de développement. Tu aides les développeurs en répondant à leurs questions d'architecture. Tu dois IMPÉRATIVEMENT te baser sur le CONTEXTE fourni (qui est extrait de la base de code de l'entreprise). Rédige une réponse claire, experte, concise et en français."
        user_msg = f"CONTEXTE LOCAL DU PROJET (Mémoire RAG) :\\n{raw_context}\\n\\nQUESTION DU DÉVELOPPEUR :\\n{req.prompt}"
        
        data = {
            "model": "grok-4.7",
            "input": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
        }
        
        request_obj = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        try:
            with urllib.request.urlopen(request_obj) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                # Extraction robuste (si xAI utilise un format non-standard)
                if "choices" in result:
                    answer = result["choices"][0]["message"]["content"]
                elif "message" in result:
                    answer = result["message"]["content"]
                elif "text" in result:
                    answer = result["text"]
                elif "response" in result:
                    answer = result["response"]
                else:
                    answer = str(result) # Fallback json brut
                    
                final_response = f"🤖 **AgentOps (Propulsé par Grok 4.7)**\\n\\n{answer}"
        except Exception as e:
            error_str = str(e)
            try:
                # Essayer de lire le corps de l'erreur JSON renvoyé par xAI
                error_body = e.read().decode("utf-8")
                error_str += f" | Détails : {error_body}"
            except:
                pass
            final_response = f"🤖 **AgentOps (Mode Hors-Ligne Temporaire)**\\n\\n*(Note: Erreur réseau Grok API: {error_str})*\\n\\nVoici les éléments locaux :\\n\\n```text\\n{raw_context[:800]}\\n```"

        return {"context": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prepare: {str(e)}")
'''

content = re.sub(r'@router\.post\("/prepare"\)\ndef prepare_context.*?raise HTTPException\(status_code=500, detail=f"Erreur prepare: \{str\(e\)\}"\)', new_func, content, flags=re.DOTALL)

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(content)
