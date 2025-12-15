"""
Script para baixar normativos do Banco Central via API de feeds
Mais eficiente que baixar PDFs escaneados - retorna conteúdo estruturado
"""
import sys
import requests
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import time
import re

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import get_settings

def parse_feed(url: str) -> list:
    """Parse feed Atom e retorna lista de normativos"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Namespace Atom
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = []
        for entry in root.findall('atom:entry', ns):
            entry_data = {}
            
            # ID
            entry_id = entry.find('atom:id', ns)
            if entry_id is not None:
                entry_data['id'] = entry_id.text
            
            # Título
            title = entry.find('atom:title', ns)
            if title is not None:
                entry_data['title'] = title.text
            
            # Link
            link = entry.find('atom:link', ns)
            if link is not None:
                entry_data['url'] = link.get('href', '')
            
            # Conteúdo
            content = entry.find('atom:content', ns)
            if content is not None:
                entry_data['content'] = content.text
            
            # Updated
            updated = entry.find('atom:updated', ns)
            if updated is not None:
                entry_data['updated'] = updated.text
            
            entries.append(entry_data)
        
        return entries
    
    except Exception as e:
        print(f"❌ Erro ao parsear feed: {e}")
        return []

def extract_norma_info(title: str) -> dict:
    """Extrai informações da norma do título"""
    info = {
        'tipo': None,
        'numero': None,
        'ano': None
    }
    
    # Padrões comuns
    patterns = [
        r'(Resolução|Instrução Normativa|Circular)\s+(?:BCB|BC)\s*N[°º]?\s*(\d+)\s+de\s+(\d+)/(\d+)/(\d+)',
        r'(Resolução|Instrução Normativa|Circular)\s+(?:BCB|BC)\s*N[°º]?\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            info['tipo'] = match.group(1)
            info['numero'] = match.group(2)
            if len(match.groups()) >= 5:
                info['ano'] = match.group(5)
            break
    
    return info

def is_pix_or_open_finance(title: str, content: str = "") -> bool:
    """Verifica se o normativo é sobre Pix ou Open Finance"""
    text = (title + " " + (content or "")).lower()
    
    pix_keywords = ['pix', 'pagamento instantâneo', 'pagamento instantaneo']
    open_finance_keywords = ['open finance', 'open banking', 'dados abertos', 'compartilhamento de dados']
    
    has_pix = any(keyword in text for keyword in pix_keywords)
    has_open_finance = any(keyword in text for keyword in open_finance_keywords)
    
    return has_pix or has_open_finance

def download_normativo_content(url: str) -> str:
    """Baixa o conteúdo HTML do normativo"""
    try:
        # Adicionar headers para parecer um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remover scripts e styles
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # O site do Bacen usa Angular, então o conteúdo pode estar em diferentes lugares
        # Tentar encontrar o conteúdo principal de várias formas
        
        # 1. Tentar encontrar div com conteúdo normativo
        content_selectors = [
            {'class': re.compile(r'content|normativo|texto|documento', re.I)},
            {'id': re.compile(r'content|normativo|texto|documento', re.I)},
            {'class': 'normativo-content'},
            {'class': 'document-content'},
        ]
        
        for selector in content_selectors:
            content_div = soup.find('div', selector)
            if content_div:
                text = content_div.get_text(separator='\n', strip=True)
                if len(text) > 200:  # Tem conteúdo suficiente
                    return f"<div class='normativo-content'>{str(content_div)}</div>"
        
        # 2. Tentar encontrar main ou article
        for tag in ['main', 'article', 'section']:
            element = soup.find(tag)
            if element:
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 200:
                    return f"<{tag}>{str(element)}</{tag}>"
        
        # 3. Se não encontrar, usar body inteiro mas limpo
        body = soup.find('body')
        if body:
            # Remover elementos vazios ou sem conteúdo
            for element in body.find_all(['div', 'span', 'p']):
                text = element.get_text(strip=True)
                if len(text) < 10:
                    element.decompose()
            
            text = body.get_text(separator='\n', strip=True)
            if len(text) > 200:
                return str(body)
        
        # 4. Se ainda não tiver conteúdo, retornar HTML limpo
        return str(soup)
            
    except Exception as e:
        print(f"⚠️  Erro ao baixar conteúdo de {url}: {e}")
        return ""

def save_normativo(entry: dict, domain: str, output_dir: Path):
    """Salva normativo como HTML"""
    # Extrair informações
    norma_info = extract_norma_info(entry.get('title', ''))
    tipo = norma_info.get('tipo', 'Normativo')
    numero = norma_info.get('numero', 'N/A')
    ano = norma_info.get('ano', '2023')
    
    # Nome do arquivo
    filename = f"{tipo.replace(' ', '_')}_{numero}_{ano}.html"
    filename = re.sub(r'[^\w\-_\.]', '_', filename)  # Limpar caracteres especiais
    
    file_path = output_dir / filename
    
    # Verificar se já existe
    if file_path.exists():
        print(f"  ⚠️  Arquivo já existe: {file_path.name}")
        return file_path
    
    # Baixar conteúdo completo
    content = download_normativo_content(entry.get('url', ''))
    
    if not content or len(content.strip()) < 100:
        # Se não conseguir baixar, usar o conteúdo do feed
        content = entry.get('content', '')
        # Criar HTML básico
        content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{entry.get('title', 'Normativo')}</title>
</head>
<body>
    <h1>{entry.get('title', 'Normativo')}</h1>
    <div class="content">
        {content}
    </div>
</body>
</html>"""
    
    # Validar que tem conteúdo útil
    text_content = re.sub(r'<[^>]+>', '', content)  # Remover tags HTML
    text_content = text_content.replace('\n', ' ').replace(' ', ' ').strip()
    
    if len(text_content) < 50:
        print(f"  ⚠️  Conteúdo muito curto, pulando: {file_path.name}")
        return None
    
    # Salvar HTML
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def download_normativos_by_year(year: int, domain: str = "pix"):
    """Baixa normativos de um ano específico"""
    base_url = "https://www.bcb.gov.br/api/feed/app/normativos/normativos"
    url = f"{base_url}?ano={year}"
    
    print(f"\n{'='*60}")
    print(f"Baixando normativos de {year}...")
    print(f"{'='*60}")
    
    # Diretório de saída
    output_dir = Path(project_root) / "data" / "raw" / domain
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse feed
    entries = parse_feed(url)
    
    if not entries:
        print(f"⚠️  Nenhum normativo encontrado para {year}")
        return 0
    
    print(f"📋 Encontrados {len(entries)} normativos no feed")
    
    # Filtrar por tema
    relevant_entries = []
    for entry in entries:
        title = entry.get('title', '')
        content = entry.get('content', '')
        
        if is_pix_or_open_finance(title, content):
            relevant_entries.append(entry)
            print(f"  ✓ {title[:80]}...")
    
    print(f"\n📌 {len(relevant_entries)} normativos relevantes para {domain}")
    
    # Baixar normativos
    downloaded = 0
    for i, entry in enumerate(relevant_entries, 1):
        try:
            file_path = save_normativo(entry, domain, output_dir)
            print(f"  [{i}/{len(relevant_entries)}] ✅ {file_path.name}")
            downloaded += 1
            
            # Pequeno delay para não sobrecarregar o servidor
            time.sleep(0.5)
        except Exception as e:
            print(f"  [{i}/{len(relevant_entries)}] ❌ Erro: {e}")
    
    return downloaded

def main():
    """Baixa normativos de 2021 a 2025"""
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = "pix"
    
    print(f"\n🚀 Baixando normativos do Banco Central via API")
    print(f"   Domínio: {domain}")
    print(f"   Anos: 2021-2025")
    print(f"   Fonte: https://www.bcb.gov.br/api/feed/app/normativos/normativos")
    
    total_downloaded = 0
    
    for year in range(2021, 2026):
        try:
            downloaded = download_normativos_by_year(year, domain)
            total_downloaded += downloaded
        except Exception as e:
            print(f"❌ Erro ao processar {year}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Concluído! {total_downloaded} normativos baixados")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

