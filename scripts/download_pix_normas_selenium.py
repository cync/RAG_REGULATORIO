"""
Script alternativo usando Selenium para renderizar JavaScript.
Use se o script básico não encontrar links.
Requer: pip install selenium webdriver-manager
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import requests
from urllib.parse import urljoin, urlparse
import os

BCB_PIX_URL = "https://www.bcb.gov.br/estabilidadefinanceira/pix-normas"
OUTPUT_DIR = Path("data/raw/pix")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, output_path: Path) -> bool:
    """Baixa um arquivo da URL"""
    try:
        print(f"Baixando: {url}")
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'pdf' in content_type.lower():
            output_path = output_path.with_suffix('.pdf')
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✓ Salvo: {output_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False

def main():
    """Função principal com Selenium"""
    print("=" * 60)
    print("Download de Normas do Pix - Usando Selenium")
    print("=" * 60)
    print()
    print("⚠️  Requer Chrome/Chromium instalado")
    print()
    
    try:
        # Configurar Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Rodar sem interface
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("Iniciando navegador...")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # Tentar sem webdriver_manager
            driver = webdriver.Chrome(options=chrome_options)
        
        print("Acessando página...")
        driver.get(BCB_PIX_URL)
        
        # Aguardar carregamento
        print("Aguardando carregamento da página...")
        time.sleep(5)  # Aguardar JavaScript carregar
        
        # Procurar links
        print("Procurando links de documentos...")
        links = []
        
        # Procurar por todos os links
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in all_links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if not href:
                    continue
                
                # Verificar se é PDF ou link relevante
                if '.pdf' in href.lower() or any(
                    keyword in text.lower() for keyword in ['circular', 'resolução', 'comunicado', 'norma']
                ):
                    links.append({
                        'url': href,
                        'text': text or 'Documento',
                        'filename': os.path.basename(urlparse(href).path) or f"documento_{len(links)}.pdf"
                    })
            except:
                continue
        
        driver.quit()
        
        if not links:
            print("⚠️  Nenhum link encontrado mesmo com Selenium.")
            print("   Baixe manualmente os PDFs de:")
            print(f"   {BCB_PIX_URL}")
            return
        
        print(f"Encontrados {len(links)} documentos.")
        print()
        
        # Baixar
        downloaded = 0
        for i, link_info in enumerate(links, 1):
            print(f"[{i}/{len(links)}] {link_info['text'][:60]}")
            
            filename = "".join(c for c in link_info['filename'] if c.isalnum() or c in (' ', '-', '_', '.')).strip()
            if not filename:
                filename = f"documento_{i}"
            
            output_path = OUTPUT_DIR / filename
            
            if output_path.exists():
                print(f"  ⊙ Já existe")
                continue
            
            if download_file(link_info['url'], output_path):
                downloaded += 1
            
            time.sleep(1)
        
        print()
        print(f"✓ Download concluído: {downloaded} documentos")
        
    except ImportError:
        print("✗ Selenium não instalado.")
        print("  Instale: pip install selenium webdriver-manager")
    except Exception as e:
        print(f"✗ Erro: {e}")

if __name__ == "__main__":
    main()

