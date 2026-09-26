import requests
import os

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "VOTRE_CLEF_API_GEMINI")

# Modèle local mis en cache pour ne pas le recharger à chaque fois
_local_model = None

def _get_local_embedding(text: str) -> list[float]:
    global _local_model
    if _local_model is None:
        print("⚡ BASCULEMENT SUR L'IA LOCALE (MiniLM) EN COURS...")
        try:
            from sentence_transformers import SentenceTransformer
            # Modèle ultra-léger, rapide, générant 384 dimensions (compatible avec Gemini/NeonDB)
            _local_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ IA Locale chargée avec succès !")
        except Exception as e:
            print(f"❌ Impossible de charger l'IA locale : {e}")
            return [0.0] * 384
            
    vector = _local_model.encode(text[:8000]).tolist()
    if len(vector) < 384:
        vector.extend([0.0] * (384 - len(vector)))
    return vector[:384]

def get_huggingface_embedding(text: str) -> list[float]:
    """Tente Gemini, si erreur ou limite atteinte, passe le relais à l'IA locale"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent?key={GEMINI_KEY}"
    payload = {
        "model": "models/gemini-embedding-2",
        "content": {"parts": [{"text": text[:8000]}]},
        "outputDimensionality": 384
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            vector = data.get("embedding", {}).get("values", [])
            if vector:
                if len(vector) < 384: vector.extend([0.0] * (384 - len(vector)))
                return vector[:384]
                
        elif response.status_code == 429:
            print("⚠️ Quota Gemini atteint. L'IA Locale prend le relais immédiatement !")
            return _get_local_embedding(text)
            
        else:
            print(f"⚠️ Erreur Gemini ({response.status_code}). L'IA Locale prend le relais !")
            return _get_local_embedding(text)
            
    except Exception as e:
        print(f"⚠️ Connexion perdue avec Google. L'IA Locale prend le relais !")
        return _get_local_embedding(text)
