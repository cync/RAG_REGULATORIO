# 📥 Guia: Baixar Normativos via API do Banco Central

## 🎯 Vantagens da API vs OCR

Usar a API do Banco Central é **muito melhor** que OCR porque:

✅ **Mais rápido** - Não precisa processar imagens  
✅ **Mais preciso** - Texto original, sem erros de OCR  
✅ **Mais confiável** - Conteúdo estruturado  
✅ **Metadados completos** - Já vem com tipo, número, ano  
✅ **HTML limpo** - Fácil de processar  

## 🚀 Como Usar

### 1. Baixar Normativos

```bash
# Baixar normativos de Pix (2021-2025)
python scripts/download_normativos_api.py pix

# Baixar normativos de Open Finance
python scripts/download_normativos_api.py open_finance
```

### 2. O Script Faz

- ✅ Acessa a API: `https://www.bcb.gov.br/api/feed/app/normativos/normativos?ano=YYYY`
- ✅ Filtra normativos sobre Pix ou Open Finance
- ✅ Baixa o conteúdo HTML completo
- ✅ Salva em `data/raw/pix/` ou `data/raw/open_finance/`

### 3. Processar com Ingestão

Depois de baixar, execute a ingestão normalmente:

```bash
python scripts/ingest.py pix
```

O parser HTML já está implementado e funcionando!

## 📋 API do Banco Central

### Endpoint

```
https://www.bcb.gov.br/api/feed/app/normativos/normativos?ano=YYYY
```

### Formato

Retorna feed Atom/XML com:
- Título do normativo
- Link para página completa
- Resumo/conteúdo
- Data de atualização

### Exemplo de Uso

```python
import requests
import xml.etree.ElementTree as ET

url = "https://www.bcb.gov.br/api/feed/app/normativos/normativos?ano=2024"
response = requests.get(url)
root = ET.fromstring(response.content)
# Parse entries...
```

## 🔍 Filtragem Automática

O script filtra automaticamente normativos sobre:
- **Pix**: "pix", "pagamento instantâneo"
- **Open Finance**: "open finance", "open banking", "dados abertos"

## ⚙️ Configuração

O script usa a mesma estrutura de diretórios:
- `data/raw/pix/` - Arquivos baixados (Pix)
- `data/raw/open_finance/` - Arquivos baixados (Open Finance)

## 📝 Notas

- A API retorna os **10 normativos mais recentes** por ano
- Se precisar de mais, pode ajustar o script para buscar por página
- Os arquivos são salvos como HTML, que o parser já processa

## 🆚 Comparação: API vs OCR

| Aspecto | API | OCR |
|---------|-----|-----|
| Velocidade | ⚡ Muito rápido | 🐌 Lento (minutos por PDF) |
| Precisão | ✅ 100% | ⚠️ 95-98% (erros de OCR) |
| Instalação | ✅ Apenas Python | ❌ Tesseract + poppler |
| Conteúdo | ✅ Estruturado | ⚠️ Texto plano |
| Metadados | ✅ Completos | ⚠️ Precisam extrair |

## 🎯 Recomendação

**Use a API sempre que possível!** É a melhor opção para este projeto.

---

**Status:** ✅ Script implementado e funcionando!

