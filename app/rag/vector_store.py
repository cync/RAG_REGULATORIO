from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
import time
from app.models.schemas import DocumentChunk, Metadata
from app.config import get_settings
from app.utils.logger import get_logger
from openai import OpenAI, RateLimitError

logger = get_logger(__name__)


class VectorStore:
    """Gerenciador do Qdrant para armazenamento vetorial"""
    
    def __init__(self):
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada. Configure a variável de ambiente.")
        
        # Configurar Qdrant com API key se disponível
        is_cloud = "cloud.qdrant.io" in settings.qdrant_host or "gcp.cloud.qdrant.io" in settings.qdrant_host
        
        # Qdrant Cloud sempre requer API key
        qdrant_api_key = settings.qdrant_api_key or getattr(settings, 'qdrant_api_key', None) or ""
        qdrant_api_key = qdrant_api_key.strip() if qdrant_api_key else ""
        
        if is_cloud and not qdrant_api_key:
            logger.error(
                "Qdrant Cloud detectado mas QDRANT_API_KEY não configurada",
                host=settings.qdrant_host
            )
            raise ValueError(
                "QDRANT_API_KEY é obrigatória para Qdrant Cloud. "
                "Configure no arquivo .env: QDRANT_API_KEY=sua-api-key"
            )
        
        # Para Qdrant Cloud, usar URL sem porta
        if is_cloud:
            # Remover porta da URL se houver
            qdrant_url = settings.qdrant_url.replace(":6333", "").replace(":6334", "")
            qdrant_kwargs = {
                "url": qdrant_url,
                "api_key": qdrant_api_key,
                "timeout": 30,
                "check_compatibility": False
            }
        else:
            # Qdrant local
            qdrant_kwargs = {
                "url": settings.qdrant_url,
                "timeout": 30,
                "check_compatibility": False
            }
            if qdrant_api_key:
                qdrant_kwargs["api_key"] = qdrant_api_key
        
        logger.info(
            "Configurando Qdrant",
            url=qdrant_kwargs["url"],
            has_api_key=bool(qdrant_api_key),
            is_cloud=is_cloud,
            host=settings.qdrant_host
        )
        
        self.client = QdrantClient(**qdrant_kwargs)
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = settings.embedding_model
        self.settings = settings
    
    def ensure_collection(self, collection_name: str):
        """Cria coleção se não existir"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if collection_name not in collection_names:
                # Criar coleção
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=3072,  # text-embedding-3-large
                        distance=Distance.COSINE
                    )
                )
                logger.info("Coleção criada", collection=collection_name)
            else:
                logger.info("Coleção já existe", collection=collection_name)
        except Exception as e:
            logger.error("Erro ao criar coleção", collection=collection_name, error=str(e))
            raise
    
    def delete_collection(self, collection_name: str):
        """Deleta coleção"""
        try:
            self.client.delete_collection(collection_name)
            logger.info("Coleção deletada", collection=collection_name)
        except Exception as e:
            logger.warning("Erro ao deletar coleção (pode não existir)", collection=collection_name, error=str(e))
    
    def index_chunks(self, collection_name: str, chunks: List[DocumentChunk]):
        """Indexa chunks na coleção"""
        if not chunks:
            return
        
        points = []
        
        for i, chunk in enumerate(chunks):
            # Gerar embedding usando OpenAI diretamente com retry
            max_retries = 5
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = self.openai_client.embeddings.create(
                        model=self.embedding_model,
                        input=chunk.text
                    )
                    embedding = response.data[0].embedding
                    break
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Backoff exponencial
                        logger.warning(
                            "Rate limit atingido, aguardando",
                            attempt=attempt + 1,
                            wait_seconds=wait_time,
                            chunk_index=i
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error("Rate limit após múltiplas tentativas", chunk_index=i)
                        raise
                except Exception as e:
                    logger.error("Erro ao gerar embedding", error=str(e), chunk_index=i)
                    raise
            
            # Pequeno delay entre requisições para evitar rate limit
            if i < len(chunks) - 1:
                time.sleep(0.1)  # 100ms entre requisições
            
            # Criar ponto
            point_id = str(uuid.uuid4())
            chunk.chunk_id = point_id
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "fonte": chunk.metadata.fonte,
                    "norma": chunk.metadata.norma,
                    "numero_norma": chunk.metadata.numero_norma,
                    "artigo": chunk.metadata.artigo or "",
                    "ano": chunk.metadata.ano,
                    "tema": chunk.metadata.tema,
                    "url": chunk.metadata.url or "",
                }
            )
            points.append(point)
        
        # Inserir em batch
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info("Chunks indexados", collection=collection_name, count=len(points))
        except Exception as e:
            logger.error("Erro ao indexar chunks", collection=collection_name, error=str(e))
            raise
    
    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        min_score: float = 0.7
    ) -> List[DocumentChunk]:
        """Busca semântica na coleção"""
        try:
            # Gerar embedding da query usando OpenAI diretamente com retry
            max_retries = 5
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = self.openai_client.embeddings.create(
                        model=self.embedding_model,
                        input=query
                    )
                    query_embedding = response.data[0].embedding
                    break
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Backoff exponencial
                        logger.warning(
                            "Rate limit na busca, aguardando",
                            attempt=attempt + 1,
                            wait_seconds=wait_time
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error("Rate limit após múltiplas tentativas na busca")
                        raise
                except Exception as e:
                    logger.error("Erro ao gerar embedding da query", error=str(e))
                    raise
            
            # Buscar
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=min_score
            )
            
            # Converter para DocumentChunk
            chunks = []
            for result in results:
                payload = result.payload
                chunk = DocumentChunk(
                    text=payload.get("text", ""),
                    metadata=Metadata(
                        fonte=payload.get("fonte", ""),
                        norma=payload.get("norma", ""),
                        numero_norma=payload.get("numero_norma", ""),
                        artigo=payload.get("artigo"),
                        ano=payload.get("ano", 2023),
                        tema=payload.get("tema", ""),
                        url=payload.get("url"),
                    ),
                    chunk_id=str(result.id),
                    score=result.score
                )
                chunks.append(chunk)
            
            logger.info(
                "Busca realizada",
                collection=collection_name,
                query_length=len(query),
                results=len(chunks)
            )
            
            return chunks
            
        except Exception as e:
            logger.error("Erro na busca", collection=collection_name, error=str(e))
            return []
    
    def get_collection_info(self, collection_name: str) -> Optional[dict]:
        """Retorna informações da coleção"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
            }
        except Exception as e:
            logger.warning("Erro ao obter info da coleção", collection=collection_name, error=str(e))
            return None

