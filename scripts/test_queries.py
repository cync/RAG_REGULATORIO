"""
Script de testes manuais com perguntas reais sobre Pix e Open Finance.
Execute após a ingestão de documentos.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Perguntas de teste reais
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
        "domain": "pix",
        "question": "Quais são as penalidades aplicáveis por descumprimento das normas do Pix?",
        "expected_keywords": ["penalidade", "sanção", "artigo"]
    },
    {
        "domain": "open_finance",
        "question": "Como funciona o consentimento no Open Finance?",
        "expected_keywords": ["consentimento", "Open Finance", "artigo"]
    },
    {
        "domain": "open_finance",
        "question": "Quais são os direitos do titular de dados no Open Finance?",
        "expected_keywords": ["direito", "titular", "artigo"]
    },
    {
        "domain": "pix",
        "question": "Qual é o limite de transação no Pix?",
        "expected_keywords": ["limite", "transação", "artigo"]
    },
]


def test_health():
    """Testa endpoint de health"""
    print("\n" + "="*60)
    print("TESTE: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {data['status']}")
        print(f"Qdrant conectado: {data['qdrant_connected']}")
        print(f"Coleções: {data['collections']}")
        print("✓ Health check OK")
        return True
    except Exception as e:
        print(f"✗ Health check FALHOU: {e}")
        return False


def test_chat(domain: str, question: str, expected_keywords: list = None):
    """Testa endpoint de chat"""
    print("\n" + "="*60)
    print(f"TESTE: Chat - {domain.upper()}")
    print("="*60)
    print(f"Pergunta: {question}")
    
    try:
        payload = {
            "question": question,
            "domain": domain
        }
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"\nResposta:")
        print("-" * 60)
        print(data['answer'])
        print("-" * 60)
        
        print(f"\nContexto suficiente: {data['has_sufficient_context']}")
        print(f"Fontes encontradas: {len(data['sources'])}")
        print(f"Citações: {data['citations']}")
        
        # Validar keywords esperadas
        if expected_keywords:
            answer_lower = data['answer'].lower()
            found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
            print(f"Keywords encontradas: {found_keywords}")
        
        # Validar estrutura da resposta
        has_article = "artigo" in data['answer'].lower() or "art." in data['answer'].lower()
        print(f"Contém referência a artigo: {has_article}")
        
        if data['has_sufficient_context'] and has_article:
            print("✓ Teste PASSOU")
            return True
        else:
            print("⚠ Teste com AVISOS (pode não ter contexto suficiente)")
            return False
            
    except Exception as e:
        print(f"✗ Teste FALHOU: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Resposta: {e.response.text}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("TESTES DO AGENTE REGULATÓRIO")
    print("="*60)
    print(f"Data/Hora: {datetime.now().isoformat()}")
    print(f"Base URL: {BASE_URL}")
    
    results = {
        "health": False,
        "chat_tests": []
    }
    
    # Teste 1: Health
    results["health"] = test_health()
    
    if not results["health"]:
        print("\n⚠ AVISO: Health check falhou. Verifique se os serviços estão rodando.")
        print("Execute: docker-compose up -d")
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
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"Health check: {'✓' if results['health'] else '✗'}")
    
    passed_chats = sum(1 for t in results["chat_tests"] if t["passed"])
    print(f"Chat tests: {passed_chats}/{len(results['chat_tests'])} passaram")
    
    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60)


if __name__ == "__main__":
    main()

