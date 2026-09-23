from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/twin", tags=["Twin"])

@router.get("/")
def get_pr_reviews():
    return [
        {"id": 482, "title": "feat: integration API Orange Money", "status": "Validé par l'IA", "confidence": 99, "time": "Il y a 2 min"},
        {"id": 481, "title": "fix: bug de paiement double", "status": "Rejeté (Faille détectée)", "confidence": 85, "time": "Il y a 1h"}
    ]
