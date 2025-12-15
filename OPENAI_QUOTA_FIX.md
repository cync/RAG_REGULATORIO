# ⚠️ Erro: Quota Insuficiente da OpenAI

## 🔴 Problema Identificado

O erro `insufficient_quota` indica que sua conta da OpenAI **atingiu o limite de créditos/quota disponível**.

**Mensagem de erro:**
```
You exceeded your current quota, please check your plan and billing details.
```

## 🔍 Como Verificar

### 1. Acesse o Dashboard da OpenAI

1. Acesse: https://platform.openai.com/usage
2. Faça login na sua conta
3. Verifique:
   - **Usage** (uso atual)
   - **Billing** (faturamento)
   - **Limits** (limites da conta)

### 2. Verifique o Tipo de Conta

**Free Tier:**
- Créditos limitados (geralmente $5-18)
- Reset mensal (se disponível)
- Rate limit muito baixo (3 req/min)

**Tier Pago:**
- Créditos baseados no plano
- Rate limits maiores (300+ req/min)
- Billing automático

## ✅ Soluções

### Solução 1: Adicionar Créditos (Recomendado)

1. Acesse: https://platform.openai.com/account/billing
2. Clique em **"Add payment method"** ou **"Add credits"**
3. Adicione um método de pagamento
4. Adicione créditos (mínimo geralmente $5-10)

**Custo estimado para ingestão completa:**
- 17 PDFs × ~50 chunks cada = ~850 chunks
- 850 embeddings × ~$0.00013 = **~$0.11**
- Total: **Menos de $1** para processar todos os documentos

### Solução 2: Aguardar Reset (Free Tier)

Se você está no free tier:
- Verifique quando a quota reseta (geralmente mensal)
- Aguarde o reset para continuar
- **Nota**: Free tier tem rate limit muito baixo (3 req/min), pode demorar horas

### Solução 3: Upgrade do Plano

1. Acesse: https://platform.openai.com/account/billing
2. Faça upgrade para um plano pago
3. Benefícios:
   - Rate limits maiores (300 req/min vs 3 req/min)
   - Quota maior
   - Processamento muito mais rápido

## 💰 Custos Estimados

### Para Ingestão Completa

**17 PDFs com ~50 chunks cada:**
- Embeddings: ~850 × $0.00013 = **~$0.11**
- LLM (para consultas): ~$0.001-0.01 por consulta

**Total para ingestão: < $1**

### Para Uso Contínuo

**Por mês (estimativa):**
- 100 consultas/dia × 30 dias = 3.000 consultas
- Embeddings: 3.000 × $0.00013 = **~$0.39**
- LLM: 3.000 × $0.001 = **~$3.00**
- **Total: ~$3-5/mês**

## 🚀 Após Resolver a Quota

### 1. Verifique a Quota

```bash
# Verificar uso atual
# Acesse: https://platform.openai.com/usage
```

### 2. Execute a Ingestão Novamente

```bash
python -m app.ingestion.main pix
```

### 3. Monitore o Progresso

O sistema continuará de onde parou (arquivos não processados ainda estão em `data/raw/pix`).

## ⚠️ Prevenção

### 1. Monitorar Uso

- Configure alertas no dashboard da OpenAI
- Monitore uso regularmente
- Configure limites de gastos

### 2. Otimizar Custos

- Use batch processing quando possível
- Cache embeddings quando viável
- Processe em horários de menor demanda

### 3. Planejar Ingestão

- Para grandes volumes, considere processar em lotes
- Use tier pago para produção
- Reserve créditos para operação contínua

## 📋 Checklist

- [ ] Verificar quota atual no dashboard da OpenAI
- [ ] Adicionar método de pagamento (se necessário)
- [ ] Adicionar créditos (mínimo $5-10 recomendado)
- [ ] Verificar rate limits do plano
- [ ] Executar ingestão novamente
- [ ] Monitorar uso durante processamento

## 🔗 Links Úteis

- **Dashboard de Uso**: https://platform.openai.com/usage
- **Billing**: https://platform.openai.com/account/billing
- **Limits**: https://platform.openai.com/account/limits
- **Pricing**: https://openai.com/pricing

---

**Resumo**: Adicione créditos na conta da OpenAI (mínimo $5-10) e execute a ingestão novamente. O custo total será inferior a $1 para processar todos os documentos.

