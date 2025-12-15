import sys
from pathlib import Path
from typing import List
from app.ingestion.document_parser import DocumentParser
from app.ingestion.chunker import JuridicalChunker
from app.rag.vector_store import VectorStore
from app.config import get_settings
from app.utils.logger import setup_logger, get_logger

# Garantir que logger está configurado
setup_logger()

logger = get_logger(__name__)


def ingest_documents(domain: str, force_reindex: bool = False):
    """
    Pipeline completo de ingestão.
    
    Args:
        domain: pix ou open_finance
        force_reindex: Se True, recria a coleção
    """
    settings = get_settings()
    parser = DocumentParser()
    chunker = JuridicalChunker(max_tokens=600)
    vector_store = VectorStore()
    
    # Caminhos
    raw_path = Path(settings.data_raw_path) / domain
    processed_path = Path(settings.data_processed_path) / domain
    
    if not raw_path.exists():
        logger.error("Diretório não encontrado", path=str(raw_path))
        return
    
    raw_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)
    
    # Listar arquivos
    files = list(raw_path.glob("*.pdf")) + list(raw_path.glob("*.html")) + list(raw_path.glob("*.htm"))
    
    if not files:
        logger.warning("Nenhum arquivo encontrado", domain=domain, path=str(raw_path))
        return
    
    logger.info("Iniciando ingestão", domain=domain, files_count=len(files))
    
    # Criar/limpar coleção se necessário
    if force_reindex:
        vector_store.delete_collection(domain)
    
    vector_store.ensure_collection(domain)
    
    total_chunks = 0
    
    for i, file_path in enumerate(files, 1):
        try:
            logger.info(
                "Processando arquivo",
                file=str(file_path),
                progress=f"{i}/{len(files)}",
                total_files=len(files)
            )
            
            # Parse
            text, base_metadata = parser.parse(file_path, tema=domain)
            
            # Chunking
            chunks = chunker.chunk(text, base_metadata)
            
            logger.info(
                "Chunks criados, iniciando indexação",
                file=str(file_path),
                chunks_count=len(chunks),
                progress=f"{i}/{len(files)}"
            )
            
            # Só indexar e mover se tiver chunks válidos
            if chunks:
                # Indexar (pode demorar devido a rate limits)
                vector_store.index_chunks(domain, chunks)
                
                total_chunks += len(chunks)
                
                # Mover para processados apenas se indexou com sucesso
                processed_file = processed_path / file_path.name
                if not processed_file.exists():
                    file_path.rename(processed_file)
            else:
                logger.warning(
                    "Arquivo processado mas sem chunks válidos - não será movido",
                    file=str(file_path)
                )
            
            logger.info(
                "Arquivo processado com sucesso",
                file=str(file_path),
                chunks=len(chunks),
                total_chunks_so_far=total_chunks,
                progress=f"{i}/{len(files)}",
                remaining=len(files) - i
            )
            
        except Exception as e:
            logger.error(
                "Erro ao processar arquivo",
                file=str(file_path),
                error=str(e),
                exc_info=True
            )
            continue
    
    logger.info(
        "Ingestão concluída",
        domain=domain,
        files_processed=len(files),
        total_chunks=total_chunks
    )


def main():
    """Entry point para ingestão"""
    setup_logger()
    settings = get_settings()
    
    if len(sys.argv) > 1:
        domain = sys.argv[1]
        if domain not in settings.domain_list:
            logger.error("Domínio inválido", domain=domain, valid=settings.domain_list)
            sys.exit(1)
    else:
        # Processar todos os domínios
        domain = None
    
    force_reindex = "--force" in sys.argv
    
    if domain:
        ingest_documents(domain, force_reindex)
    else:
        for d in settings.domain_list:
            ingest_documents(d, force_reindex)


if __name__ == "__main__":
    main()

