"""
Script para resetar a ingestão - move arquivos de volta para data/raw
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

from app.config import get_settings

def reset_ingestion(domain: str):
    """Move arquivos de processed de volta para raw"""
    # Sempre usar a raiz do projeto como base
    project_root = Path(__file__).parent.parent
    settings = get_settings()
    
    # Construir caminhos a partir da raiz do projeto
    raw_path = (project_root / settings.data_raw_path / domain).resolve()
    processed_path = (project_root / settings.data_processed_path / domain).resolve()
    
    print(f"\n{'='*60}")
    print(f"Resetando ingestão para domínio: {domain.upper()}")
    print(f"{'='*60}")
    print(f"Diretório raw: {raw_path}")
    print(f"Diretório processed: {processed_path}")
    print(f"{'='*60}\n")
    
    if not processed_path.exists():
        print(f"[AVISO] Diretório {processed_path} não existe")
        print(f"[INFO] Verificando se há arquivos em {raw_path}...")
        
        # Se processed não existe, verificar se os arquivos já estão em raw
        if raw_path.exists():
            files = list(raw_path.glob("*.pdf")) + list(raw_path.glob("*.html")) + list(raw_path.glob("*.htm"))
            if files:
                print(f"[INFO] Encontrados {len(files)} arquivo(s) em {raw_path}")
                print(f"[INFO] Os arquivos já estão em raw, prontos para reingestão!")
                return
            else:
                print(f"[ERRO] Nenhum arquivo encontrado em {raw_path}")
                print(f"[INFO] Coloque os arquivos PDF/HTML em {raw_path} antes de executar a ingestão")
                return
        else:
            print(f"[ERRO] Diretório {raw_path} também não existe")
            print(f"[INFO] Criando diretório {raw_path}...")
            raw_path.mkdir(parents=True, exist_ok=True)
            print(f"[INFO] Coloque os arquivos PDF/HTML em {raw_path} antes de executar a ingestão")
            return
    
    # Listar arquivos processados
    files = list(processed_path.glob("*.pdf")) + list(processed_path.glob("*.html")) + list(processed_path.glob("*.htm"))
    
    if not files:
        print(f"[AVISO] Nenhum arquivo encontrado em {processed_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Resetando ingestão para domínio: {domain.upper()}")
    print(f"{'='*60}")
    print(f"Arquivos encontrados: {len(files)}")
    
    # Criar diretório raw se não existir
    raw_path.mkdir(parents=True, exist_ok=True)
    
    # Mover arquivos de volta
    moved = 0
    for file_path in files:
        try:
            target = raw_path / file_path.name
            if target.exists():
                print(f"[AVISO] {file_path.name} já existe em raw, pulando...")
                continue
            
            file_path.rename(target)
            moved += 1
            print(f"[OK] Movido: {file_path.name}")
        except Exception as e:
            print(f"[ERRO] Erro ao mover {file_path.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"[OK] {moved} arquivo(s) movido(s) de volta para {raw_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/reset_ingestion.py <domain>")
        print("Exemplo: python scripts/reset_ingestion.py pix")
        sys.exit(1)
    
    domain = sys.argv[1]
    reset_ingestion(domain)

