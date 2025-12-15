# 📊 Monitorando a Ingestão em Tempo Real

## 🔄 O que Está Acontecendo Agora

Durante a ingestão, o sistema está:

1. **Parseando PDFs** (rápido - ~5-10s por arquivo)
2. **Criando chunks jurídicos** (rápido - ~1-2s por arquivo)
3. **Gerando embeddings** (LENTO - depende do rate limit) ⚠️
4. **Indexando no Qdrant** (rápido - ~1-2s por batch)

## 📈 Como Monitorar

### Opção 1: Logs do Terminal

Você verá logs como:

```
Processando arquivo: IN_16.pdf [1/17]
Chunks criados: 45
Gerando embeddings... (pode demorar)
Rate limit atingido, aguardando 2s
Chunks indexados: 45
Arquivo processado com sucesso [1/17]
Total chunks até agora: 45
```

**O que observar:**
- ✅ Progresso: `[3/17]` = arquivo 3 de 17
- ✅ Chunks criados por arquivo
- ⚠️ Avisos de rate limit (normal, o sistema aguarda automaticamente)
- ✅ Total acumulado de chunks

### Opção 2: Verificar Status via API

Em outro terminal, você pode verificar o status:

```bash
# Verificar saúde do sistema
curl https://seu-dominio.com/health

# Ou localmente
curl http://localhost:8000/health
```

**Resposta esperada durante ingestão:**
```json
{
  "status": "degraded",
  "qdrant_connected": true,
  "collections": {
    "pix": false,  // Ainda vazia ou em processo
    "open_finance": false
  }
}
```

**Resposta esperada após ingestão:**
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "collections": {
    "pix": true,  // ✅ Populada!
    "open_finance": false
  }
}
```

### Opção 3: Verificar Logs em Arquivo

```bash
# Ver últimas linhas do log
tail -f logs/app.log

# Ou no Windows PowerShell
Get-Content logs/app.log -Tail 50 -Wait
```

## ⏱️ Tempo Estimado

### Com Free Tier da OpenAI (3 req/min)
- **17 PDFs:** 30-60 minutos
- **Pode chegar a 1-2 horas** se muitos rate limits

### Com Tier Pago (300 req/min)
- **17 PDFs:** 5-15 minutos

## ✅ Sinais de Sucesso

**Durante a ingestão:**
- Logs mostrando progresso `[X/17]`
- Chunks sendo criados e indexados
- Avisos de rate limit (normal, sistema aguarda)

**Ao finalizar:**
- Mensagem: `Ingestão concluída`
- Total de chunks processados
- Arquivos movidos para `data/processed/`

## ⚠️ Sinais de Problema

**Se parar de processar:**
- Nenhum log novo por mais de 5 minutos
- Muitos erros consecutivos
- Erro de conexão com Qdrant

**O que fazer:**
1. Verificar logs para erro específico
2. Verificar `QDRANT_API_KEY` (se usar Qdrant Cloud)
3. Verificar `OPENAI_API_KEY`
4. Tentar executar novamente (é idempotente)

## 🎯 O que Fazer Quando Terminar

### 1. Verificar Status

```bash
curl https://seu-dominio.com/health
```

Deve mostrar `"pix": true` se populada.

### 2. Testar uma Consulta

```bash
curl -X POST https://seu-dominio.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "quais são as obrigações de um PSP no Pix?",
    "domain": "pix"
  }'
```

**Resposta esperada:**
- `has_sufficient_context: true`
- `sources_count: > 0`
- `answer` com referências normativas

### 3. Verificar Quantidade de Documentos

```bash
# Via código Python
python -c "
from app.rag.vector_store import VectorStore
vs = VectorStore()
info = vs.get_collection_info('pix')
print(f'Chunks indexados: {info[\"points_count\"]}')
"
```

## 📋 Checklist Pós-Ingestão

- [ ] Ingestão concluída sem erros
- [ ] `/health` mostra `"pix": true`
- [ ] Teste de consulta retorna documentos
- [ ] `sources_count > 0` nas respostas
- [ ] Respostas contêm referências normativas

## 🔄 Se Precisar Reexecutar

A ingestão é **idempotente**:
- Arquivos já processados são ignorados
- Você pode executar novamente sem problemas
- Use `--force-reindex` para reprocessar tudo:

```bash
python -m app.ingestion.main pix --force-reindex
```

## 💡 Dicas

1. **Deixe rodando em background** - pode demorar
2. **Monitore os logs** - veja o progresso
3. **Não interrompa** - o sistema faz retry automático
4. **Aguarde conclusão** - especialmente com free tier

---

**Resumo:** Deixe rodando! O sistema faz retry automático. Quando terminar, teste com `/chat`!

