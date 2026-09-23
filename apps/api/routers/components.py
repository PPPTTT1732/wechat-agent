from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.sonatel_models import UIComponent

router = APIRouter(prefix="/api/v1/components", tags=["Components"])

@router.get("/")
def get_components(db: Session = Depends(get_db)):
    components = db.query(UIComponent).order_by(UIComponent.id.desc()).all()
    if not components:
        # Seed pour la démo
        demo_data = [
            UIComponent(name="Bouton Paiement Orange Money", tags="WXML · UI · Mobile Money", author="Awa Ba", initials="AB", preview="Payer 25 000 FCFA", code={"WXML": "<button class='om-button'>Payer {{amount}} FCFA</button>"}),
            UIComponent(name="Carte solde client", tags="WXML · Data · Orange Money", author="Ousmane Mbaye", initials="OM", preview="Solde disponible 85 400 F", code={"WXML": "<view class='balance'>85 400 F</view>"})
        ]
        db.add_all(demo_data)
        db.commit()
        components = db.query(UIComponent).order_by(UIComponent.id.desc()).all()
    return components

@router.post("/")
def publish_component(payload: dict, db: Session = Depends(get_db)):
    comp = UIComponent(
        name=payload.get("name", "Nouveau Composant"),
        tags=payload.get("tags", "WXML"),
        author=payload.get("author", "AgentOps Dev"),
        initials=payload.get("initials", "DEV"),
        preview=payload.get("preview", "Preview UI"),
        code=payload.get("code", {"WXML": ""}),
        image_url=payload.get("image_url", "")
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return {"status": "success", "data": comp}
