# 🔧 Solução para Erro 403 Forbidden no Qdrant Cloud

## ❌ Problema

Erro `403 Forbidden` mesmo com API key configurada.

## 🔍 Possíveis Causas

### 1. API Key Incorreta ou Expirada

**Solução:**
1. Acesse: https://cloud.qdrant.io
2. Vá no seu cluster
3. Vá em **"API Keys"**
4. Verifique se a API key existe e está ativa
5. Se necessário, crie uma nova API key
6. Copie a API key **completa**
7. Atualize no `.env`:
   ```
   QDRANT_API_KEY=nova-api-key-completa
   ```

### 2. API Key sem Permissões Adequadas

**Solução:**
- Certifique-se de que a API key tem permissões de **leitura e escrita**
- Algumas API keys podem ser somente leitura

### 3. API Key de Cluster Diferente

**Solução:**
- Verifique se a API key foi gerada para o cluster correto
- Cada cluster tem suas próprias API keys

### 4. Formato da API Key

**Verificar:**
- A API key não deve ter espaços
- A API key não deve estar entre aspas no `.env`
- A API key deve estar na mesma linha que `QDRANT_API_KEY=`

## ✅ Passo a Passo para Resolver

### Passo 1: Verificar API Key no Qdrant Cloud

1. Acesse: https://cloud.qdrant.io
2. Faça login
3. Clique no seu cluster
4. Vá em **"API Keys"** ou **"Settings"** → **"API Keys"**
5. Verifique:
   - Se a API key existe
   - Se está ativa (não expirada)
   - Se tem permissões adequadas

### Passo 2: Criar Nova API Key (se necessário)

1. No Qdrant Cloud, clique em **"Create API Key"**
2. Dê um nome (ex: "RAG Regulatorio")
3. Selecione permissões: **Read & Write**
4. Copie a API key **imediatamente** (você só verá uma vez)
5. Cole no `.env`

### Passo 3: Atualizar .env

Edite `C:\Users\Felipe\RAG_REGULATORIO\.env`:

```env
QDRANT_API_KEY=sua-nova-api-key-aqui
```

**Importante:**
- Sem espaços antes ou depois do `=`
- Sem aspas
- API key completa na mesma linha

### Passo 4: Testar

```bash
cd C:\Users\Felipe\RAG_REGULATORIO
python -m app.ingestion.main pix
```

## 🔍 Verificar se Está Funcionando

Se a API key estiver correta, você verá:

```
Conexão com Qdrant Cloud validada com sucesso
```

Se ainda der 403, a API key está incorreta ou sem permissões.

## 💡 Dica

Se você tem múltiplos clusters no Qdrant Cloud:
- Certifique-se de usar a API key do cluster correto
- Verifique se o `QDRANT_HOST` corresponde ao cluster da API key

## 📝 Checklist

- [ ] API key existe no Qdrant Cloud
- [ ] API key está ativa (não expirada)
- [ ] API key tem permissões de leitura/escrita
- [ ] API key foi gerada para o cluster correto
- [ ] API key está correta no `.env` (sem espaços, sem aspas)
- [ ] Teste de conexão passou

