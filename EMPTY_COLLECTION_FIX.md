# 🔍 Problema: Coleção Vazia (sources_count: 0)

## 📊 Sintomas dos Logs

Os logs mostram:
- ✅ API funcionando (200 OK)
- ❌ `sources_count: 0` - Nenhum documento encontrado
- ❌ `has_sufficient_context: false` - Sem contexto
- ⚠️ Rate limits da OpenAI (429) durante busca
- ⚠️ Timeout de 34 segundos (devido aos retries)

## 🎯 Causa Raiz

**A coleção do Qdrant está vazia** - não há documentos indexados ainda.

Isso acontece porque:
1. A ingestão ainda não foi executada com sucesso
2. Ou a ingestão falhou antes de indexar documentos
3. Ou o problema do `QDRANT_API_KEY` (403) impediu a indexação

## ✅ Solução

### Passo 1: Verificar Status da Coleção

Execute o endpoint `/health`:

```bash
curl https://seu-dominio.com/health
```

Você deve ver algo como:
```json
{
  "status": "degraded",
  "qdrant_connected": true,
  "collections": {
    "pix": false,  // ← false = vazia
    "open_finance": false
  }
}
```

### Passo 2: Resolver QDRANT_API_KEY (se necessário)

Se ainda estiver com erro 403:
1. Acesse https://cloud.qdrant.io
2. Crie uma nova API Key com permissões **Read & Write**
3. Atualize no `.env` e no Railway

### Passo 3: Executar Ingestão

**Localmente:**
```bash
cd C:\Users\Felipe\RAG_REGULATORIO
python -m app.ingestion.main pix
```

**No Railway (via SSH ou localmente apontando para Railway):**
```bash
# Via Railway CLI
railway run python -m app.ingestion.main pix

# Ou via endpoint /reindex (se implementado)
curl -X POST https://seu-dominio.com/reindex?domain=pix
```

### Passo 4: Verificar Progresso

Durante a ingestão, você verá logs como:
```
Processando arquivo: IN_16.pdf [1/17]
Chunks criados: 45
Gerando embeddings...
Chunks indexados: 45
Arquivo processado com sucesso [1/17]
```

### Passo 5: Verificar Novamente

Após a ingestão, verifique `/health`:
```json
{
  "collections": {
    "pix": true,  // ← true = tem documentos
    "open_finance": false
  }
}
```

## 🔧 Melhorias Implementadas

### 1. Timeout Aumentado
- **Antes:** 30 segundos
- **Agora:** 60 segundos
- **Motivo:** Dar tempo aos retries de rate limit

### 2. Retry Unificado
- Busca agora usa a mesma função `_get_embedding_with_retry()` que a indexação
- Retry automático com exponential backoff
- Logs mais claros

### 3. Logs Melhorados
- Progresso da ingestão (`[3/17]`)
- Chunks criados por arquivo
- Total acumulado

## ⚠️ Rate Limits Durante Busca

**É normal** ter rate limits durante a busca também, não apenas na ingestão:
- Cada busca precisa gerar 1 embedding da query
- Com free tier (3 req/min), pode demorar
- O sistema faz retry automático

**Solução:**
- Usar tier pago da OpenAI (300 req/min)
- Ou aguardar os retries automáticos

## 📋 Checklist

- [ ] Verificar `/health` - coleção está vazia?
- [ ] Resolver `QDRANT_API_KEY` se necessário
- [ ] Executar ingestão (`python -m app.ingestion.main pix`)
- [ ] Aguardar conclusão (30-60 min com free tier)
- [ ] Verificar `/health` novamente - coleção populada?
- [ ] Testar `/chat` - deve retornar documentos agora

## 🎯 Próximos Passos

1. **Resolver QDRANT_API_KEY** (se ainda com 403)
2. **Executar ingestão** localmente ou no Railway
3. **Aguardar conclusão** (pode demorar 30-60 min)
4. **Testar novamente** - deve funcionar!

---

**Resumo:** O sistema está funcionando, mas precisa de documentos indexados. Execute a ingestão primeiro!

