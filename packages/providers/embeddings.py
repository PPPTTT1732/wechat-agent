import requests
import os

def get_huggingface_embedding(text: str) -> list[float]:
    """Utilise l'API gratuite d'HuggingFace pour générer un vecteur de 384 dimensions."""
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    # URL correcte pour les modèles sentence-transformers
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    headers = {"Content-Type": "application/json"}
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": text, "options": {"wait_for_model": True}},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        # HuggingFace sentence-transformers retourne [[...]] pour un seul texte
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            result = result[0]

        # Vérification de la dimension et des valeurs
        if not isinstance(result, list) or len(result) == 0:
            print(f"⚠️ Réponse HuggingFace inattendue : {str(result)[:200]}")
            return [0.0] * 384

        if len(result) != 384:
            print(f"⚠️ Dimension inattendue : {len(result)}, attendu 384")

        return [float(x) for x in result]

    except Exception as e:
        print(f"❌ Erreur HuggingFace Embeddings : {e}")
        return [0.0] * 384

