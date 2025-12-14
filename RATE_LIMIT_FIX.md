# 🔧 Correção de Rate Limit (429 Too Many Requests)

## Problema

A API da OpenAI está retornando erro 429 (Too Many Requests) quando há muitas requisições simultâneas ou frequentes.

## Solução Implementada

### 1. Retry com Backoff Exponencial

Adicionei retry automático com backoff exponencial em:
- Geração de embeddings (indexação)
- Geração de embeddings (busca)
- Chamadas ao LLM

**Como funciona:**
- Tenta até 5 vezes
- Espera: 1s, 2s, 4s, 8s, 16s entre tentativas
- Loga avisos para monitoramento

### 2. Delay entre Requisições

- Adicionado delay de 100ms entre embeddings durante indexação
- Reduz carga na API da OpenAI

### 3. Tratamento de Erros

- Erros 429 são capturados e tratados
- Logs informativos para debug
- Erro final apenas após todas as tentativas

## Como Usar

### Durante Ingestão

Se você estiver indexando muitos documentos:

1. **Reduza o batch size** (processe menos documentos por vez)
2. **Aumente o delay** se necessário (edite `time.sleep(0.1)` em `vector_store.py`)
3. **Use OpenAI com rate limits maiores** (tier pago)

### Durante Busca

A busca já tem retry automático. Se ainda receber 429:

1. Verifique seu plano OpenAI (free tier tem limites baixos)
2. Aguarde alguns segundos e tente novamente
3. Considere upgrade do plano OpenAI

## Configurações Recomendadas

### Para Contas Free Tier

```python
# Em vector_store.py, linha ~70
time.sleep(0.2)  # Aumentar para 200ms entre requisições
```

### Para Contas Pagas

```python
# Em vector_store.py, linha ~70
time.sleep(0.05)  # Reduzir para 50ms (mais rápido)
```

## Monitoramento

Os logs agora mostram:
- Quando rate limit é atingido
- Quantas tentativas foram feitas
- Tempo de espera antes de retry

Exemplo de log:
```
WARNING: Rate limit atingido, aguardando attempt=2 wait_seconds=2 chunk_index=5
```

## Limites da OpenAI

### Free Tier
- 3 requisições/minuto para embeddings
- 3 requisições/minuto para chat completions

### Tier Pago (Pay-as-you-go)
- 300 requisições/minuto para embeddings
- 500 requisições/minuto para chat completions

## Dicas

1. **Para ingestão inicial:** Processe documentos em lotes pequenos
2. **Para produção:** Use tier pago da OpenAI
3. **Monitor logs:** Acompanhe avisos de rate limit
4. **Ajuste delays:** Baseado no seu plano OpenAI

