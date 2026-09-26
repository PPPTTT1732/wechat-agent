with open("apps/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

if "import ingest_api" not in content:
    content = content.replace(
        "from apps.api.routers import components, devops, team, twin, auth",
        "from apps.api.routers import components, devops, team, twin, auth, ingest_api"
    )
    content = content.replace(
        "app.include_router(auth.router)",
        "app.include_router(auth.router)\napp.include_router(ingest_api.router)"
    )
    
    with open("apps/api/main.py", "w", encoding="utf-8") as f:
        f.write(content)
