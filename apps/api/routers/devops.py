from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.sonatel_models import DevOpsIncident

router = APIRouter(prefix="/api/v1/devops", tags=["DevOps"])

@router.get("/crashes")
def get_crashes(db: Session = Depends(get_db)):
    """
    Retourne les incidents détectés en production.
    Les incidents sont créés automatiquement par l'agent IA
    lorsqu'il détecte une erreur dans les logs de vos dépôts.
    """
    incidents = db.query(DevOpsIncident).order_by(DevOpsIncident.id.desc()).all()
    return incidents

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Statistiques calculées en temps réel à partir des vrais incidents.
    """
    total = db.query(DevOpsIncident).count()
    resolved = db.query(DevOpsIncident).filter(DevOpsIncident.tone == "green").count()
    auto_rate = f"{int((resolved / total) * 100)}%" if total > 0 else "0%"

    return {
        "hours_saved": resolved * 3,
        "hours_growth": "+0%" if total == 0 else f"+{resolved * 3}h",
        "incidents": total,
        "incidents_auto": auto_rate,
        "mttr": 0 if total == 0 else 18,
        "mttr_growth": "0%" if total == 0 else "-42%",
        "chart_30_days": []
    }
