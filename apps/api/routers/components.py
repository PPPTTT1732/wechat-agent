from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from packages.database.session import get_db
from packages.database.sonatel_models import UIComponent, ComponentCategory
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/components", tags=["Components"])

class CategoryCreate(BaseModel):
    name: str

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(ComponentCategory).all()
    return cats

@router.post("/categories")
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(ComponentCategory).filter(ComponentCategory.name == payload.name).first()
    if existing:
        return existing
    cat = ComponentCategory(name=payload.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/")
def get_components(category: str = None, db: Session = Depends(get_db)):
    query = db.query(UIComponent)
    # Dans un système complet on lierait par ID, ici on filtre simplement par tag contenant la catégorie
    if category and category != "Tous":
        query = query.filter(UIComponent.tags.ilike(f"%{category}%"))
    return query.order_by(UIComponent.id.desc()).all()

@router.post("/")
def publish_component(payload: dict, db: Session = Depends(get_db)):
    category = payload.get("category", "")
    tags = f"WXML · {category}" if category else "WXML"
    
    comp = UIComponent(
        name=payload.get("name", "Nouveau Composant"),
        tags=tags,
        author=payload.get("author", "Développeur Sonatel"),
        initials=payload.get("initials", "DS"),
        preview=payload.get("preview", "Aperçu du composant")
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return {"status": "success", "data": comp}
