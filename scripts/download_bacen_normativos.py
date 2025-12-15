"""
Script para baixar e normalizar normativos do Banco Central via API oficial.

Uso:
    python scripts/download_bacen_normativos.py pix
    python scripts/download_bacen_normativos.py open_finance
    python scripts/download_bacen_normativos.py --tipo "Instrução Normativa BCB" --numero 513
"""
import sys
import argparse
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ingestion.bacen_normativos import main, process_normativo
from app.config import get_settings
from app.utils.logger import setup_logger, get_logger

# Configurar logger
setup_logger()
logger = get_logger(__name__)


# Listas de normativos conhecidos por domínio
NORMATIVOS_PIX = [
    ("Instrução Normativa BCB", 513),
    ("Instrução Normativa BCB", 512),
    ("Instrução Normativa BCB", 511),
    ("Instrução Normativa BCB", 508),
    ("Instrução Normativa BCB", 491),
    ("Instrução Normativa BCB", 412),
    ("Instrução Normativa BCB", 243),
    ("Instrução Normativa BCB", 200),
    ("Instrução Normativa BCB", 199),
    ("Instrução Normativa BCB", 198),
    ("Instrução Normativa BCB", 32),
    ("Instrução Normativa BCB", 19),
    ("Instrução Normativa BCB", 16),
    ("Instrução Normativa BCB", 1),
    ("Resolução BCB", 264),
    ("Resolução BCB", 1),
]

NORMATIVOS_OPEN_FINANCE = [
    ("Resolução BCB", 1),  # Exemplo - ajustar conforme necessário
]


def download_by_domain(domain: str):
    """Baixa normativos de um domínio específico."""
    settings = get_settings()
    output_dir = Path(settings.data_raw_path)
    
    if domain == "pix":
        normativos = NORMATIVOS_PIX
    elif domain == "open_finance":
        normativos = NORMATIVOS_OPEN_FINANCE
    else:
        logger.error("Domínio inválido", domain=domain)
        print(f"❌ Domínio inválido: {domain}")
        print("Use: pix ou open_finance")
        return
    
    print(f"\n{'='*60}")
    print(f"Baixando normativos: {domain.upper()}")
    print(f"{'='*60}")
    print(f"Total: {len(normativos)} normativos\n")
    
    results = main(normativos, str(output_dir))
    
    # Resumo
    successful = sum(1 for r in results if r.get("success"))
    print(f"\n{'='*60}")
    print(f"✅ Concluído: {successful}/{len(normativos)} normativos processados")
    print(f"{'='*60}\n")


def download_single(tipo: str, numero: int):
    """Baixa um normativo específico."""
    settings = get_settings()
    output_dir = Path(settings.data_raw_path)
    
    print(f"\n{'='*60}")
    print(f"Baixando normativo: {tipo} {numero}")
    print(f"{'='*60}\n")
    
    result = process_normativo(tipo, numero, output_dir / "temp")
    
    if result.get("success"):
        print(f"✅ Sucesso!")
        print(f"   Título: {result.get('titulo', 'N/A')}")
        print(f"   Artigos: {result.get('artigos_encontrados', 0)}")
        print(f"   Chunks salvos: {result.get('chunks_salvos', 0)}")
    else:
        print(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")
    
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Baixa e normaliza normativos do Banco Central via API oficial"
    )
    parser.add_argument(
        "domain",
        nargs="?",
        choices=["pix", "open_finance"],
        help="Domínio para baixar normativos"
    )
    parser.add_argument(
        "--tipo",
        type=str,
        help="Tipo do normativo (ex: 'Instrução Normativa BCB')"
    )
    parser.add_argument(
        "--numero",
        type=int,
        help="Número do normativo"
    )
    
    args = parser.parse_args()
    
    if args.tipo and args.numero:
        # Baixar normativo específico
        download_single(args.tipo, args.numero)
    elif args.domain:
        # Baixar por domínio
        download_by_domain(args.domain)
    else:
        parser.print_help()
        print("\nExemplos:")
        print("  python scripts/download_bacen_normativos.py pix")
        print("  python scripts/download_bacen_normativos.py --tipo 'Instrução Normativa BCB' --numero 513")

