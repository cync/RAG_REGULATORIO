# 🔧 Troubleshooting - Problemas Comuns

## ❌ "Não há base normativa explícita nos documentos analisados"

Este erro indica que **não há documentos indexados** ou o **Qdrant não está conectado**.

### Diagnóstico Passo a Passo

#### 1. Verificar Health Check

Acesse: `https://ragregulatorio-production.up.railway.app/health`

**Resposta esperada:**
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

**Se retornar:**
- `qdrant_connected: false` → Problema de conexão com Qdrant
- `collections: {"pix": false, "open_finance": false}` → Não há documentos indexados

#### 2. Verificar Variáveis de Ambiente no Railway

Certifique-se de que estas variáveis estão configuradas:

```env
OPENAI_API_KEY=sk-...
QDRANT_HOST=seu-cluster.qdrant.io  # ou IP do servidor
QDRANT_PORT=6333
```

**Como verificar:**
1. Railway → Seu projeto → Settings → Variables
2. Verifique se `QDRANT_HOST` está correto
3. Se usar Qdrant Cloud, verifique se a URL está correta

#### 3. Verificar se há Documentos Indexados

**Opção A: Via API (se tiver acesso ao Qdrant)**
```bash
curl https://ragregulatorio-production.up.railway.app/health
```

**Opção B: Verificar logs do Railway**
- Railway → Deployments → Clique no último deploy → Logs
- Procure por mensagens de ingestão ou erros de conexão

#### 4. Indexar Documentos

Se não há documentos indexados, você precisa fazer a ingestão:

**Opção A: Via API (Reindex)**
```bash
curl -X POST "https://ragregulatorio-production.up.railway.app/reindex?domain=pix&force=true"
```

**Opção B: Localmente (se tiver acesso ao servidor)**
```bash
python -m app.ingestion.main pix
python -m app.ingestion.main open_finance
```

**⚠️ IMPORTANTE:** Para fazer ingestão, você precisa:
1. Ter documentos PDF/HTML em `data/raw/pix/` ou `data/raw/open_finance/`
2. Ter acesso ao Qdrant configurado
3. Ter `OPENAI_API_KEY` configurada

## 🔍 Problemas Comuns

### Problema 1: Qdrant não conecta

**Sintomas:**
- Health check retorna `qdrant_connected: false`
- Erros de conexão nos logs

**Soluções:**
1. Verifique `QDRANT_HOST` no Railway
2. Se usar Qdrant Cloud, verifique se o cluster está ativo
3. Verifique se a porta está correta (6333)
4. Se usar Qdrant próprio, verifique firewall/security groups

### Problema 2: Nenhum documento indexado

**Sintomas:**
- Health check retorna `collections: {"pix": false}`
- Todas as perguntas retornam "não há base normativa"

**Soluções:**
1. Faça ingestão de documentos (veja passo 4 acima)
2. Verifique se há arquivos em `data/raw/`
3. Verifique logs de ingestão para erros

### Problema 3: Busca não encontra resultados relevantes

**Sintomas:**
- Há documentos indexados
- Mas perguntas retornam "não há base normativa"

**Soluções:**
1. Verifique `MIN_SIMILARITY_SCORE` (padrão: 0.7)
   - Pode estar muito alto, tente reduzir para 0.5
2. Verifique se os documentos são relevantes para a pergunta
3. Tente perguntas mais específicas com termos normativos

### Problema 4: Erro de autenticação OpenAI

**Sintomas:**
- Erros nos logs sobre API key inválida
- Timeout nas requisições

**Soluções:**
1. Verifique se `OPENAI_API_KEY` está correta no Railway
2. Verifique se a chave não expirou
3. Verifique limites de uso da API

## 📋 Checklist de Diagnóstico

- [ ] Health check retorna `healthy`
- [ ] `qdrant_connected: true`
- [ ] `collections` mostra `true` para pelo menos um domínio
- [ ] `OPENAI_API_KEY` configurada no Railway
- [ ] `QDRANT_HOST` configurada corretamente
- [ ] Documentos foram indexados (verificar via health check)
- [ ] Logs não mostram erros de conexão

## 🚀 Solução Rápida

Se você acabou de fazer deploy e não indexou documentos ainda:

1. **Configure Qdrant:**
   - Use Qdrant Cloud (mais fácil): https://cloud.qdrant.io
   - Ou configure seu próprio servidor Qdrant

2. **Configure variáveis no Railway:**
   ```
   QDRANT_HOST=seu-cluster.qdrant.io
   QDRANT_PORT=6333
   ```

3. **Faça ingestão de documentos:**
   - Coloque PDFs/HTMLs em `data/raw/pix/` ou `data/raw/open_finance/`
   - Execute ingestão (localmente ou via API)

4. **Teste novamente:**
   - Acesse o health check
   - Faça uma pergunta no frontend

## 💡 Dica

Para testar rapidamente se o sistema está funcionando:

1. Acesse: `https://ragregulatorio-production.up.railway.app/health`
2. Se `collections` estiver `false`, você precisa indexar documentos
3. Se `qdrant_connected` estiver `false`, verifique a conexão com Qdrant

