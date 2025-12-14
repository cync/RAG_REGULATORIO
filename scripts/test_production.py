"""
Script de testes para ambiente de produção.
Adapta o script de testes local para produção.
"""
import requests
import json
import sys
import os
from datetime import datetime
import time

# Configuração
BASE_URL = os.getenv("PRODUCTION_URL", "https://seu-dominio.com")
API_KEY = os.getenv("API_KEY", None)  # Se usar autenticação

# Headers
headers = {
    "Content-Type": "application/json"
}

if API_KEY:
    headers["Authorization"] = f"Bearer {API_KEY}"

# Perguntas de teste
TEST_QUERIES = [
    {
        "domain": "pix",
        "question": "Quais são as obrigações de um PSP (Prestador de Serviços de Pagamento) no Pix?",
        "expected_keywords": ["obrigação", "PSP", "Pix", "artigo"]
    },
    {
        "domain": "pix",
        "question": "Quais são as regras de participação no Pix?",
        "expected_keywords": ["regra", "participação", "artigo"]
    },
    {
        "domain": "open_finance",
        "question": "Como funciona o consentimento no Open Finance?",
        "expected_keywords": ["consentimento", "Open Finance", "artigo"]
    },
]


def test_health():
    """Testa endpoint de health"""
    print("\n" + "="*60)
    print("TESTE: Health Check")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/health",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {data['status']}")
        print(f"Qdrant conectado: {data['qdrant_connected']}")
        print(f"Coleções: {data['collections']}")
        
        if data['status'] == 'healthy':
            print("✓ Health check OK")
            return True
        else:
            print("⚠ Health check com avisos")
            return False
    except Exception as e:
        print(f"✗ Health check FALHOU: {e}")
        return False


def test_chat(domain: str, question: str, expected_keywords: list = None):
    """Testa endpoint de chat"""
    print("\n" + "="*60)
    print(f"TESTE: Chat - {domain.upper()}")
    print("="*60)
    print(f"Pergunta: {question}")
    
    start_time = time.time()
    
    try:
        payload = {
            "question": question,
            "domain": domain
        }
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        elapsed = time.time() - start_time
        
        print(f"\nResposta ({elapsed:.2f}s):")
        print("-" * 60)
        print(data['answer'][:500] + "..." if len(data['answer']) > 500 else data['answer'])
        print("-" * 60)
        
        print(f"\nContexto suficiente: {data['has_sufficient_context']}")
        print(f"Fontes encontradas: {len(data['sources'])}")
        print(f"Citações: {data['citations']}")
        
        # Validar keywords
        if expected_keywords:
            answer_lower = data['answer'].lower()
            found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
            print(f"Keywords encontradas: {found_keywords}")
        
        # Validar estrutura
        has_article = "artigo" in data['answer'].lower() or "art." in data['answer'].lower()
        print(f"Contém referência a artigo: {has_article}")
        
        # Validar tempo de resposta
        if elapsed > 30:
            print(f"⚠ Tempo de resposta alto: {elapsed:.2f}s")
        
        if data['has_sufficient_context'] and has_article and elapsed < 30:
            print("✓ Teste PASSOU")
            return True
        else:
            print("⚠ Teste com AVISOS")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Timeout - requisição demorou mais de 60s")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"✗ Erro HTTP: {e}")
        print(f"Resposta: {e.response.text if e.response else 'N/A'}")
        return False
    except Exception as e:
        print(f"✗ Teste FALHOU: {e}")
        return False


def test_load(n_requests: int = 10, concurrency: int = 2):
    """Teste de carga básico"""
    print("\n" + "="*60)
    print(f"TESTE: Carga ({n_requests} requisições, {concurrency} concorrentes)")
    print("="*60)
    
    import concurrent.futures
    
    def make_request():
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "question": "Quais são as obrigações de um PSP no Pix?",
                    "domain": "pix"
                },
                headers=headers,
                timeout=60
            )
            return response.status_code == 200, response.elapsed.total_seconds()
        except Exception as e:
            return False, 0
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request) for _ in range(n_requests)]
        for future in concurrent.futures.as_completed(futures):
            success, elapsed = future.result()
            results.append((success, elapsed))
    
    total_time = time.time() - start_time
    
    successful = sum(1 for s, _ in results if s)
    avg_time = sum(t for _, t in results) / len(results) if results else 0
    max_time = max(t for _, t in results) if results else 0
    
    print(f"Requisições bem-sucedidas: {successful}/{n_requests}")
    print(f"Tempo total: {total_time:.2f}s")
    print(f"Tempo médio: {avg_time:.2f}s")
    print(f"Tempo máximo: {max_time:.2f}s")
    print(f"Requisições/segundo: {n_requests/total_time:.2f}")
    
    if successful == n_requests and avg_time < 10:
        print("✓ Teste de carga PASSOU")
        return True
    else:
        print("⚠ Teste de carga com AVISOS")
        return False


def main():
    """Executa todos os testes"""
    import os
    
    print("\n" + "="*60)
    print("TESTES DE PRODUÇÃO - AGENTE REGULATÓRIO")
    print("="*60)
    print(f"URL: {BASE_URL}")
    print(f"Data/Hora: {datetime.now().isoformat()}")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--load":
            # Apenas teste de carga
            test_load(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
            return
    
    results = {
        "health": False,
        "chat_tests": [],
        "load": False
    }
    
    # Teste 1: Health
    results["health"] = test_health()
    
    if not results["health"]:
        print("\n⚠ AVISO: Health check falhou. Verifique se o serviço está rodando.")
        return
    
    # Teste 2: Chat queries
    print("\n" + "="*60)
    print("INICIANDO TESTES DE CHAT")
    print("="*60)
    
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n[{i}/{len(TEST_QUERIES)}]")
        result = test_chat(
            test["domain"],
            test["question"],
            test.get("expected_keywords")
        )
        results["chat_tests"].append({
            "question": test["question"],
            "domain": test["domain"],
            "passed": result
        })
    
    # Teste 3: Carga (opcional)
    print("\n" + "="*60)
    print("TESTE DE CARGA")
    print("="*60)
    results["load"] = test_load(n_requests=5, concurrency=2)
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"Health check: {'✓' if results['health'] else '✗'}")
    
    passed_chats = sum(1 for t in results["chat_tests"] if t["passed"])
    print(f"Chat tests: {passed_chats}/{len(results['chat_tests'])} passaram")
    print(f"Teste de carga: {'✓' if results['load'] else '✗'}")
    
    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60)


if __name__ == "__main__":
    import os
    main()

