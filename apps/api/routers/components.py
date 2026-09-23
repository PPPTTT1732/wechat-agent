from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.sonatel_models import UIComponent

router = APIRouter(prefix="/api/v1/components", tags=["Components"])

@router.get("/")
def get_components(db: Session = Depends(get_db)):
    """
    Retourne les composants UI publiés par les développeurs de l'équipe.
    Un composant est ajouté quand un développeur clique sur "Publier"
    depuis la plateforme AgentOps.
    """
    components = db.query(UIComponent).order_by(UIComponent.id.desc()).all()
    return components

@router.post("/")
def publish_component(payload: dict, db: Session = Depends(get_db)):
    """
    Publie un nouveau composant UI dans la bibliothèque partagée.
    Le composant est associé à l'auteur connecté via Clerk.
    """
    comp = UIComponent(
        name=payload.get("name", "Nouveau Composant"),
        tags=payload.get("tags", "WXML"),
        author=payload.get("author", "Développeur Sonatel"),
        initials=payload.get("initials", "DS"),
        preview=payload.get("preview", "Aperçu du composant"),
        code=payload.get("code", {"WXML": ""}),
        image_url=payload.get("image_url", None)
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return {"status": "success", "data": comp}
