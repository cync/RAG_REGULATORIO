"""
Script para baixar automaticamente as normas do Pix do site do Banco Central.
URL: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
from urllib.parse import urljoin, urlparse
import os

# Configurações
BCB_PIX_URL = "https://www.bcb.gov.br/estabilidadefinanceira/pix-normas"
OUTPUT_DIR = Path("data/raw/pix")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, output_path: Path) -> bool:
    """Baixa um arquivo da URL"""
    try:
        print(f"Baixando: {url}")
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Verificar se é PDF ou HTML
        content_type = response.headers.get('content-type', '')
        if 'pdf' in content_type.lower():
            output_path = output_path.with_suffix('.pdf')
        elif 'html' in content_type.lower():
            output_path = output_path.with_suffix('.html')
        
        # Salvar arquivo
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✓ Salvo: {output_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Erro ao baixar {url}: {e}")
        return False

def extract_document_links(html_content: str, base_url: str) -> list:
    """Extrai links de documentos (PDF, HTML) da página"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    
    # Procurar por links de documentos
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # Links absolutos ou relativos
        full_url = urljoin(base_url, href)
        
        # Verificar se é um documento
        if any(ext in href.lower() for ext in ['.pdf', '.html', '.htm']):
            links.append({
                'url': full_url,
                'text': text,
                'filename': os.path.basename(urlparse(full_url).path) or f"documento_{len(links)}.pdf"
            })
        
        # Também procurar por links que contenham palavras-chave
        if any(keyword in text.lower() for keyword in ['circular', 'resolução', 'comunicado', 'norma', 'instrução']):
            if href and not href.startswith('#'):
                full_url = urljoin(base_url, href)
                if full_url not in [l['url'] for l in links]:
                    links.append({
                        'url': full_url,
                        'text': text,
                        'filename': os.path.basename(urlparse(full_url).path) or f"{text[:50]}.pdf"
                    })
    
    return links

def main():
    """Função principal"""
    print("=" * 60)
    print("Download de Normas do Pix - Banco Central do Brasil")
    print("=" * 60)
    print(f"URL: {BCB_PIX_URL}")
    print(f"Diretório de saída: {OUTPUT_DIR}")
    print()
    
    try:
        # Fazer requisição à página
        print("Acessando página do Banco Central...")
        response = requests.get(BCB_PIX_URL, timeout=30)
        response.raise_for_status()
        
        # Extrair links de documentos
        print("Extraindo links de documentos...")
        links = extract_document_links(response.text, BCB_PIX_URL)
        
        if not links:
            print("⚠️  Nenhum link de documento encontrado na página.")
            print("   Você pode baixar manualmente os PDFs e colocá-los em:")
            print(f"   {OUTPUT_DIR}")
            return
        
        print(f"Encontrados {len(links)} documentos potenciais.")
        print()
        
        # Baixar documentos
        downloaded = 0
        for i, link_info in enumerate(links, 1):
            print(f"[{i}/{len(links)}] {link_info['text'][:60]}")
            
            # Criar nome de arquivo seguro
            filename = "".join(c for c in link_info['filename'] if c.isalnum() or c in (' ', '-', '_', '.')).strip()
            if not filename:
                filename = f"documento_{i}"
            
            output_path = OUTPUT_DIR / filename
            
            # Não baixar se já existe
            if output_path.exists():
                print(f"  ⊙ Já existe: {output_path.name}")
                continue
            
            if download_file(link_info['url'], output_path):
                downloaded += 1
            
            # Delay para não sobrecarregar o servidor
            time.sleep(1)
        
        print()
        print("=" * 60)
        print(f"Download concluído!")
        print(f"  Total de links: {len(links)}")
        print(f"  Documentos baixados: {downloaded}")
        print(f"  Diretório: {OUTPUT_DIR}")
        print()
        print("Próximo passo: Execute a ingestão:")
        print("  python -m app.ingestion.main pix")
        print("=" * 60)
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao acessar a página: {e}")
        print()
        print("Solução alternativa:")
        print("1. Acesse manualmente: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas")
        print("2. Baixe os PDFs manualmente")
        print(f"3. Coloque em: {OUTPUT_DIR}")
    except Exception as e:
        print(f"✗ Erro: {e}")

if __name__ == "__main__":
    main()

