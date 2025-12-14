# Agente Regulatório - RAG para Pix e Open Finance

Sistema de RAG (Retrieval-Augmented Generation) especializado em regulação do Banco Central do Brasil, com foco em **Pix** e **Open Finance**.

## ⚠️ Disclaimer Jurídico

Este sistema é uma ferramenta de auxílio à consulta normativa. **NÃO substitui consultoria jurídica especializada**. Todas as respostas são baseadas exclusivamente nos documentos normativos indexados. O uso deste sistema não implica em garantia de precisão absoluta ou atualização normativa. Sempre consulte a fonte oficial do Banco Central do Brasil para decisões regulatórias críticas.

## 🏗️ Arquitetura

- **Backend**: Python + FastAPI
- **RAG**: LlamaIndex
- **Vector DB**: Qdrant (Docker)
- **Embeddings**: OpenAI text-embedding-3-large
- **LLM**: GPT-4o-mini
- **Infra**: Docker

## 📋 Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- Conta OpenAI com API key

## 🚀 Instalação e Uso

### 1. Clone o repositório

```bash
git clone <repo-url>
cd RAG_REGULATORIO
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env e adicione sua OPENAI_API_KEY
```

### 3. Inicie os serviços com Docker

```bash
docker-compose up -d
```

Isso iniciará:
- Qdrant (porta 6333)
- API FastAPI (porta 8000)

### 4. Ingira documentos regulatórios

```bash
# Coloque seus PDFs/HTMLs em data/raw/pix ou data/raw/open_finance
# Execute a ingestão
python -m app.ingestion.main pix
python -m app.ingestion.main open_finance

# Ou para reindexar completamente:
python -m app.ingestion.main pix --force
python -m app.ingestion.main open_finance --force
```

### 5. Acesse a API

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais são as obrigações de um PSP no Pix?",
    "domain": "pix"
  }'
```

## 📁 Estrutura do Projeto

```
/app
  /api          # Endpoints FastAPI
  /rag          # Engine RAG core
  /ingestion    # Pipeline de ingestão
  /models       # Modelos Pydantic
  /config       # Configurações
  /utils        # Utilitários
/data
  /raw          # Documentos originais
  /processed    # Documentos processados
/logs           # Logs estruturados
/docker         # Dockerfiles
```

## 🔍 Funcionalidades

- **Busca semântica** em documentos normativos
- **Validação anti-alucinação** obrigatória
- **Citações normativas** automáticas (norma, artigo, ano)
- **Logs auditáveis** de todas as consultas
- **Rejeição automática** quando não há base documental

## 🧪 Testes

Execute o script de testes:

```bash
python scripts/test_queries.py
```

## 📝 Logs e Auditoria

Todos os logs são armazenados em `/logs` com formato estruturado, contendo:
- Pergunta do usuário
- Data/hora
- Documentos utilizados
- Normas/artigos citados
- Resposta final

## 🔧 Desenvolvimento

### Reindexar completamente

```bash
# Via API
curl -X POST "http://localhost:8000/reindex?domain=pix&force=true"

# Ou via script
python -m app.ingestion.main pix --force
```

### Ver logs

```bash
tail -f logs/app.log
```

## 🚀 Deploy em Produção

Para deploy em produção, consulte:

- **Quick Start**: `QUICK_START_PRODUCTION.md` - Deploy rápido (30 min)
- **Guia Completo**: `PRODUCTION_DEPLOY.md` - Opções de provedores e arquiteturas
- **Frontend**: `FRONTEND_DEPLOY.md` - Deploy do frontend
- **Testes**: `scripts/test_production.py` - Script de testes para produção

### Opções Recomendadas:

1. **Rápido**: Railway (Backend) + Qdrant Cloud + Vercel (Frontend)
2. **Completo**: AWS ECS + EC2 (Qdrant) + S3/CloudFront (Frontend)
3. **Simples**: DigitalOcean Droplet (tudo em um servidor)

## 📄 Licença

Uso interno - Sistema regulatório.

