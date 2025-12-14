import re
from typing import List, Dict, Any
from app.models.schemas import DocumentChunk


def validate_normative_reference(text: str) -> bool:
    """
    Valida se o texto contém referência normativa explícita.
    Procura por padrões como: artigo, art., inciso, parágrafo, etc.
    """
    patterns = [
        r'\b(artigo|art\.?)\s+\d+',
        r'\b(inciso|inc\.?)\s+[IVX]+',
        r'\b(parágrafo|par\.?)\s+\d+',
        r'\b(resolução|circular|comunicado)\s+\d+',
        r'\b(norma|normativo)',
    ]
    
    text_lower = text.lower()
    return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns)


def validate_response(
    response_text: str,
    sources: List[DocumentChunk],
    min_sources: int = 1
) -> Dict[str, Any]:
    """
    Valida resposta completa contra alucinação.
    Retorna dict com validações.
    """
    validations = {
        "has_normative_reference": validate_normative_reference(response_text),
        "has_article_citation": bool(re.search(r'\b(artigo|art\.?)\s+\d+', response_text, re.IGNORECASE)),
        "has_sufficient_sources": len(sources) >= min_sources,
        "is_valid": False,
    }
    
    # Resposta é válida se passar em todas as validações
    validations["is_valid"] = all([
        validations["has_normative_reference"],
        validations["has_article_citation"],
        validations["has_sufficient_sources"],
    ])
    
    return validations


def extract_citations(response_text: str, sources: List[DocumentChunk]) -> List[str]:
    """
    Extrai citações normativas da resposta e dos sources.
    """
    citations = []
    
    # Extrair do texto da resposta
    article_pattern = r'\b(artigo|art\.?)\s+(\d+)'
    matches = re.findall(article_pattern, response_text, re.IGNORECASE)
    for match in matches:
        citations.append(f"Art. {match[1]}")
    
    # Extrair dos metadados dos sources
    for source in sources:
        if source.metadata.artigo:
            citation = f"{source.metadata.norma} {source.metadata.numero_norma}/{source.metadata.ano}, Art. {source.metadata.artigo}"
            if citation not in citations:
                citations.append(citation)
    
    return list(set(citations))

