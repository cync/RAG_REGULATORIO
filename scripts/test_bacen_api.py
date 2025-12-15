"""
Script para testar a API do Bacen e ver o que está sendo retornado
"""
import sys
import requests
import json
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ingestion.bacen_normativos import fetch_normativo, normalize_html

def test_api(tipo: str, numero: int):
    """Testa a API e mostra o que está sendo retornado"""
    print(f"\n{'='*60}")
    print(f"Testando: {tipo} {numero}")
    print(f"{'='*60}\n")
    
    try:
        # Buscar normativo
        normativo = fetch_normativo(tipo, numero)
        
        print(f"✅ Normativo encontrado!")
        print(f"   Título: {normativo.get('Titulo', 'N/A')}")
        print(f"   Tipo: {normativo.get('Tipo', 'N/A')}")
        print(f"   Número: {normativo.get('Numero', 'N/A')}")
        print(f"   Data: {normativo.get('Data', 'N/A')}")
        
        # Verificar campo Texto
        html_text = normativo.get("Texto", "")
        
        print(f"\n📄 Campo 'Texto':")
        print(f"   Tipo: {type(html_text)}")
        print(f"   Tamanho: {len(html_text) if html_text else 0} caracteres")
        print(f"   É None: {html_text is None}")
        print(f"   É string vazia: {html_text == ''}")
        
        if html_text:
            print(f"\n   Preview (primeiros 500 chars):")
            print(f"   {html_text[:500]}")
            
            # Tentar normalizar
            print(f"\n🔧 Normalizando HTML...")
            normalized = normalize_html(html_text)
            
            print(f"   Tamanho normalizado: {len(normalized)} caracteres")
            print(f"   Tamanho não-whitespace: {len(normalized.replace(' ', '').replace('\\n', ''))} caracteres")
            
            if normalized:
                print(f"\n   Preview normalizado (primeiros 500 chars):")
                print(f"   {normalized[:500]}")
            else:
                print(f"\n   ⚠️  Texto normalizado está vazio!")
        else:
            print(f"\n   ⚠️  Campo 'Texto' está vazio ou None!")
        
        # Mostrar todos os campos disponíveis
        print(f"\n📋 Campos disponíveis no normativo:")
        for key, value in normativo.items():
            if key == "Texto":
                print(f"   {key}: [HTML - {len(str(value))} chars]")
            else:
                print(f"   {key}: {str(value)[:100]}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Testar com um normativo conhecido
    test_api("Instrução Normativa BCB", 513)

