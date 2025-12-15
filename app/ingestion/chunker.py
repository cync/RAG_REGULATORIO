import re
import tiktoken
from typing import List, Optional
from app.models.schemas import DocumentChunk, Metadata
from app.utils.logger import get_logger

logger = get_logger(__name__)


class JuridicalChunker:
    """
    Chunker especializado em documentos jurídicos.
    Divide por artigo, preservando estrutura normativa.
    """
    
    def __init__(self, max_tokens: int = 600):
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4")
    
    def count_tokens(self, text: str) -> int:
        """Conta tokens usando tiktoken"""
        return len(self.encoding.encode(text))
    
    def split_by_article(self, text: str) -> List[tuple[str, Optional[str]]]:
        """
        Divide texto por artigos.
        Retorna lista de (texto, número_artigo).
        """
        # Padrão para encontrar artigos
        article_pattern = r'(?i)(Art\.?\s*\d+[º°]?)\s*[–-]?\s*'
        
        articles = []
        matches = list(re.finditer(article_pattern, text))
        
        if not matches:
            # Se não encontrar artigos, retorna texto inteiro
            return [(text, None)]
        
        for i, match in enumerate(matches):
            start = match.start()
            
            # Determinar fim do artigo
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)
            
            article_text = text[start:end].strip()
            article_num = match.group(1)
            # Limpar número do artigo
            article_num_clean = re.sub(r'(?i)art\.?\s*', '', article_num).strip()
            
            articles.append((article_text, article_num_clean))
        
        return articles
    
    def split_article_by_inciso(self, article_text: str, article_num: str) -> List[tuple[str, str]]:
        """
        Divide artigo por incisos se necessário.
        Retorna lista de (texto, identificador_completo).
        """
        # Padrão para incisos romanos
        inciso_pattern = r'(?i)([IVX]+[º°]?)\s*[–-]?\s*'
        
        incisos = []
        matches = list(re.finditer(inciso_pattern, article_text))
        
        if not matches:
            return [(article_text, f"Art. {article_num}")]
        
        for i, match in enumerate(matches):
            start = match.start()
            
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(article_text)
            
            inciso_text = article_text[start:end].strip()
            inciso_num = match.group(1)
            identifier = f"Art. {article_num}, {inciso_num}"
            
            incisos.append((inciso_text, identifier))
        
        return incisos
    
    def chunk(self, text: str, base_metadata: dict) -> List[DocumentChunk]:
        """
        Chunking jurídico principal.
        Divide por artigo, e por inciso se necessário.
        """
        chunks = []
        articles = self.split_by_article(text)
        
        for article_text, article_num in articles:
            # Verificar se precisa dividir por inciso
            tokens = self.count_tokens(article_text)
            
            if tokens <= self.max_tokens:
                # Artigo cabe em um chunk
                metadata = Metadata(
                    **base_metadata,
                    artigo=article_num
                )
                chunks.append(DocumentChunk(
                    text=article_text,
                    metadata=metadata
                ))
            else:
                # Dividir por inciso
                incisos = self.split_article_by_inciso(article_text, article_num or "N/A")
                
                for inciso_text, identifier in incisos:
                    inciso_tokens = self.count_tokens(inciso_text)
                    
                    if inciso_tokens <= self.max_tokens:
                        metadata = Metadata(
                            **base_metadata,
                            artigo=identifier
                        )
                        chunks.append(DocumentChunk(
                            text=inciso_text,
                            metadata=metadata
                        ))
                    else:
                        # Se ainda for muito grande, dividir por parágrafos ou truncar
                        # Por segurança, truncar mantendo início
                        truncated = inciso_text[:self.max_tokens * 4]  # Aproximação
                        metadata = Metadata(
                            **base_metadata,
                            artigo=identifier
                        )
                        chunks.append(DocumentChunk(
                            text=truncated,
                            metadata=metadata
                        ))
                        logger.warning(
                            "Chunk truncado por exceder limite",
                            identifier=identifier,
                            tokens=inciso_tokens
                        )
        
        # Validar chunks
        valid_chunks = []
        for chunk in chunks:
            # Se o chunk tem artigo no metadata, já é uma referência normativa válida
            if chunk.metadata.artigo:
                valid_chunks.append(chunk)
            # Se não tem artigo mas contém referência normativa no texto, também é válido
            elif self._has_normative_reference(chunk.text):
                valid_chunks.append(chunk)
            # Se não tem artigo nem referência, mas tem norma/numero_norma, aceitar (pode ser introdução/preâmbulo)
            elif chunk.metadata.norma or chunk.metadata.numero_norma:
                logger.debug(
                    "Chunk aceito sem artigo explícito (pode ser preâmbulo/introdução)",
                    norma=chunk.metadata.norma,
                    numero_norma=chunk.metadata.numero_norma
                )
                valid_chunks.append(chunk)
            else:
                logger.warning(
                    "Chunk sem referência normativa removido",
                    chunk_id=chunk.chunk_id,
                    norma=chunk.metadata.norma,
                    artigo=chunk.metadata.artigo
                )
        
        logger.info("Chunking concluído", total_chunks=len(valid_chunks))
        return valid_chunks
    
    def _has_normative_reference(self, text: str) -> bool:
        """Verifica se texto contém referência normativa"""
        # Padrões mais flexíveis para documentos normativos
        patterns = [
            r'(?i)\b(artigo|art\.?)\s+\d+',  # Artigo
            r'(?i)\b(inciso|inc\.?)\s+[IVX]+',  # Inciso
            r'(?i)\b(parágrafo|par\.?)\s+\d+',  # Parágrafo
            r'(?i)\b(resolução|circular|comunicado|instrução)',  # Tipos de norma
            r'(?i)\b(norma|normativo|regulamenta)',  # Termos normativos
            r'(?i)\b(bacen|banco\s+central)',  # Referência ao Bacen
            r'(?i)\b(pix|open\s+finance)',  # Temas específicos
            r'(?i)\b(obrigação|dever|proibição|permissão)',  # Termos jurídicos
        ]
        text_lower = text.lower()
        # Verificar se tem pelo menos 50 caracteres e algum padrão
        if len(text.strip()) < 50:
            return False
        return any(re.search(pattern, text_lower) for pattern in patterns)

