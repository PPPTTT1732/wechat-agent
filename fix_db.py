from packages.database.session import engine, SessionLocal
from packages.database.sonatel_models import LeaderboardProfile, DevOpsIncident

def fix():
    db = SessionLocal()
    if not db.query(LeaderboardProfile).first():
        db.add_all([
            LeaderboardProfile(name="Marie Laurent", initials="ML", score=248, growth="+18%", badge="Top contributor", rank=1),
            LeaderboardProfile(name="Simon Bernard", initials="SB", score=184, growth="+12%", badge="Régulier", rank=2),
            LeaderboardProfile(name="Clara Dubois", initials="CD", score=156, growth="+24%", badge="En progression", rank=3)
        ])
    if not db.query(DevOpsIncident).first():
        db.add_all([
            DevOpsIncident(error_trace="TypeError: Cannot read properties of undefined", repo="platform-api", time_ago="Il y a 8 min", status="PR créée automatiquement", tone="green"),
            DevOpsIncident(error_trace="TimeoutError: Database connection", repo="data-pipeline", time_ago="Il y a 42 min", status="Analyse en cours", tone="amber")
        ])
    db.commit()
    db.close()
    print("Seed réparé !")
fix()
