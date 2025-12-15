# 📥 Guia: Download de Normativos via API Oficial do Banco Central

## 🎯 Visão Geral

Este módulo consome a **API oficial do Banco Central** para baixar, normalizar e preparar normativos para indexação RAG.

**API Oficial:** `https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo`

## ✅ Vantagens

- ✅ **API Oficial** - Fonte confiável e autorizada
- ✅ **Texto Completo** - HTML completo do normativo
- ✅ **Metadados Ricos** - Tipo, número, data, versão, revogação, etc.
- ✅ **Sem Scraping** - Não precisa renderizar JavaScript
- ✅ **Estruturado** - JSON limpo e normalizado
- ✅ **Idempotente** - Pode executar múltiplas vezes sem duplicar

## 🚀 Como Usar

### 1. Baixar Normativos por Domínio

```bash
# Baixar todos os normativos do Pix
python scripts/download_bacen_normativos.py pix

# Baixar normativos de Open Finance
python scripts/download_bacen_normativos.py open_finance
```

### 2. Baixar Normativo Específico

```bash
python scripts/download_bacen_normativos.py \
  --tipo "Instrução Normativa BCB" \
  --numero 513
```

### 3. Processar Arquivos Baixados

Após baixar, os arquivos JSON são salvos em `data/raw/pix/` ou `data/raw/open_finance/`.

Execute a ingestão normalmente:

```bash
python scripts/ingest.py pix
```

O parser já reconhece arquivos JSON e processa automaticamente!

## 📋 Estrutura dos Arquivos

Cada artigo é salvo como um arquivo JSON:

```json
{
  "text": "Art. 1º Este normativo estabelece...",
  "metadata": {
    "fonte": "BACEN",
    "tipo": "Instrução Normativa BCB",
    "numero": "513",
    "titulo": "Instrução Normativa BCB Nº 513",
    "artigo": "1",
    "data_publicacao": "2024-01-15",
    "versao": "1.0",
    "revogado": false,
    "cancelado": false,
    "atualizacoes": [],
    "assunto": "Pix - Regulamento",
    "url": "https://www.bcb.gov.br/...",
    "tema": "pix",
    "ano": 2024
  }
}
```

## 🔧 Funcionalidades

### Normalização HTML

- Remove tags desnecessárias (`<span>`, `<div>`, `<font>`)
- **Remove completamente texto revogado** (`<s>`)
- Preserva estrutura jurídica (artigos, parágrafos, incisos)
- Normaliza quebras de linha e espaços

### Chunking por Artigo

- Divide automaticamente por "Art. Xº"
- Cada chunk = 1 artigo completo
- Preserva incisos e parágrafos juntos
- Mantém rastreabilidade (metadados completos)

### Metadados Completos

- Tipo e número do normativo
- Data de publicação
- Versão
- Status (revogado, cancelado)
- Atualizações
- Assunto
- URL oficial
- Tema (pix/open_finance) inferido automaticamente

## 📊 Normativos Pré-configurados

### Pix

- Instruções Normativas: 1, 16, 19, 32, 198, 199, 200, 243, 412, 491, 508, 511, 512, 513
- Resoluções: 1, 264

### Open Finance

- (Ajustar conforme necessário)

## 🔍 Exemplo de Uso Programático

```python
from app.ingestion.bacen_normativos import process_normativo
from pathlib import Path

# Processar um normativo
result = process_normativo(
    tipo="Instrução Normativa BCB",
    numero=513,
    output_dir=Path("data/raw/pix")
)

if result["success"]:
    print(f"✅ {result['artigos_encontrados']} artigos processados")
    print(f"   {result['chunks_salvos']} arquivos salvos")
else:
    print(f"❌ Erro: {result['error']}")
```

## ⚠️ Tratamento de Erros

O módulo trata automaticamente:

- Normativo não encontrado
- Erros de rede/timeout
- HTML malformado
- Texto vazio ou muito curto
- Falhas na normalização

Todos os erros são logados com detalhes para debug.

## 🎯 Integração com Pipeline RAG

Os arquivos JSON gerados são automaticamente:

1. **Reconhecidos** pelo parser (`parse_json_normativo`)
2. **Processados** com metadados completos
3. **Chunked** preservando estrutura jurídica
4. **Indexados** no Qdrant com rastreabilidade completa

## 📝 Notas Importantes

- **Idempotência**: Arquivos existentes são pulados (não duplica)
- **Estrutura Preservada**: Artigos, parágrafos e incisos mantidos
- **Texto Revogado**: Completamente removido (tag `<s>`)
- **Metadados Ricos**: Tudo necessário para auditoria regulatória

---

**Status:** ✅ Módulo completo e pronto para produção!

