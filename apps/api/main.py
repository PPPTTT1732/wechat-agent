from fastapi import FastAPI
from apps.api.routers import tasks

app = FastAPI(
    title="WeChat Engineering Intelligence API",
    description="Plateforme AgentOps pour l'écosystème WeChat",
    version="0.1.0"
)

# Inclusion des routes
app.include_router(tasks.router)

@app.get("/health", tags=["System"])
async def health_check():
    """Vérification de la santé du conteneur (pour Docker/Render)."""
    return {
        "status": "ok", 
        "service": "wechat-engineering-agent",
        "database": "unconnected",
        "worker": "unconnected"
    }
