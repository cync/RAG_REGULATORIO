"""
Script para baixar automaticamente as normas do Pix do site do Banco Central.
URL: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
"""
import sys
import io
# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
        
        print(f"  [OK] Salvo: {output_path.name}")
        return True
    except Exception as e:
        print(f"  [ERRO] Erro ao baixar {url}: {e}")
        return False

def extract_document_links(html_content: str, base_url: str) -> list:
    """Extrai links de documentos (PDF, HTML) da página"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    seen_urls = set()
    
    # Estratégia 1: Procurar por links diretos de PDF
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if not href or href.startswith('#'):
            continue
        
        # Links absolutos ou relativos
        full_url = urljoin(base_url, href)
        
        # Evitar duplicatas
        if full_url in seen_urls:
            continue
        
        # Verificar se é um documento PDF/HTML
        if any(ext in href.lower() for ext in ['.pdf', '.html', '.htm']):
            seen_urls.add(full_url)
            links.append({
                'url': full_url,
                'text': text or os.path.basename(urlparse(full_url).path),
                'filename': os.path.basename(urlparse(full_url).path) or f"documento_{len(links)}.pdf"
            })
            continue
        
        # Estratégia 2: Procurar por links que contenham palavras-chave normativas
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ['circular', 'resolução', 'comunicado', 'norma', 'instrução', 'pix']):
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                # Tentar determinar extensão pela URL ou assumir PDF
                filename = os.path.basename(urlparse(full_url).path)
                if not filename or '.' not in filename:
                    filename = f"{text[:50].replace('/', '_')}.pdf"
                links.append({
                    'url': full_url,
                    'text': text,
                    'filename': filename
                })
    
    # Estratégia 3: Procurar por iframes ou objetos que possam conter PDFs
    for iframe in soup.find_all(['iframe', 'embed', 'object']):
        src = iframe.get('src') or iframe.get('data')
        if src:
            full_url = urljoin(base_url, src)
            if '.pdf' in full_url.lower() and full_url not in seen_urls:
                seen_urls.add(full_url)
                links.append({
                    'url': full_url,
                    'text': 'Documento PDF',
                    'filename': os.path.basename(urlparse(full_url).path) or "documento.pdf"
                })
    
    # Estratégia 4: Procurar por padrões de URL do Bacen
    # O Bacen geralmente usa padrões como: /estabilidadefinanceira/pix/arquivos/...
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if '/arquivos/' in href or '/normas/' in href or '/pix/' in href:
            full_url = urljoin(base_url, href)
            if full_url not in seen_urls and ('.pdf' in href.lower() or 'download' in href.lower()):
                seen_urls.add(full_url)
                text = link.get_text(strip=True) or 'Documento'
                links.append({
                    'url': full_url,
                    'text': text,
                    'filename': os.path.basename(urlparse(full_url).path) or f"{text[:50]}.pdf"
                })
    
    # Estratégia 5: Procurar por divs/seções que possam conter links
    # Muitas vezes os links estão em estruturas específicas
    for section in soup.find_all(['div', 'section', 'article'], class_=lambda x: x and any(
        keyword in str(x).lower() for keyword in ['documento', 'norma', 'arquivo', 'download', 'pdf']
    )):
        for link in section.find_all('a', href=True):
            href = link.get('href', '')
            if href and not href.startswith('#'):
                full_url = urljoin(base_url, href)
                if full_url not in seen_urls and ('.pdf' in href.lower() or any(
                    kw in link.get_text(strip=True).lower() for kw in ['circular', 'resolução', 'pdf']
                )):
                    seen_urls.add(full_url)
                    text = link.get_text(strip=True) or 'Documento'
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
            print("[AVISO] Nenhum link de documento encontrado automaticamente na pagina.")
            print()
            print("Possíveis causas:")
            print("  - A página carrega links via JavaScript (requer Selenium)")
            print("  - Os links estão em formato diferente")
            print()
            print("Solução alternativa:")
            print("  1. Acesse manualmente: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas")
            print("  2. Baixe os PDFs manualmente")
            print(f"  3. Coloque em: {OUTPUT_DIR}")
            print()
            print("Ou tente usar o script com Selenium:")
            print("  pip install selenium webdriver-manager")
            print("  python scripts/download_pix_normas_selenium.py")
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
                print(f"  [EXISTE] Ja existe: {output_path.name}")
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
        print(f"[ERRO] Erro ao acessar a pagina: {e}")
        print()
        print("Solução alternativa:")
        print("1. Acesse manualmente: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas")
        print("2. Baixe os PDFs manualmente")
        print(f"3. Coloque em: {OUTPUT_DIR}")
    except Exception as e:
        print(f"[ERRO] Erro: {e}")

if __name__ == "__main__":
    main()

