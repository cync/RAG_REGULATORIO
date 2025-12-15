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

IMPORTANTE: Você receberá trechos normativos que FORAM ENCONTRADOS como relevantes para a pergunta.
Estes trechos CONTÊM informações sobre o tema perguntado.

SUA TAREFA: Responder a pergunta usando as informações dos trechos fornecidos.

REGRAS OBRIGATÓRIAS:
1. SEMPRE use as informações dos trechos fornecidos para responder
2. SEMPRE cite o artigo usando "Art. X" ou "Artigo X" na sua resposta
3. SEMPRE cite a norma completa (ex: "Instrução Normativa 1/2020" ou "Circular 1/2020")
4. SEMPRE cite o ano
5. Use o formato: "Conforme Art. X da [Norma] Y/Ano, ..." ou similar

Se realmente não conseguir encontrar informação relevante nos trechos, diga:
"Não há base normativa explícita nos documentos analisados para responder a esta pergunta."
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
            # Construir referência normativa completa
            norma_ref = f"{chunk.metadata.norma} {chunk.metadata.numero_norma}/{chunk.metadata.ano}"
            artigo_ref = f"Art. {chunk.metadata.artigo}" if chunk.metadata.artigo else "Sem artigo específico"
            
            context_parts.append(
                f"[Documento {i}]\n"
                f"Referência Normativa: {norma_ref}, {artigo_ref}\n"
                f"Tema: {chunk.metadata.tema}\n"
                f"Conteúdo:\n{chunk.text}\n"
            )
        
        context_str = "\n---\n\n".join(context_parts)
        
        # Log do contexto para debug (primeiros 500 chars)
        logger.debug(
            "Contexto construído para LLM",
            context_length=len(context_str),
            chunks_count=len(chunks),
            context_preview=context_str[:500]
        )
        
        return context_str
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Constrói prompt completo"""
        return f"""TRECHOS NORMATIVOS ENCONTRADOS (USE ESTAS INFORMAÇÕES PARA RESPONDER):

{context}

PERGUNTA: {question}

INSTRUÇÕES OBRIGATÓRIAS:

1. Os trechos acima FORAM ENCONTRADOS como relevantes para a pergunta "{question}".
2. Eles CONTÊM informações que respondem à pergunta. ANALISE-OS CUIDADOSAMENTE.
3. EXTRAIA informações dos trechos e responda a pergunta usando essas informações.

4. FORMATO OBRIGATÓRIO DA RESPOSTA:
   - SEMPRE comece com: "Conforme Art. [NÚMERO] da [NORMA] [NÚMERO]/[ANO]"
   - Use as informações do trecho para responder
   - Cite o artigo usando "Art. X" ou "Artigo X"
   - Mencione a norma completa e o ano

5. EXEMPLO DE RESPOSTA CORRETA:
   "Conforme Art. 5 da Instrução Normativa 1/2020, os PSPs têm a obrigação de implementar sistemas de segurança adequados para operações no Pix, conforme estabelecido no trecho acima."

6. IMPORTANTE: 
   - Os trechos FORAM SELECIONADOS como relevantes
   - Eles CONTÊM informações sobre a pergunta
   - USE as informações dos trechos para responder
   - NÃO diga que não há base normativa sem analisar cuidadosamente todos os trechos primeiro

7. Se REALMENTE não conseguir extrair informação relevante dos trechos (após analisar todos), diga:
   "Não há base normativa explícita nos documentos analisados para responder a esta pergunta."

Sua resposta DEVE começar com uma citação no formato "Conforme Art. X da [Norma] Y/Ano" se houver qualquer informação relevante nos trechos.

RESPONDA AGORA:
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
        
        # 6. Extrair citações dos sources (sempre, mesmo se resposta não citar)
        citations = extract_citations(answer, sources)
        
        # Se tiver sources mas resposta não citou, incluir citações dos sources
        if sources and not citations:
            for source in sources:
                if source.metadata.artigo:
                    citation = f"{source.metadata.norma} {source.metadata.numero_norma}/{source.metadata.ano}, Art. {source.metadata.artigo}"
                    citations.append(citation)
            citations = list(set(citations))
        
        # Converter sources para dict para compatibilidade com ChatResponse
        sources_dict = [s.metadata.model_dump() for s in sources]
        
        # 7. Se não passar validação, retornar resposta mas com aviso
        if not validations["is_valid"]:
            logger.warning(
                "Resposta não passou validação",
                validations=validations,
                question=question[:100],
                answer_preview=answer[:200] if answer else "",  # Log dos primeiros 200 chars para debug
                sources_count=len(sources),
                citations_count=len(citations)
            )
            
            # Retornar resposta mesmo sem validação, mas incluir citações dos sources
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

