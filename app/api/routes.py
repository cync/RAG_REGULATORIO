from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, ReindexResponse
from app.rag.engine import RegulatoryRAGEngine
from app.rag.vector_store import VectorStore
from app.ingestion.main import ingest_documents
from app.config import get_settings
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_rag_engine() -> RegulatoryRAGEngine:
    """Dependency para RAG engine"""
    return RegulatoryRAGEngine()


def get_vector_store() -> VectorStore:
    """Dependency para vector store"""
    return VectorStore()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    engine: RegulatoryRAGEngine = Depends(get_rag_engine)
):
    """
    Endpoint principal de chat.
    Recebe pergunta e retorna resposta baseada em documentos normativos.
    """
    try:
        logger.info(
            "Nova consulta recebida",
            question=request.question[:100],
            domain=request.domain
        )
        
        # Executar query
        result = engine.query(
            question=request.question,
            domain=request.domain,
            top_k=request.top_k,
            min_score=request.min_score
        )
        
        # Log de auditoria
        logger.info(
            "Consulta processada",
            question=request.question,
            domain=request.domain,
            has_sufficient_context=result["has_sufficient_context"],
            sources_count=len(result["sources"]),
            citations=result["citations"],
            timestamp=datetime.now().isoformat()
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            citations=result["citations"],
            has_sufficient_context=result["has_sufficient_context"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(
            "Erro ao processar consulta",
            question=request.question[:100],
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Erro ao processar consulta: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health(vector_store: VectorStore = Depends(get_vector_store)):
    """
    Health check do sistema.
    Verifica conexão com Qdrant e status das coleções.
    """
    settings = get_settings()
    
    try:
        # Verificar conexão Qdrant
        collections_info = {}
        qdrant_connected = False
        
        try:
            collections = vector_store.client.get_collections().collections
            qdrant_connected = True
            
            for domain in settings.domain_list:
                collection_info = vector_store.get_collection_info(domain)
                collections_info[domain] = collection_info is not None and collection_info.get("points_count", 0) > 0
        except Exception as e:
            logger.warning("Erro ao verificar Qdrant", error=str(e))
            for domain in settings.domain_list:
                collections_info[domain] = False
        
        status = "healthy" if qdrant_connected and any(collections_info.values()) else "degraded"
        
        return HealthResponse(
            status=status,
            qdrant_connected=qdrant_connected,
            collections=collections_info,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error("Erro no health check", error=str(e))
        return HealthResponse(
            status="unhealthy",
            qdrant_connected=False,
            collections={},
            timestamp=datetime.now()
        )


@router.post("/reindex", response_model=ReindexResponse)
async def reindex(
    domain: str = "pix",
    force: bool = True
):
    """
    Reindexa documentos de um domínio.
    """
    settings = get_settings()
    
    if domain not in settings.domain_list:
        raise HTTPException(status_code=400, detail=f"Domínio inválido: {domain}")
    
    try:
        logger.info("Iniciando reindexação", domain=domain, force=force)
        
        # Executar ingestão
        ingest_documents(domain, force_reindex=force)
        
        # Obter estatísticas
        vector_store = VectorStore()
        collection_info = vector_store.get_collection_info(domain)
        chunks_count = collection_info.get("points_count", 0) if collection_info else 0
        
        # Contar arquivos processados (aproximação)
        from pathlib import Path
        processed_path = Path(settings.data_processed_path) / domain
        files_count = len(list(processed_path.glob("*.pdf"))) + len(list(processed_path.glob("*.html")))
        
        logger.info("Reindexação concluída", domain=domain, chunks=chunks_count)
        
        return ReindexResponse(
            status="success",
            message=f"Reindexação concluída para domínio {domain}",
            documents_processed=files_count,
            chunks_created=chunks_count,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error("Erro na reindexação", domain=domain, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro na reindexação: {str(e)}")

