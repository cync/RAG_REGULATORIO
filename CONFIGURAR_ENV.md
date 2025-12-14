# ⚙️ Configurar .env para Ingestão Local

## 📝 Passo a Passo

### 1. Editar arquivo .env

O arquivo `.env` foi criado. Agora você precisa editar e adicionar suas credenciais.

**Localização:** `C:\Users\Felipe\RAG_REGULATORIO\.env`

### 2. Adicionar OPENAI_API_KEY

1. Abra o arquivo `.env` em um editor de texto
2. Substitua `sk-...` pela sua chave real da OpenAI
3. Para obter a chave:
   - Acesse: https://platform.openai.com/api-keys
   - Crie uma nova chave
   - Cole no `.env`

### 3. Verificar QDRANT_HOST

O `QDRANT_HOST` já está preenchido com o valor do Railway. Se estiver diferente, atualize.

### 4. Adicionar QDRANT_API_KEY (se necessário)

Se o seu Qdrant Cloud exigir API key:
1. Acesse: https://cloud.qdrant.io
2. Vá no seu cluster
3. Copie a API key
4. Cole no `.env` em `QDRANT_API_KEY=`

### 5. Salvar e Executar

Após configurar:

```bash
cd C:\Users\Felipe\RAG_REGULATORIO
python -m app.ingestion.main pix
```

## 📋 Exemplo de .env Completo

```env
OPENAI_API_KEY=sk-proj-abc123...
QDRANT_HOST=649590f4-0fc9-4610-948c-c6d47999d8f3.us-east4-0.gcp.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=sua-api-key-aqui
APP_ENV=development
LOG_LEVEL=INFO
```

## ⚠️ Importante

- Use as **mesmas credenciais do Railway** para que os documentos sejam indexados no mesmo Qdrant
- O arquivo `.env` está no `.gitignore` (não será commitado)
- Nunca compartilhe suas chaves API

