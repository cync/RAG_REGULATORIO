"""
Módulo de Download e Normalização de Normativos do Banco Central do Brasil

Este módulo consome a API oficial do Bacen para baixar, normalizar e preparar
normativos para indexação em sistemas RAG.

API Oficial: https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from app.utils.logger import get_logger

logger = get_logger(__name__)

# URL base da API oficial do Banco Central
API_BASE_URL = "https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo"


def fetch_normativo(tipo: str, numero: int) -> Dict:
    """
    Busca normativo na API oficial do Banco Central.
    
    Args:
        tipo: Tipo do normativo (ex: "Instrução Normativa BCB", "Resolução BCB")
        numero: Número do normativo (ex: 513)
    
    Returns:
        dict: Conteúdo completo do normativo (conteudo[0])
    
    Raises:
        requests.HTTPError: Se a requisição falhar
        ValueError: Se o normativo não for encontrado
    """
    params = {
        "p1": tipo,
        "p2": numero
    }
    
    logger.info(
        "Buscando normativo na API do Bacen",
        tipo=tipo,
        numero=numero
    )
    
    try:
        response = requests.get(API_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Validar estrutura da resposta
        if not isinstance(data, dict):
            raise ValueError(f"Resposta da API em formato inesperado: {type(data)}")
        
        if "conteudo" not in data:
            raise ValueError("Resposta da API não contém campo 'conteudo'")
        
        if not data["conteudo"] or len(data["conteudo"]) == 0:
            raise ValueError(
                f"Normativo não encontrado: {tipo} {numero}. "
                "Verifique se o tipo e número estão corretos."
            )
        
        normativo = data["conteudo"][0]
        
        logger.info(
            "Normativo encontrado",
            tipo=tipo,
            numero=numero,
            titulo=normativo.get("Titulo", "N/A")[:100]
        )
        
        return normativo
        
    except requests.exceptions.RequestException as e:
        logger.error(
            "Erro ao buscar normativo na API",
            tipo=tipo,
            numero=numero,
            error=str(e)
        )
        raise
    except (KeyError, IndexError, ValueError) as e:
        logger.error(
            "Erro ao processar resposta da API",
            tipo=tipo,
            numero=numero,
            error=str(e)
        )
        raise ValueError(f"Erro ao processar normativo {tipo} {numero}: {e}")


def normalize_html(html: str) -> str:
    """
    Normaliza HTML preservando estrutura jurídica.
    
    Remove tags desnecessárias, texto revogado e normaliza formatação,
    mantendo artigos, parágrafos e incisos.
    
    Args:
        html: HTML bruto do normativo
    
    Returns:
        str: Texto normalizado e limpo
    """
    if not html or not html.strip():
        logger.warning("HTML vazio recebido para normalização")
        return ""
    
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Remover completamente texto revogado (tag <s>)
        for revoked in soup.find_all("s"):
            revoked.decompose()
        
        # Remover tags que não contêm conteúdo útil
        for tag in soup.find_all(["script", "style", "noscript"]):
            tag.decompose()
        
        # Processar tags de formatação: substituir por texto, não remover
        # Isso preserva o conteúdo dentro de span, div, font, etc.
        for tag in soup.find_all(["span", "div", "font"]):
            # Se a tag tem apenas texto (sem filhos), substituir pelo texto
            if not tag.find_all():
                text = tag.get_text(strip=True)
                if text:
                    tag.replace_with(text)
                else:
                    tag.decompose()
            # Se tem filhos, manter estrutura mas remover atributos
            else:
                # Remover apenas atributos, manter conteúdo
                tag.attrs = {}
        
        # Converter quebras de linha para \n
        for br in soup.find_all("br"):
            br.replace_with("\n")
        
        # Processar parágrafos: preservar conteúdo
        for p in soup.find_all("p"):
            text = p.get_text(separator=" ", strip=True)
            if text:
                # Adicionar quebra de linha após parágrafo
                p.replace_with(f"{text}\n")
            else:
                p.decompose()
        
        # Extrair texto preservando quebras de linha
        # Usar get_text com separator para preservar estrutura
        text = soup.get_text(separator="\n", strip=True)
        
        # Se ainda estiver vazio, tentar método alternativo
        if not text or len(text.strip()) < 50:
            logger.warning("Texto extraído muito curto, tentando método alternativo")
            # Tentar extrair diretamente do body ou html
            body = soup.find("body") or soup
            text = body.get_text(separator="\n", strip=True)
        
        # Normalizar múltiplas quebras de linha (máximo 2 consecutivas)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Normalizar espaços múltiplos dentro de linhas
        lines = text.split('\n')
        normalized_lines = []
        for line in lines:
            # Preservar espaços iniciais (para indentação de incisos)
            leading_spaces = len(line) - len(line.lstrip())
            # Normalizar espaços múltiplos no conteúdo
            content = re.sub(r' +', ' ', line.strip())
            if content:
                normalized_lines.append(' ' * leading_spaces + content)
            else:
                normalized_lines.append('')
        
        text = '\n'.join(normalized_lines)
        
        # Remover linhas vazias excessivas no início e fim
        text = text.strip()
        
        # Validar que tem conteúdo
        text_non_whitespace = text.replace('\n', '').replace(' ', '').replace('\t', '').strip()
        
        logger.debug(
            "HTML normalizado",
            original_length=len(html),
            normalized_length=len(text),
            non_whitespace_length=len(text_non_whitespace)
        )
        
        if len(text_non_whitespace) < 50:
            logger.warning(
                "Texto normalizado muito curto após processamento",
                original_length=len(html),
                normalized_length=len(text),
                non_whitespace_length=len(text_non_whitespace)
            )
        
        return text
        
    except Exception as e:
        logger.error("Erro ao normalizar HTML", error=str(e))
        # Fallback: extrair texto básico sem processamento complexo
        try:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup.find_all(["s", "script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            logger.info("Usando fallback de extração de texto", text_length=len(text))
            return text
        except Exception as e2:
            logger.error("Erro no fallback de extração", error=str(e2))
            return ""


def chunk_by_article(text: str) -> List[Tuple[str, str]]:
    """
    Divide texto normativo por artigos.
    
    Cada chunk contém exatamente um artigo, preservando incisos e parágrafos.
    
    Args:
        text: Texto normalizado do normativo
    
    Returns:
        List[Tuple[str, str]]: Lista de (artigo_numero, artigo_texto)
    """
    if not text or not text.strip():
        logger.warning("Texto vazio recebido para chunking")
        return []
    
    # Padrão para encontrar artigos
    # Aceita: Art. 1, Art. 1º, Artigo 1, ART. 1, etc.
    article_pattern = r'(?i)(Art\.?\s*\d+[º°]?)\s*[–-]?\s*'
    
    articles = []
    matches = list(re.finditer(article_pattern, text))
    
    if not matches:
        logger.warning("Nenhum artigo encontrado no texto")
        # Se não encontrar artigos, retornar texto inteiro como único chunk
        return [("", text)]
    
    for i, match in enumerate(matches):
        start = match.start()
        
        # Determinar fim do artigo (início do próximo ou fim do texto)
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)
        
        article_text = text[start:end].strip()
        
        # Extrair número do artigo
        article_num = match.group(1)
        article_num_clean = re.sub(r'(?i)art\.?\s*', '', article_num).strip()
        article_num_clean = re.sub(r'[º°]', '', article_num_clean).strip()
        
        if article_text and len(article_text) > 10:
            articles.append((article_num_clean, article_text))
            logger.debug(
                "Artigo extraído",
                artigo=article_num_clean,
                tamanho=len(article_text)
            )
    
    logger.info(
        "Chunking por artigos concluído",
        total_artigos=len(articles)
    )
    
    return articles


def build_metadata(normativo: Dict, artigo: str) -> Dict:
    """
    Constrói metadados completos para um chunk de artigo.
    
    Args:
        normativo: Dados completos do normativo da API
        artigo: Número do artigo (string vazia se não houver)
    
    Returns:
        dict: Metadados estruturados
    """
    # Construir URL oficial do normativo
    tipo = normativo.get("Tipo", "")
    numero = normativo.get("Numero", "")
    
    # URL base do Bacen para normativos
    url_base = "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo"
    url = f"{url_base}?tipo={tipo}&numero={numero}" if tipo and numero else ""
    
    metadata = {
        "fonte": "BACEN",
        "tipo": tipo,
        "numero": str(numero) if numero else "",
        "titulo": normativo.get("Titulo", ""),
        "artigo": artigo if artigo else None,
        "data_publicacao": normativo.get("Data", ""),
        "versao": normativo.get("VersaoNormativo", ""),
        "revogado": normativo.get("Revogado", False),
        "cancelado": normativo.get("Cancelado", False),
        "atualizacoes": normativo.get("Atualizacoes", []),
        "assunto": normativo.get("Assunto", ""),
        "url": url,
        "tema": _infer_theme(normativo),  # Pix ou Open Finance
        "ano": _extract_year(normativo.get("Data", ""))
    }
    
    return metadata


def _infer_theme(normativo: Dict) -> str:
    """Infere o tema (pix ou open_finance) baseado no conteúdo."""
    text = (
        normativo.get("Titulo", "") + " " +
        normativo.get("Assunto", "") + " " +
        normativo.get("Texto", "")
    ).lower()
    
    if any(keyword in text for keyword in ["pix", "pagamento instantâneo", "pagamento instantaneo"]):
        return "pix"
    elif any(keyword in text for keyword in ["open finance", "open banking", "dados abertos", "compartilhamento de dados"]):
        return "open_finance"
    else:
        return "outros"


def _extract_year(data_str: str) -> int:
    """Extrai ano da data de publicação."""
    if not data_str:
        return datetime.now().year
    
    # Tentar extrair ano de vários formatos
    year_match = re.search(r'\d{4}', data_str)
    if year_match:
        try:
            return int(year_match.group())
        except ValueError:
            pass
    
    return datetime.now().year


def save_chunks(chunks: List[Dict], output_dir: Path, normativo_info: Dict) -> int:
    """
    Salva chunks como arquivos JSON prontos para indexação RAG.
    
    Args:
        chunks: Lista de chunks com estrutura {"text": str, "metadata": dict}
        output_dir: Diretório de saída
        normativo_info: Informações do normativo para nomear arquivos
    
    Returns:
        int: Número de arquivos salvos
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tipo = normativo_info.get("Tipo", "Normativo").replace(" ", "_")
    numero = normativo_info.get("Numero", "N/A")
    ano = _extract_year(normativo_info.get("Data", ""))
    
    saved = 0
    
    for i, chunk in enumerate(chunks):
        artigo = chunk["metadata"].get("artigo", "")
        
        # Nome do arquivo: Tipo_Numero_Ano_Art_X.json
        if artigo:
            filename = f"{tipo}_{numero}_{ano}_Art_{artigo}.json"
        else:
            filename = f"{tipo}_{numero}_{ano}_preambulo.json"
        
        # Limpar caracteres inválidos do nome do arquivo
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        file_path = output_dir / filename
        
        # Verificar se já existe (idempotência)
        if file_path.exists():
            logger.debug("Arquivo já existe, pulando", file=str(file_path))
            continue
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            
            saved += 1
            logger.debug(
                "Chunk salvo",
                file=filename,
                artigo=artigo,
                tamanho=len(chunk["text"])
            )
        except Exception as e:
            logger.error(
                "Erro ao salvar chunk",
                file=filename,
                error=str(e)
            )
    
    logger.info(
        "Chunks salvos",
        total=len(chunks),
        salvos=saved,
        diretorio=str(output_dir)
    )
    
    return saved


