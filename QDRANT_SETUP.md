# 🔧 Configuração do Qdrant - Guia Completo

## ❌ Problema Atual

O health check mostra:
```json
{
  "qdrant_connected": false,
  "collections": {"pix": false, "open_finance": false}
}
```

Isso significa que o **Qdrant não está conectado**.

## 🎯 Solução: Configurar Qdrant

Você tem 2 opções:

### Opção 1: Qdrant Cloud (Recomendado - Mais Fácil) ⭐

#### Passo 1: Criar Cluster no Qdrant Cloud

1. Acesse: https://cloud.qdrant.io
2. Crie uma conta (gratuita até 1GB)
3. Clique em "Create Cluster"
4. Escolha o plano Free (1GB)
5. Escolha a região (ex: us-east-1)
6. Clique em "Create"

#### Passo 2: Obter Credenciais

Após criar o cluster:
1. Clique no cluster criado
2. Vá em "API Keys" ou "Settings"
3. Copie:
   - **Cluster URL** (ex: `abc123-def456.us-east-1.qdrant.io`)
   - **API Key** (se necessário)

#### Passo 3: Configurar no Railway

No Railway:
1. Vá em **Settings** → **Variables**
2. Adicione/Edite:

```env
QDRANT_HOST=seu-cluster.us-east-1.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=sua-api-key-aqui  # Se o cluster exigir
```

**⚠️ IMPORTANTE:**
- Use apenas o hostname, SEM `https://` ou `http://`
- Exemplo correto: `abc123.us-east-1.qdrant.io`
- Exemplo errado: `https://abc123.us-east-1.qdrant.io`

#### Passo 4: Verificar Conexão

Após configurar, aguarde o redeploy e teste:
```bash
curl https://ragregulatorio-production.up.railway.app/health
```

Deve retornar:
```json
{
  "qdrant_connected": true,
  ...
}
```

---

### Opção 2: Qdrant Próprio (Servidor Dedicado)

Se você tem um servidor próprio:

#### Passo 1: Instalar Qdrant

```bash
# No seu servidor
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:v1.7.0
```

#### Passo 2: Configurar no Railway

```env
QDRANT_HOST=seu-ip-ou-dominio.com
QDRANT_PORT=6333
```

#### Passo 3: Verificar Acessibilidade

O Railway precisa conseguir acessar seu servidor:
- Verifique firewall (porta 6333 aberta)
- Verifique se o IP/domínio é acessível publicamente
- Teste: `curl http://seu-ip:6333/health`

---

## 🔍 Diagnóstico

### Verificar Variáveis no Railway

1. Railway → Seu Projeto → **Settings** → **Variables**
2. Verifique se existem:
   - `QDRANT_HOST`
   - `QDRANT_PORT` (opcional, padrão: 6333)

### Verificar Formato da URL

**Correto:**
```
QDRANT_HOST=abc123.us-east-1.qdrant.io
```

**Errado:**
```
QDRANT_HOST=https://abc123.us-east-1.qdrant.io
QDRANT_HOST=http://abc123.us-east-1.qdrant.io
QDRANT_HOST=abc123.us-east-1.qdrant.io:6333
```

### Verificar Logs do Railway

1. Railway → Deployments → Último deploy → **Logs**
2. Procure por:
   - Erros de conexão
   - "Connection refused"
   - "Timeout"
   - "Name resolution failed"

---

## 🐛 Problemas Comuns

### Problema 1: "Connection refused"

**Causa:** Qdrant não está rodando ou porta errada

**Solução:**
- Verifique se o Qdrant está ativo (Qdrant Cloud: dashboard)
- Verifique se a porta está correta (6333)
- Verifique firewall

### Problema 2: "Name resolution failed"

**Causa:** Hostname incorreto

**Solução:**
- Verifique se `QDRANT_HOST` está correto
- Remova `https://` ou `http://`
- Teste o hostname: `ping seu-cluster.qdrant.io`

### Problema 3: "Timeout"

**Causa:** Qdrant não acessível ou muito lento

**Solução:**
- Verifique se o cluster está ativo
- Verifique latência de rede
- Aumente timeout (edite código se necessário)

### Problema 4: "Unauthorized" ou "403"

**Causa:** API key incorreta ou ausente

**Solução:**
- Verifique se `QDRANT_API_KEY` está configurada
- Verifique se a API key está correta
- Gere nova API key se necessário

---

## ✅ Checklist de Configuração

- [ ] Qdrant Cloud criado OU servidor próprio configurado
- [ ] `QDRANT_HOST` configurado no Railway (sem https://)
- [ ] `QDRANT_PORT` configurado (ou deixar padrão 6333)
- [ ] `QDRANT_API_KEY` configurada (se necessário)
- [ ] Variáveis salvas no Railway
- [ ] Railway fez redeploy
- [ ] Health check retorna `qdrant_connected: true`

---

## 🚀 Próximos Passos

Após conectar o Qdrant:

1. **Indexar documentos:**
   ```bash
   curl -X POST "https://ragregulatorio-production.up.railway.app/reindex?domain=pix&force=true"
   ```

2. **Verificar health check novamente:**
   ```bash
   curl https://ragregulatorio-production.up.railway.app/health
   ```
   Deve mostrar `collections: {"pix": true}` após indexação

3. **Testar no frontend:**
   - Faça uma pergunta
   - Deve funcionar agora!

---

## 💡 Dica Rápida

**Para começar rápido:**
1. Use Qdrant Cloud (gratuito até 1GB)
2. Configure apenas `QDRANT_HOST` no Railway
3. Teste o health check
4. Indexe documentos

**Tempo estimado:** 5 minutos

