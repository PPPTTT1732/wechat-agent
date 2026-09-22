from fastapi import FastAPI
from apps.api.routers import memory

app = FastAPI(title="WeChat AgentOps API")

app.include_router(memory.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Le Cerveau d'Équipe AgentOps est en ligne !"}
