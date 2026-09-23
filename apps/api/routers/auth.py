from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.auth_models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class SyncRequest(BaseModel):
    clerk_id: str
    email: str = None
    name: str = None

@router.post("/sync")
def sync_user(req: SyncRequest, db: Session = Depends(get_db)):
    # On cherche si l'utilisateur existe déjà
    user = db.query(User).filter(User.clerk_id == req.clerk_id).first()
    
    if not user:
        # S'il n'existe pas, on compte combien il y a d'utilisateurs en tout
        total_users = db.query(User).count()
        
        # Le TOUT PREMIER utilisateur devient automatiquement ADMIN !
        new_role = "ADMIN" if total_users == 0 else "USER"
        
        user = User(clerk_id=req.clerk_id, email=req.email, name=req.name, role=new_role)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return {"status": "success", "role": user.role, "email": user.email}
