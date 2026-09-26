import re

with open("apps/api/routers/ingest_api.py", "r", encoding="utf-8") as f:
    content = f.read()

# Ajouter l'import manquant de AgentSkill
content = content.replace(
    "from packages.database.sonatel_models import MemoryChunk",
    "from packages.database.sonatel_models import MemoryChunk, AgentSkill"
)

with open("apps/api/routers/ingest_api.py", "w", encoding="utf-8") as f:
    f.write(content)
