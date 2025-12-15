"""
Script simplificado para executar ingestão
Pode ser executado de qualquer lugar
"""
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Agora importar e executar
from app.ingestion.main import ingest_documents

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/ingest.py <domain>")
        print("Exemplo: python scripts/ingest.py pix")
        sys.exit(1)
    
    domain = sys.argv[1]
    print(f"Iniciando ingestão para domínio: {domain}")
    ingest_documents(domain)