def process_normativo(tipo: str, numero: int, output_dir: Path) -> Dict:
    """
    Processa um normativo completo: download, normalização e chunking.
    
    Args:
        tipo: Tipo do normativo
        numero: Número do normativo
        output_dir: Diretório de saída
    
    Returns:
        dict: Estatísticas do processamento
    """
    logger.info(
        "Iniciando processamento de normativo",
        tipo=tipo,
        numero=numero
    )
    
    try:
        # 1. Buscar normativo na API
        normativo = fetch_normativo(tipo, numero)
        
        # 2. Extrair e normalizar HTML
        html_text = normativo.get("Texto", "")
        if not html_text:
            raise ValueError("Normativo não contém texto (campo 'Texto' vazio)")
        
        normalized_text = normalize_html(html_text)
        
        if not normalized_text or len(normalized_text.strip()) < 50:
            raise ValueError("Texto normalizado muito curto ou vazio")
        
        # 3. Dividir por artigos
        articles = chunk_by_article(normalized_text)
        
        if not articles:
            raise ValueError("Nenhum artigo encontrado após chunking")
        
        # 4. Construir chunks com metadados
        chunks = []
        for artigo_num, artigo_text in articles:
            metadata = build_metadata(normativo, artigo_num)
            chunks.append({
                "text": artigo_text,
                "metadata": metadata
            })
        
        # 5. Salvar chunks
        saved = save_chunks(chunks, output_dir, normativo)
        
        return {
            "success": True,
            "tipo": tipo,
            "numero": numero,
            "titulo": normativo.get("Titulo", ""),
            "artigos_encontrados": len(articles),
            "chunks_salvos": saved,
            "texto_tamanho": len(normalized_text)
        }
        
    except Exception as e:
        logger.error(
            "Erro ao processar normativo",
            tipo=tipo,
            numero=numero,
            error=str(e)
        )
        return {
            "success": False,
            "tipo": tipo,
            "numero": numero,
            "error": str(e)
        }


