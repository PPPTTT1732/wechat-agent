from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from packages.database.session import get_db
from packages.database.sonatel_models import ApiToken, UserProfile
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
    user = db.query(UserProfile).filter(UserProfile.clerk_id == req.clerk_id).first()
    
    # Premier admin automatique pour les fondateurs, les autres sont USER
    default_role = "ADMIN" if "malickteuw.devweb@gmail.com" in req.email.lower() else "USER"
    
    if not user:
        user = UserProfile(
            clerk_id=req.clerk_id,
            email=req.email,
            name=req.name,
            role=default_role,
            can_ingest=1 if default_role == "ADMIN" else 0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return {
        "role": user.role, 
        "can_ingest": bool(user.can_ingest), 
        "message": "Synchronisation réussie"
    }

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserProfile).all()
    return [{"id": u.clerk_id, "name": u.name, "email": u.email, "role": u.role, "can_ingest": bool(u.can_ingest)} for u in users]

@router.post("/users/{clerk_id}/toggle-ingest")
def toggle_ingest_permission(clerk_id: str, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.can_ingest = 0 if user.can_ingest == 1 else 1
    db.commit()
    
    return {"message": "Permission mise à jour", "can_ingest": bool(user.can_ingest)}

@router.post("/token")
def generate_cli_token(req: TokenRequest, db: Session = Depends(get_db)):
    raw_token = secrets.token_hex(24)
    full_token = f"sk_live_{raw_token}"
    new_token = ApiToken(clerk_id=req.clerk_id, token=full_token)
    db.add(new_token)
    db.commit()
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

@router.get("/force-migrate")
def force_migrate():
    from packages.database.session import engine
    from packages.database.models import Base
    from packages.database.sonatel_models import Base as SonatelBase
    Base.metadata.create_all(bind=engine)
    SonatelBase.metadata.create_all(bind=engine)
    return {"message": "Toutes les tables ont été synchronisées avec succès !"}
