import requests
import os

def get_huggingface_embedding(text: str) -> list[float]:
    """Utilise l'API gratuite d'HuggingFace pour générer un vecteur de 384 dimensions.
    
    HuggingFace feature-extraction retourne [[v1, v2, ...]] pour un seul texte.
    On aplatit toujours le résultat pour obtenir [v1, v2, ...].
    """
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"

    headers = {}
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

        # HuggingFace retourne parfois [[...]] au lieu de [...] — on aplatit
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            result = result[0]

        # Vérification de la dimension attendue
        if len(result) != 384:
            print(f"⚠️ Dimension inattendue : {len(result)}, attendu 384")

        return result

    except Exception as e:
        print(f"❌ Erreur HuggingFace Embeddings : {e}")
        # Vecteur neutre de secours pour ne pas bloquer le serveur
        return [0.0] * 384
