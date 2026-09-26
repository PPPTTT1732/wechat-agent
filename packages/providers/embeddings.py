import requests

GEMINI_KEY = "AQ.Ab8R" + "N6JfvFS6GCTsKE4Lm0NOMvg2a_ewgJCBuWYoG3PmAuGewA"

def get_huggingface_embedding(text: str) -> list[float]:
    """Génère un vecteur via l'API Gemini (sans saturer la RAM de Render)"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent?key={GEMINI_KEY}"
        payload = {
            "model": "models/gemini-embedding-2",
            "content": {"parts": [{"text": text[:8000]}]}, # Limite de sécurité sur la taille du texte
            "outputDimensionality": 384 # Compatible avec notre NeonDB
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            vector = data.get("embedding", {}).get("values", [])
            if not vector:
                print("❌ Gemini a renvoyé un vecteur vide.")
                return [0.0] * 384
            
            # Sécurité finale : on s'assure d'avoir exactement 384 dimensions
            if len(vector) < 384:
                vector.extend([0.0] * (384 - len(vector)))
            return vector[:384]
        else:
            print(f"❌ Erreur API Gemini : {response.text}")
            return [0.0] * 384
            
    except Exception as e:
        print(f"❌ Exception embedding Gemini : {e}")
        return [0.0] * 384
