# Guia de Deploy - Agente Regulatório

## Pré-requisitos

1. **Docker e Docker Compose** instalados
2. **Conta OpenAI** com API key válida
3. **Documentos regulatórios** em formato PDF ou HTML

## Passo a Passo

### 1. Configuração Inicial

```bash
# Clone o repositório
git clone <repo-url>
cd RAG_REGULATORIO

# Copie o arquivo de exemplo de variáveis de ambiente
cp .env.example .env

# Edite o .env e adicione sua OPENAI_API_KEY
# Abra o arquivo .env e configure:
# OPENAI_API_KEY=sk-...
```

### 2. Preparar Documentos

```bash
# Crie os diretórios (já devem existir)
mkdir -p data/raw/pix
mkdir -p data/raw/open_finance

# Coloque seus documentos PDF/HTML nos diretórios apropriados
# Exemplo:
# data/raw/pix/circular_123_2023.pdf
# data/raw/open_finance/resolucao_456_2023.pdf
```

**Dica**: Organize os arquivos com nomes descritivos:
- `pix_circular_123_2023.pdf`
- `open_finance_resolucao_456_2023.pdf`

### 3. Iniciar Serviços

```bash
# Iniciar Qdrant e Backend
docker-compose up -d

# Verificar se estão rodando
docker-compose ps

# Ver logs
docker-compose logs -f backend
```

### 4. Ingerir Documentos

```bash
# Opção 1: Via script Python (recomendado)
python -m app.ingestion.main pix
python -m app.ingestion.main open_finance

# Opção 2: Via API (após iniciar serviços)
curl -X POST "http://localhost:8000/reindex?domain=pix&force=true"
curl -X POST "http://localhost:8000/reindex?domain=open_finance&force=true"
```

### 5. Verificar Health

```bash
curl http://localhost:8000/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "collections": {
    "pix": true,
    "open_finance": true
  }
}
```

### 6. Testar API

```bash
# Exemplo de consulta
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais são as obrigações de um PSP no Pix?",
    "domain": "pix"
  }'
```

### 7. Executar Testes

```bash
# Instalar dependências localmente (se necessário)
pip install -r requirements.txt

# Executar script de testes
python scripts/test_queries.py
```

## Estrutura de Produção

### Variáveis de Ambiente Importantes

```env
# Produção
APP_ENV=production
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
API_TIMEOUT=30

# RAG
TOP_K_RESULTS=5
MIN_SIMILARITY_SCORE=0.7
MAX_TOKENS_RESPONSE=1000
```

### Monitoramento

- **Logs**: `logs/app_YYYYMMDD.log`
- **Health Check**: `GET /health`
- **Métricas**: Verificar logs estruturados em JSON

### Backup

```bash
# Backup do Qdrant
docker exec rag_qdrant tar -czf /tmp/qdrant_backup.tar.gz /qdrant/storage
docker cp rag_qdrant:/tmp/qdrant_backup.tar.gz ./backup/

# Backup dos logs
tar -czf logs_backup.tar.gz logs/
```

## Troubleshooting

### Qdrant não conecta

```bash
# Verificar se Qdrant está rodando
docker-compose ps qdrant

# Ver logs
docker-compose logs qdrant

# Reiniciar
docker-compose restart qdrant
```

### Erro de API Key

```bash
# Verificar se está configurada
docker-compose exec backend env | grep OPENAI

# Atualizar
# Edite .env e reinicie
docker-compose restart backend
```

### Sem resultados nas buscas

1. Verificar se documentos foram indexados:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verificar logs de ingestão:
   ```bash
   docker-compose logs backend | grep ingest
   ```

3. Reindexar:
   ```bash
   python -m app.ingestion.main pix --force
   ```

## Próximos Passos

1. **Adicionar mais documentos**: Coloque novos PDFs/HTMLs em `data/raw/` e reexecute a ingestão
2. **Ajustar parâmetros RAG**: Edite `.env` para ajustar `TOP_K_RESULTS` e `MIN_SIMILARITY_SCORE`
3. **Monitorar logs**: Acompanhe `logs/app_*.log` para auditoria
4. **Integrar com frontend**: Use os endpoints da API para construir interface

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/`
2. Execute o health check
3. Verifique se todos os serviços estão rodando
4. Consulte a documentação no README.md

