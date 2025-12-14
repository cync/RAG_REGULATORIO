# 🔧 Variáveis de Ambiente no Railway

## ⚠️ ERRO: OPENAI_API_KEY não configurada

Se você está vendo este erro, precisa configurar as variáveis de ambiente no Railway.

## 📋 Variáveis Obrigatórias

Configure estas variáveis no Railway:

### 1. Acesse as Variáveis de Ambiente

No Railway:
1. Vá no seu projeto
2. Clique em **Settings**
3. Clique em **Variables**
4. Adicione as variáveis abaixo

### 2. Variáveis Necessárias

```env
# OBRIGATÓRIA - OpenAI API Key
OPENAI_API_KEY=sk-...

# OBRIGATÓRIA - Qdrant (se usar Qdrant Cloud)
QDRANT_HOST=seu-cluster.qdrant.io
QDRANT_PORT=6333

# OBRIGATÓRIA - Se usar Qdrant Cloud com autenticação
QDRANT_API_KEY=sua-api-key

# Opcionais (têm valores padrão)
APP_ENV=production
LOG_LEVEL=INFO
API_TIMEOUT=30
RATE_LIMIT_PER_MINUTE=60
TOP_K_RESULTS=5
MIN_SIMILARITY_SCORE=0.7
MAX_TOKENS_RESPONSE=1000
EMBEDDING_MODEL=text-embedding-3-large
LLM_MODEL=gpt-4o-mini
DOMAINS=pix,open_finance
```

## 🔑 Como Obter as Chaves

### OpenAI API Key
1. Acesse: https://platform.openai.com/api-keys
2. Clique em "Create new secret key"
3. Copie a chave (começa com `sk-`)
4. Cole no Railway

### Qdrant (se usar Qdrant Cloud)
1. Acesse: https://cloud.qdrant.io
2. Crie um cluster
3. Copie a URL do cluster (ex: `abc123.qdrant.io`)
4. Cole em `QDRANT_HOST`
5. Se tiver API key, cole em `QDRANT_API_KEY`

### Qdrant (se usar próprio servidor)
- `QDRANT_HOST`: IP ou domínio do seu servidor
- `QDRANT_PORT`: 6333 (padrão)

## ✅ Após Configurar

1. **Salve as variáveis** no Railway
2. **Redeploy** o serviço (Railway detecta automaticamente)
3. **Verifique os logs** para confirmar que iniciou

## 🧪 Testar

Após configurar, teste o health check:

```bash
curl https://seu-backend.railway.app/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  ...
}
```

## ⚠️ Importante

- **NUNCA** commite chaves API no Git
- Use variáveis de ambiente sempre
- Revogue chaves antigas se expostas

