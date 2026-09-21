from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    framework: Optional[str] = "WeChat Native"
    language: Optional[str] = "JavaScript"
    repository_url: str

class ProjectResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    framework: Optional[str]
    language: Optional[str]
    repository_url: Optional[str]
    created_at: datetime

    # Permet à Pydantic de lire directement depuis les objets SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
