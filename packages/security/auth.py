from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

security = HTTPBearer()

class CurrentUser(BaseModel):
    user_id: str
    organization_id: str
    roles: list[str]

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> CurrentUser:
    """
    Valide le Bearer Token (JWT).
    Dans l'application finale, on valide la signature cryptographique (via JWKS d'Auth0, Clerk ou Supabase).
    Ici, nous créons le stub (bouchon) pour l'architecture.
    """
    token = credentials.credentials
    
    # Simulation pour les tests
    if token == "DEV_TOKEN_ORG_A":
        return CurrentUser(user_id="dev_123", organization_id="org_A", roles=["developer"])
    if token == "DEV_TOKEN_ORG_B":
        return CurrentUser(user_id="dev_456", organization_id="org_B", roles=["developer"])
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou manquant",
        headers={"WWW-Authenticate": "Bearer"},
    )
