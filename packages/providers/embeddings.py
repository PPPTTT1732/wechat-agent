from sentence_transformers import SentenceTransformer

# Chargement du modèle local une seule fois (mise en cache en mémoire)
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_huggingface_embedding(text: str) -> list[float]:
    """Génère un vecteur de 384 dimensions via le modèle local all-MiniLM-L6-v2."""
    try:
        model = _get_model()
        vector = model.encode(text)
        return [float(x) for x in vector]
    except Exception as e:
        print(f"❌ Erreur embedding local : {e}")
        return [0.0] * 384
