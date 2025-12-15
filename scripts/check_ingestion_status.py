"""
Script para verificar o status da ingestão e coleções
"""
import sys
import os
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.rag.vector_store import VectorStore
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def check_collection_status(domain: str):
    """Verifica status de uma coleção"""
    try:
        vector_store = VectorStore()
        
        # Verificar se coleção existe
        try:
            info = vector_store.get_collection_info(domain)
            if info:
                points = info.get("points_count", 0)
                vectors = info.get("vectors_count", 0)
                
                print(f"\n{'='*60}")
                print(f"Coleção: {domain.upper()}")
                print(f"{'='*60}")
                print(f"[OK] Colecao existe")
                print(f"[INFO] Chunks indexados: {points}")
                print(f"[INFO] Vetores: {vectors}")
                
                if points > 0:
                    print(f"[OK] Colecao populada e pronta para uso!")
                else:
                    print(f"[AVISO] Colecao vazia - execute a ingestao primeiro")
                
                return points > 0
            else:
                print(f"[ERRO] Nao foi possivel obter informacoes da colecao")
                return False
        except Exception as e:
            print(f"[ERRO] Colecao '{domain}' nao existe ou erro ao acessar: {e}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao conectar com Qdrant: {e}")
        print(f"\nVerifique:")
        print(f"  - QDRANT_HOST está correto?")
        print(f"  - QDRANT_API_KEY está configurada? (se usar Qdrant Cloud)")
        print(f"  - Qdrant está rodando?")
        return False


def check_raw_files():
    """Verifica arquivos em data/raw"""
    settings = get_settings()
    raw_path = Path(settings.data_raw_path)
    
    if not raw_path.exists():
        print(f"\n[AVISO] Diretorio {raw_path} nao existe")
        return []
    
    files = list(raw_path.glob("*.pdf")) + list(raw_path.glob("*.html"))
    print(f"\n{'='*60}")
    print(f"Arquivos em {raw_path}")
    print(f"{'='*60}")
    print(f"[INFO] Total: {len(files)} arquivos")
    
    if files:
        for f in files[:10]:  # Mostrar primeiros 10
            print(f"  - {f.name}")
        if len(files) > 10:
            print(f"  ... e mais {len(files) - 10} arquivos")
    else:
        print("  [AVISO] Nenhum arquivo encontrado")
    
    return files


def check_processed_files():
    """Verifica arquivos em data/processed"""
    settings = get_settings()
    processed_path = Path(settings.data_processed_path)
    
    if not processed_path.exists():
        return []
    
    files = list(processed_path.glob("*.pdf")) + list(processed_path.glob("*.html"))
    print(f"\n{'='*60}")
    print(f"Arquivos processados em {processed_path}")
    print(f"{'='*60}")
    print(f"[OK] Total processados: {len(files)} arquivos")
    
    if files:
        for f in files[:10]:  # Mostrar primeiros 10
            print(f"  [OK] {f.name}")
        if len(files) > 10:
            print(f"  ... e mais {len(files) - 10} arquivos")
    
    return files


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("VERIFICACAO DE STATUS DA INGESTAO")
    print("="*60)
    
    # Verificar arquivos
    raw_files = check_raw_files()
    processed_files = check_processed_files()
    
    # Verificar coleções
    settings = get_settings()
    domains = settings.domain_list
    
    print(f"\n{'='*60}")
    print("STATUS DAS COLEÇÕES")
    print("="*60)
    
    all_ready = True
    for domain in domains:
        is_ready = check_collection_status(domain)
        if not is_ready:
            all_ready = False
    
    # Resumo
    print(f"\n{'='*60}")
    print("RESUMO")
    print("="*60)
    print(f"Arquivos brutos: {len(raw_files)}")
    print(f"Arquivos processados: {len(processed_files)}")
    
    if all_ready and len(processed_files) > 0:
        print(f"\n[OK] Sistema pronto para uso!")
        print(f"   Todas as colecoes estao populadas.")
    elif len(processed_files) > 0:
        print(f"\n[AVISO] Algumas colecoes ainda estao vazias.")
        print(f"   Execute a ingestao para os dominios faltantes.")
    elif len(raw_files) > 0:
        print(f"\n[AGUARDANDO] Ingestao em andamento ou nao iniciada.")
        print(f"   Aguarde a conclusao ou execute:")
        print(f"   python -m app.ingestion.main <domain>")
    else:
        print(f"\n[ERRO] Nenhum arquivo encontrado para processar.")
        print(f"   Baixe os documentos primeiro em {settings.data_raw_path}")
    
    print()


if __name__ == "__main__":
    main()

