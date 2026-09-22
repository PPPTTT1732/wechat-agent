import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Enum, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
import enum

class Base(DeclarativeBase):
    pass

class ChunkStatus(str, enum.Enum):
    PROPOSED = "proposed"
    OBSERVED = "observed"
    VALIDATED = "validated"
    TRUSTED = "trusted"
    SHARED = "shared"

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text)
    # Changement ici : 384 dimensions pour HuggingFace (all-MiniLM-L6-v2) au lieu de 1536
    embedding: Mapped[Vector] = mapped_column(Vector(384))
    status: Mapped[ChunkStatus] = mapped_column(Enum(ChunkStatus), default=ChunkStatus.PROPOSED)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
