import requests
import os

def get_huggingface_embedding(text: str) -> list[float]:
    """Utilise l'API gratuite d'HuggingFace pour générer un vecteur de 384 dimensions."""
    # Modèle extrêmement rapide et léger pour le code/texte
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    
    # En production, on utiliserait un HF_TOKEN, mais l'API publique fonctionne pour de petits volumes
    headers = {}
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
        
    response = requests.post(api_url, headers=headers, json={"inputs": text, "options": {"wait_for_model": True}})
    
    if response.status_code == 200:
        return response.json()
    else:
        # Fallback de secours (vecteur neutre) si l'API est surchargée
        print(f"Erreur HF API: {response.text}")
        return [0.0] * 384
