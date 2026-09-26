from packages.database.session import SessionLocal
from packages.database.sonatel_models import DevOpsIncident, LeaderboardProfile, UIComponent

db = SessionLocal()

try:
    # 1. DevOps Incidents
    if db.query(DevOpsIncident).count() == 0:
        db.add_all([
            DevOpsIncident(error="TypeError: Cannot read properties of null (reading 'token')", repo="auth-service", time="Il y a 12 min", status="Corrigé (Auto-Heal)", tone="green"),
            DevOpsIncident(error="Timeout: Connection refused", repo="payment-gateway", time="Il y a 2h", status="En analyse (IA)", tone="amber"),
            DevOpsIncident(error="Build failed: missing dependency", repo="agentops-web", time="Il y a 5h", status="Ticket créé", tone="blue")
        ])
    
    # 2. Leaderboard
    if db.query(LeaderboardProfile).count() == 0:
        db.add_all([
            LeaderboardProfile(name="Malick Sy", initials="MS", score=312, growth="+22%", badge="Top Contributor"),
            LeaderboardProfile(name="Marie Laurent", initials="ML", score=248, growth="+15%", badge="Sécurité"),
            LeaderboardProfile(name="Awa Ba", initials="AB", score=195, growth="+8%", badge="Régulier")
        ])
    
    # 3. Components
    if db.query(UIComponent).count() == 0:
        db.add_all([
            UIComponent(name="Bouton PayDunya", tags="WXML · Paiement", author="Malick Sy", initials="MS", preview="Payer 5000 FCFA"),
            UIComponent(name="Carte Solde Orange Money", tags="WXML · Finance", author="Awa Ba", initials="AB", preview="Solde: 25 000 FCFA")
        ])
    
    db.commit()
    print("✅ Base de données Neon mise à jour avec de vraies données démo !")
except Exception as e:
    print(f"Erreur : {e}")
finally:
    db.close()
