"""
Script para mover PDFs escaneados para uma pasta separada
para focar apenas nos HTMLs da API
"""
import sys
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def clean_pdfs(domain: str = "pix"):
    """Move PDFs escaneados para pasta separada"""
    raw_path = project_root / "data" / "raw" / domain
    pdfs_backup = project_root / "data" / "raw" / domain / "_pdfs_escaneados"
    
    if not raw_path.exists():
        print(f"❌ Diretório não encontrado: {raw_path}")
        return
    
    # Criar pasta de backup
    pdfs_backup.mkdir(exist_ok=True)
    
    # Listar PDFs
    pdfs = list(raw_path.glob("*.pdf"))
    
    if not pdfs:
        print(f"✅ Nenhum PDF encontrado em {raw_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Movendo PDFs escaneados para backup")
    print(f"{'='*60}")
    print(f"PDFs encontrados: {len(pdfs)}")
    
    moved = 0
    for pdf in pdfs:
        try:
            target = pdfs_backup / pdf.name
            pdf.rename(target)
            print(f"  ✅ {pdf.name}")
            moved += 1
        except Exception as e:
            print(f"  ❌ Erro ao mover {pdf.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ {moved} PDF(s) movido(s) para {pdfs_backup}")
    print(f"📁 Mantendo apenas HTMLs em {raw_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else "pix"
    clean_pdfs(domain)