def main(normativos: List[Tuple[str, int]], output_base_dir: str = "data/raw"):
    """
    Função principal que executa o pipeline completo.
    
    Args:
        normativos: Lista de tuplas (tipo, numero) para processar
        output_base_dir: Diretório base de saída
    """
    logger.info(
        "Iniciando pipeline de download e normalização",
        total_normativos=len(normativos),
        output_dir=output_base_dir
    )
    
    results = []
    output_base = Path(output_base_dir)
    
    for i, (tipo, numero) in enumerate(normativos, 1):
        logger.info(
            "Processando normativo",
            progress=f"{i}/{len(normativos)}",
            tipo=tipo,
            numero=numero
        )
        
        # Determinar diretório de saída baseado no tema
        # Será inferido durante o processamento
        temp_output = output_base / "temp"
        result = process_normativo(tipo, numero, temp_output)
        
        # Mover para diretório correto baseado no tema
        if result["success"]:
            # Inferir tema do primeiro chunk
            chunks_files = list(temp_output.glob("*.json"))
            if chunks_files:
                try:
                    with open(chunks_files[0], 'r', encoding='utf-8') as f:
                        chunk_data = json.load(f)
                        tema = chunk_data["metadata"].get("tema", "outros")
                    
                    final_output = output_base / tema
                    final_output.mkdir(parents=True, exist_ok=True)
                    
                    # Mover arquivos
                    for chunk_file in chunks_files:
                        target = final_output / chunk_file.name
                        if not target.exists():  # Idempotência
                            chunk_file.rename(target)
                        else:
                            chunk_file.unlink()  # Remover duplicado
                    
                    # Limpar diretório temp se vazio
                    try:
                        if temp_output.exists() and not list(temp_output.iterdir()):
                            temp_output.rmdir()
                    except:
                        pass
                except Exception as e:
                    logger.warning(
                        "Erro ao mover arquivos para diretório final",
                        error=str(e)
                    )
        
        results.append(result)
    
    # Resumo final
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    
    logger.info(
        "Pipeline concluído",
        total=len(results),
        sucesso=successful,
        falhas=failed
    )
    
    # Log de erros
    if failed > 0:
        logger.warning("Normativos com erro:")
        for result in results:
            if not result.get("success"):
                logger.warning(
                    "  - {} {}: {}".format(
                        result.get("tipo", "N/A"),
                        result.get("numero", "N/A"),
                        result.get("error", "Erro desconhecido")
                    )
                )
    
    return results


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo: processar algumas normas do Pix
    normativos_pix = [
        ("Instrução Normativa BCB", 513),
        ("Instrução Normativa BCB", 512),
        ("Resolução BCB", 264),
    ]
    
    main(normativos_pix)

