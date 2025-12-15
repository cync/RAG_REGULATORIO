from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
import time
from app.models.schemas import DocumentChunk, Metadata
from app.config import get_settings
from app.utils.logger import get_logger
from openai import OpenAI, RateLimitError
import tenacity

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
        
        # Validar API key para Qdrant Cloud
        if is_cloud:
            if not qdrant_api_key or len(qdrant_api_key) < 10:
                logger.error(
                    "Qdrant Cloud detectado mas QDRANT_API_KEY inválida ou vazia",
                    host=settings.qdrant_host,
                    api_key_length=len(qdrant_api_key) if qdrant_api_key else 0
                )
                raise ValueError(
                    "QDRANT_API_KEY é obrigatória e deve ser válida para Qdrant Cloud. "
                    "Configure no arquivo .env: QDRANT_API_KEY=sua-api-key-completa"
                )
        
        # Para Qdrant Cloud, usar URL sem porta
        if is_cloud:
            # Remover porta da URL se houver e garantir formato correto
            qdrant_url = settings.qdrant_url.replace(":6333", "").replace(":6334", "")
            # Garantir que não tenha porta após o hostname
            if "://" in qdrant_url:
                protocol, rest = qdrant_url.split("://", 1)
                if ":" in rest and not rest.split(":")[0].endswith(".io"):
                    # Tem porta, remover
                    hostname = rest.split(":")[0]
                    qdrant_url = f"{protocol}://{hostname}"
            
            # Para Qdrant Cloud, garantir URL sem porta
            # Remover qualquer porta que possa ter sobrado
            if ":6333" in qdrant_url or ":6334" in qdrant_url:
                # Remover porta explicitamente
                qdrant_url = re.sub(r':\d+$', '', qdrant_url.split('://')[1])
                qdrant_url = f"https://{qdrant_url}"
            
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
            has_api_key=bool(qdrant_api_key and len(qdrant_api_key) > 10),
            api_key_length=len(qdrant_api_key) if qdrant_api_key else 0,
            is_cloud=is_cloud,
            host=settings.qdrant_host
        )
        
        self.client = QdrantClient(**qdrant_kwargs)
        
        # Testar conexão se for Cloud
        if is_cloud:
            try:
                # Tentar uma operação simples para validar autenticação
                self.client.get_collections()
                logger.info("Conexão com Qdrant Cloud validada com sucesso")
            except Exception as e:
                logger.error(
                    "Erro ao validar conexão com Qdrant Cloud",
                    error=str(e),
                    url=qdrant_url
                )
                raise ValueError(
                    f"Falha na autenticação com Qdrant Cloud: {str(e)}\n"
                    "Verifique se QDRANT_API_KEY está correta no arquivo .env"
                )
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
    
    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=16),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type(RateLimitError),
        before_sleep=tenacity.before_sleep_log(logger, "info"),
        reraise=True
    )
    def _get_embedding_with_retry(self, text: str) -> List[float]:
        """Tenta obter embedding com retry em caso de RateLimitError."""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
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
        min_score: float = 0.15  # Reduzido para 0.15 - scores de similaridade estão em ~0.19
    ) -> List[DocumentChunk]:
        """Busca semântica na coleção"""
        try:
            # Verificar se a coleção existe e tem documentos
            try:
                collection_info = self.client.get_collection(collection_name)
                if collection_info.points_count == 0:
                    logger.warning(
                        "Coleção vazia - nenhum documento indexado",
                        collection=collection_name,
                        query=query[:100]
                    )
                    return []
            except Exception as e:
                logger.warning(
                    "Erro ao verificar coleção (pode não existir)",
                    collection=collection_name,
                    error=str(e)
                )
                return []
            
            # Gerar embedding da query usando função com retry unificado
            query_embedding = self._get_embedding_with_retry(query)
            
            # Buscar usando query_points() - método atual do qdrant-client >= 1.7
            # Verificar dimensão do embedding
            embedding_dim = len(query_embedding)
            logger.debug(
                "Gerando query de busca",
                collection=collection_name,
                embedding_dim=embedding_dim,
                query_length=len(query)
            )
            
            # Para coleções simples (sem named vectors), usar lista diretamente
            try:
                # Tentar primeiro com lista direta (mais simples)
                # Remover score_threshold para ver todos os resultados
                query_result = self.client.query_points(
                    collection_name=collection_name,
                    query=query_embedding,  # Lista de floats diretamente
                    limit=top_k
                    # score_threshold removido para debug
                )
            except (TypeError, ValueError) as e:
                logger.warning("Erro ao buscar com lista direta, tentando NamedVector", error=str(e))
                # Se não funcionar, tentar com NamedVector
                from qdrant_client.models import NamedVector
                query_result = self.client.query_points(
                    collection_name=collection_name,
                    query=NamedVector(
                        name="",  # Nome vazio para vetor padrão
                        vector=query_embedding
                    ),
                    limit=top_k
                    # score_threshold removido para debug
                )
            
            # query_points retorna um objeto QueryResponse com .points
            all_points = query_result.points if hasattr(query_result, 'points') else []
            
            # Filtrar por score_threshold manualmente
            results = []
            for point in all_points:
                score = point.score if hasattr(point, 'score') else 0.0
                if score >= min_score:
                    results.append(point)
            
            logger.info(
                "Busca realizada",
                collection=collection_name,
                query_length=len(query),
                total_points=len(all_points),
                filtered_results=len(results),
                min_score=min_score,
                scores=[p.score for p in all_points[:5]] if all_points and hasattr(all_points[0], 'score') else []
            )
            
            # Converter para DocumentChunk
            chunks = []
            for result in results:
                # Result pode ser ScoredPoint ou dict
                if hasattr(result, 'payload'):
                    payload = result.payload
                    point_id = result.id
                    score = result.score
                else:
                    # Se for dict
                    payload = result.get('payload', {})
                    point_id = result.get('id')
                    score = result.get('score', 0.0)
                
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
                    chunk_id=str(point_id),
                    score=score
                )
                chunks.append(chunk)
            
            # Log já feito acima
            
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
                "vectors_count": getattr(info, 'vectors_count', info.points_count),  # Fallback se não existir
            }
        except Exception as e:
            logger.warning("Erro ao obter info da coleção", collection=collection_name, error=str(e))
            return None

