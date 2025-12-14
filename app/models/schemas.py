from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Metadata(BaseModel):
    """Metadados obrigatórios de cada chunk"""
    fonte: str = Field(..., description="Fonte do documento")
    norma: str = Field(..., description="Nome da norma (ex: Circular, Resolução)")
    numero_norma: str = Field(..., description="Número da norma")
    artigo: Optional[str] = Field(None, description="Número do artigo")
    ano: int = Field(..., description="Ano da norma")
    tema: str = Field(..., description="Tema: pix ou open_finance")
    url: Optional[str] = Field(None, description="URL do documento original")


class DocumentChunk(BaseModel):
    """Chunk de documento com metadados"""
    text: str
    metadata: Metadata
    chunk_id: Optional[str] = None
    score: Optional[float] = None


class ChatRequest(BaseModel):
    """Request para endpoint de chat"""
    question: str = Field(..., min_length=1, max_length=1000)
    domain: str = Field(..., pattern="^(pix|open_finance)$")
    top_k: Optional[int] = Field(None, ge=1, le=10)
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Response do endpoint de chat"""
    answer: str
    sources: List[DocumentChunk] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    has_sufficient_context: bool
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Response do health check"""
    status: str
    qdrant_connected: bool
    collections: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.now)


class ReindexResponse(BaseModel):
    """Response do reindex"""
    status: str
    message: str
    documents_processed: int
    chunks_created: int
    timestamp: datetime = Field(default_factory=datetime.now)

