from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from packages.database.session import get_db
from packages.database.sonatel_models import ApiToken
import secrets

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class SyncUserRequest(BaseModel):
    clerk_id: str
    email: str
    name: str

class TokenRequest(BaseModel):
    clerk_id: str

@router.post("/sync")
def sync_user(req: SyncUserRequest, db: Session = Depends(get_db)):
    # Simuler le rôle en fonction du premier arrivé (ou spécifique admin)
    role = "ADMIN" if "marie" in req.email.lower() or "malick" in req.email.lower() else "USER"
    return {"role": role, "message": "Synchronisation réussie"}

@router.post("/token")
def generate_cli_token(req: TokenRequest, db: Session = Depends(get_db)):
    # 1. Générer un vrai token cryptographique
    raw_token = secrets.token_hex(24)
    full_token = f"sk_live_{raw_token}"
    
    # 2. Sauvegarder dans Neon
    new_token = ApiToken(clerk_id=req.clerk_id, token=full_token)
    db.add(new_token)
    db.commit()
    
    # 3. Retourner le token (affiché une seule fois au user)
    return {"token": full_token}

@router.post("/seed-demo")
def seed_demo_data(db: Session = Depends(get_db)):
    from packages.database.sonatel_models import DevOpsIncident, LeaderboardProfile, UIComponent
    if db.query(DevOpsIncident).count() == 0:
        db.add_all([
            DevOpsIncident(error_trace="TypeError: Cannot read properties of null", repo="auth-service", time_ago="Il y a 12 min", status="Corrigé (Auto-Heal)", tone="green"),
            DevOpsIncident(error_trace="Timeout: Connection refused", repo="payment-gateway", time_ago="Il y a 2h", status="En analyse (IA)", tone="amber")
        ])
    if db.query(LeaderboardProfile).count() == 0:
        db.add_all([
            LeaderboardProfile(name="Malick Sy", initials="MS", score=312, growth="+22%", badge="Top Contributor"),
            LeaderboardProfile(name="Marie Laurent", initials="ML", score=248, growth="+15%", badge="Sécurité")
        ])
    if db.query(UIComponent).count() == 0:
        db.add_all([
            UIComponent(name="Bouton PayDunya", tags="WXML · Paiement", author="Malick Sy", initials="MS", preview="Payer 5000 FCFA")
        ])
    db.commit()
    return {"message": "Données démo injectées"}
