from packages.database.session import SessionLocal, engine
from packages.database.sonatel_models import Base, ComponentCategory

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    default_cats = ["Authentification", "Navigation", "Formulaires", "Paiement (Orange Money)", "Listes & Données"]
    for cat_name in default_cats:
        if not db.query(ComponentCategory).filter_by(name=cat_name).first():
            db.add(ComponentCategory(name=cat_name))
    db.commit()
    print("Catégories injectées !")
except Exception as e:
    print(e)
finally:
    db.close()
