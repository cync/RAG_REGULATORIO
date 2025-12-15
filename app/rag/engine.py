from typing import List, Optional, Dict, Any
import time
from openai import OpenAI, RateLimitError
from app.rag.vector_store import VectorStore
from app.models.schemas import DocumentChunk
from app.config import get_settings
from app.utils.logger import get_logger
from app.utils.validators import validate_response, extract_citations

logger = get_logger(__name__)

SYSTEM_PROMPT = """Você é um especialista em regulação do Banco Central do Brasil,
com foco exclusivo em Pix e Open Finance.

Responda apenas com base nos trechos normativos fornecidos.
Não faça inferências, interpretações jurídicas ou extrapolações.

Se a resposta não estiver explicitamente nos documentos, diga:
"Não há base normativa explícita nos documentos analisados."

REGRAS OBRIGATÓRIAS DE CITAÇÃO:
- SEMPRE cite o ARTIGO usando o formato: "Art. X" ou "Artigo X"
- SEMPRE cite a NORMA (ex: "Instrução Normativa X", "Resolução X")
- SEMPRE cite o ANO
- Exemplo: "Conforme Art. 5 da Instrução Normativa 1/2020"

Formato obrigatório da resposta:

Resposta objetiva:
[Resposta direta à pergunta, citando Art. X da Norma Y/Ano]

Base normativa:
Art. X da Norma Y/Ano

Explicação técnica:
[Detalhamento técnico, sempre citando Art. X]
"""


class RegulatoryRAGEngine:
    """Engine RAG principal com validações anti-alucinação"""
    
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada. Configure a variável de ambiente.")
        
        self.vector_store = VectorStore()
        self.llm_client = OpenAI(api_key=self.settings.openai_api_key)
    
    def _build_context(self, chunks: List[DocumentChunk]) -> str:
        """Constrói contexto a partir dos chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Documento {i}]\n"
                f"Norma: {chunk.metadata.norma} {chunk.metadata.numero_norma}/{chunk.metadata.ano}\n"
                f"Artigo: {chunk.metadata.artigo or 'N/A'}\n"
                f"Tema: {chunk.metadata.tema}\n"
                f"Conteúdo:\n{chunk.text}\n"
            )
        
        return "\n---\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Constrói prompt completo"""
        return f"""Com base nos seguintes trechos normativos, responda à pergunta.

Trechos normativos:

{context}

Pergunta: {question}

INSTRUÇÕES OBRIGATÓRIAS:
1. Responda APENAS com base nos trechos fornecidos acima
2. SEMPRE cite o ARTIGO usando "Art. X" ou "Artigo X" na sua resposta
3. SEMPRE cite a NORMA (ex: "Instrução Normativa X", "Resolução X")
4. SEMPRE cite o ANO
5. Use o formato: "Conforme Art. X da Norma Y/Ano"
6. Se não houver base normativa nos trechos, diga explicitamente: "Não há base normativa explícita nos documentos analisados."
7. Não faça inferências ou interpretações jurídicas

EXEMPLO DE RESPOSTA CORRETA:
"Conforme Art. 5 da Instrução Normativa 1/2020, os PSPs têm a obrigação de..."

IMPORTANTE: Sua resposta DEVE conter pelo menos uma citação no formato "Art. X" ou "Artigo X" para ser válida.
"""
    
    def _call_llm(self, prompt: str) -> str:
        """Chama o LLM com retry para rate limits"""
        max_retries = 5
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.llm_client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.settings.max_tokens_response,
                    temperature=0.1,  # Baixa temperatura para respostas mais determinísticas
                )
                
                return response.choices[0].message.content.strip()
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Backoff exponencial
                    logger.warning(
                        "Rate limit no LLM, aguardando",
                        attempt=attempt + 1,
                        wait_seconds=wait_time
                    )
                    time.sleep(wait_time)
                else:
                    logger.error("Rate limit no LLM após múltiplas tentativas")
                    raise
            except Exception as e:
                logger.error("Erro ao chamar LLM", error=str(e))
                raise
    
    def query(
        self,
        question: str,
        domain: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executa query completa com validações.
        
        Returns:
            dict com answer, sources, citations, has_sufficient_context
        """
        # Parâmetros
        top_k = top_k or self.settings.top_k_results
        min_score = min_score or self.settings.min_similarity_score
        
        logger.info("Iniciando query RAG", question=question[:100], domain=domain)
        
        # 1. Buscar contexto
        sources = self.vector_store.search(
            collection_name=domain,
            query=question,
            top_k=top_k,
            min_score=min_score
        )
        
        # 2. Validar se há contexto suficiente
        if not sources or len(sources) == 0:
            logger.warning("Sem contexto suficiente", question=question[:100])
            return {
                "answer": "Não há base normativa explícita nos documentos analisados para responder a esta pergunta.",
                "sources": [],
                "citations": [],
                "has_sufficient_context": False,
            }
        
        # 3. Construir contexto e prompt
        context = self._build_context(sources)
        prompt = self._build_prompt(question, context)
        
        # 4. Chamar LLM
        answer = self._call_llm(prompt)
        
        # 5. Validar resposta
        validations = validate_response(answer, sources, min_sources=1)
        
        # 6. Se não passar validação, tentar extrair citações dos sources mesmo assim
        if not validations["is_valid"]:
            logger.warning(
                "Resposta não passou validação",
                validations=validations,
                question=question[:100],
                answer_preview=answer[:200] if answer else ""  # Log dos primeiros 200 chars para debug
            )
            
            # Extrair citações dos sources mesmo se a resposta não tiver
            citations = extract_citations(answer, sources)
            
            # Se tiver sources mas resposta não citou, incluir citações dos sources
            if sources and not citations:
                for source in sources:
                    if source.metadata.artigo:
                        citation = f"{source.metadata.norma} {source.metadata.numero_norma}/{source.metadata.ano}, Art. {source.metadata.artigo}"
                        citations.append(citation)
                citations = list(set(citations))
            
            # Retornar resposta mesmo sem validação, mas marcar como sem contexto suficiente
            # Converter sources para dict para compatibilidade com ChatResponse
            sources_dict = [s.metadata.model_dump() for s in sources]
            return {
                "answer": answer if answer else "Não há base normativa explícita nos documentos analisados para responder a esta pergunta.",
                "sources": sources_dict,
                "citations": citations,
                "has_sufficient_context": len(sources) > 0,  # Tem contexto se tem sources
            }
        
        # 7. Extrair citações
        citations = extract_citations(answer, sources)
        
        logger.info(
            "Query concluída",
            question=question[:100],
            sources_count=len(sources),
            has_citations=len(citations) > 0
        )
        
        # Converter sources para dict para compatibilidade com ChatResponse
        sources_dict = [s.metadata.model_dump() for s in sources]
        
        return {
            "answer": answer,
            "sources": sources_dict,
            "citations": citations,
            "has_sufficient_context": True,
        }

