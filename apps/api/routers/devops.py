from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.sonatel_models import DevOpsIncident

router = APIRouter(prefix="/api/v1/devops", tags=["DevOps"])

@router.get("/crashes")
def get_crashes(db: Session = Depends(get_db)):
    incidents = db.query(DevOpsIncident).all()
    if not incidents:
        # Seed pour la démo
        demo_data = [
            DevOpsIncident(error_trace="TypeError: Cannot read properties of undefined", repo="platform-api", time_ago="Il y a 8 min", status="PR créée automatiquement", tone="green"),
            DevOpsIncident(error_trace="TimeoutError: Database connection", repo="data-pipeline", time_ago="Il y a 42 min", status="Analyse en cours", tone="amber")
        ]
        db.add_all(demo_data)
        db.commit()
        incidents = db.query(DevOpsIncident).all()
    return incidents

@router.get("/stats")
def get_stats():
    return {
        "hours_saved": 124, "hours_growth": "+28.4%",
        "incidents": 38, "incidents_auto": "92%",
        "mttr": 18, "mttr_growth": "-42%",
        "chart_30_days": [38,55,45,68,64,80,72,92,78,100,88,96]
    }
