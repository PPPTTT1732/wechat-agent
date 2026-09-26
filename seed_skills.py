from packages.database.session import SessionLocal, engine
from packages.database.sonatel_models import Base, AgentSkill

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.query(AgentSkill).count() == 0:
        db.add_all([
            AgentSkill(title="Pourquoi utilise-t-on une queue durable pour les workflows ?", description="Cette règle validée décrit les décisions techniques et les garde-fous adoptés par l’équipe Platform...", category="Architecture / Workflows", author="Marie Laurent"),
            AgentSkill(title="Standards d'accessibilité WXML", description="Lors de la création de composants de paiement, toujours ajouter aria-label et utiliser les couleurs accessibles.", category="UI / Frontend", author="Malick Sy")
        ])
        db.commit()
        print("Skills par défaut injectés.")
except Exception as e:
    print(e)
finally:
    db.close()
