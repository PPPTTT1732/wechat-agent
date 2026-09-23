from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.sonatel_models import LeaderboardProfile

router = APIRouter(prefix="/api/v1/team", tags=["Team"])

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    leaders = db.query(LeaderboardProfile).order_by(LeaderboardProfile.rank).all()
    if not leaders:
        # Seed
        demo_data = [
            LeaderboardProfile(name="Marie Laurent", initials="ML", score=248, growth="+18%", badge="Top contributor", rank=1),
            LeaderboardProfile(name="Simon Bernard", initials="SB", score=184, growth="+12%", badge="Régulier", rank=2),
            LeaderboardProfile(name="Clara Dubois", initials="CD", score=156, growth="+24%", badge="En progression", rank=3)
        ]
        db.add_all(demo_data)
        db.commit()
        leaders = db.query(LeaderboardProfile).order_by(LeaderboardProfile.rank).all()
    return leaders
