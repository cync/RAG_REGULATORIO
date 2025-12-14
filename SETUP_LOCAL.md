# 🔧 Configuração Local para Ingestão

## ⚠️ Arquivo .env Necessário

Para executar a ingestão localmente, você precisa configurar o arquivo `.env`.

## 📋 Passo a Passo

### 1. Criar arquivo .env

O arquivo `.env.example` foi copiado para `.env`. Agora você precisa editar e adicionar suas credenciais.

### 2. Configurar Variáveis

Abra o arquivo `.env` e configure:

```env
# OpenAI (OBRIGATÓRIA)
OPENAI_API_KEY=sk-...

# Qdrant (OBRIGATÓRIA - use a mesma do Railway)
QDRANT_HOST=seu-cluster.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=sua-api-key  # Se usar Qdrant Cloud

# Outras (opcionais, têm valores padrão)
APP_ENV=development
LOG_LEVEL=INFO
```

### 3. Obter Credenciais

**OpenAI API Key:**
- Acesse: https://platform.openai.com/api-keys
- Crie uma nova chave
- Cole no `.env`

**Qdrant (mesmo do Railway):**
- Use as mesmas credenciais que estão no Railway
- `QDRANT_HOST`: URL do seu cluster Qdrant Cloud
- `QDRANT_API_KEY`: API key do Qdrant Cloud (se necessário)

### 4. Executar Ingestão

Após configurar o `.env`:

```bash
cd C:\Users\Felipe\RAG_REGULATORIO
python -m app.ingestion.main pix
```

## ⚠️ Importante

- **NUNCA** commite o arquivo `.env` no Git
- O `.env` já está no `.gitignore`
- Use as mesmas credenciais do Railway para que os documentos sejam indexados no mesmo Qdrant

## ✅ Após Configurar

1. Edite `.env` com suas credenciais
2. Execute: `python -m app.ingestion.main pix`
3. Aguarde a indexação (pode demorar devido a rate limits)
4. Verifique: `curl https://ragregulatorio-production.up.railway.app/health`

