from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.sonatel_models import LeaderboardProfile

router = APIRouter(prefix="/api/v1/team", tags=["Team"])

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Retourne le classement des développeurs basé sur leurs vraies contributions.
    Le classement se remplit automatiquement quand des développeurs publient
    des composants ou résolvent des incidents via la plateforme.
    """
    leaders = db.query(LeaderboardProfile).order_by(LeaderboardProfile.rank).all()
    return leaders
