"""
Script alternativo para baixar normas do Pix.
Tenta acessar URLs conhecidas do Banco Central.
"""
import requests
from pathlib import Path
import time

OUTPUT_DIR = Path("data/raw/pix")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# URLs conhecidas de documentos do Pix (você pode adicionar mais)
KNOWN_PIX_DOCUMENTS = [
    # Adicione aqui URLs diretas de PDFs do Pix que você encontrar
    # Exemplo:
    # "https://www.bcb.gov.br/estabilidadefinanceira/pix/documentos/circular_xxx.pdf",
]

def download_file(url: str, filename: str = None) -> bool:
    """Baixa um arquivo"""
    try:
        if not filename:
            filename = url.split('/')[-1] or "documento.pdf"
        
        output_path = OUTPUT_DIR / filename
        
        if output_path.exists():
            print(f"  ⊙ Já existe: {filename}")
            return True
        
        print(f"Baixando: {url}")
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✓ Salvo: {filename}")
        return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("Download Manual de Normas do Pix")
    print("=" * 60)
    print()
    print("Este script tenta baixar de URLs conhecidas.")
    print("Para adicionar mais URLs, edite o arquivo e adicione em KNOWN_PIX_DOCUMENTS")
    print()
    
    if not KNOWN_PIX_DOCUMENTS:
        print("⚠️  Nenhuma URL configurada.")
        print()
        print("Para usar este script:")
        print("1. Acesse: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas")
        print("2. Encontre os links dos PDFs (clique com botão direito → Copiar endereço do link)")
        print("3. Adicione as URLs no arquivo scripts/download_pix_normas_manual.py")
        print("4. Execute novamente este script")
        return
    
    downloaded = 0
    for i, url in enumerate(KNOWN_PIX_DOCUMENTS, 1):
        print(f"[{i}/{len(KNOWN_PIX_DOCUMENTS)}]")
        if download_file(url):
            downloaded += 1
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"Download concluído: {downloaded}/{len(KNOWN_PIX_DOCUMENTS)}")
    print(f"Diretório: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()

