# 🔑 Correção: QDRANT_API_KEY Obrigatória

## ❌ Erro: 403 Forbidden

O erro `403 Forbidden` do Qdrant Cloud indica que a **API key não está configurada ou não está sendo enviada corretamente**.

## ✅ Solução

### 1. Obter API Key do Qdrant Cloud

1. Acesse: https://cloud.qdrant.io
2. Faça login
3. Vá no seu cluster
4. Clique em **"API Keys"** ou **"Settings"**
5. Copie a API key

### 2. Configurar no .env

Edite o arquivo `.env` e adicione:

```env
QDRANT_API_KEY=sua-api-key-aqui
```

**Exemplo:**
```env
QDRANT_HOST=649590f4-0fc9-4610-948c-c6d47999d8f3.us-east4-0.gcp.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=abc123def456...  # ← Cole sua API key aqui
```

### 3. Verificar Formato

**Correto:**
```env
QDRANT_API_KEY=abc123def456ghi789
```

**Errado:**
```env
QDRANT_API_KEY= abc123def456  # Sem espaço
QDRANT_API_KEY="abc123def456"  # Sem aspas
```

### 4. Executar Novamente

Após configurar:

```bash
python -m app.ingestion.main pix
```

## 🔍 Verificar se Está Configurado

O código agora mostra um aviso se a API key não estiver configurada:

```
WARNING: Qdrant Cloud detectado mas QDRANT_API_KEY não configurada
```

Se ver esse aviso, configure a API key no `.env`.

## ⚠️ Importante

- **Qdrant Cloud sempre requer API key**
- A API key é diferente da URL do cluster
- Mantenha a API key segura (não commite no Git)

## 📝 Checklist

- [ ] API key obtida do Qdrant Cloud
- [ ] `QDRANT_API_KEY` adicionada no `.env`
- [ ] Sem espaços ou aspas na API key
- [ ] Arquivo `.env` salvo
- [ ] Ingestão executada novamente

