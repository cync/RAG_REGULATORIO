# 📚 Guia de Indexação de Documentos

## ✅ Status Atual

O Qdrant está conectado, mas as coleções estão vazias:
```json
{
  "qdrant_connected": true,
  "collections": {"pix": false, "open_finance": false}
}
```

Isso significa que você precisa **indexar documentos** para o sistema funcionar.

## 🎯 Como Indexar Documentos

### Opção 1: Via API (Recomendado)

#### Passo 1: Preparar Documentos

Você precisa ter documentos PDF ou HTML sobre Pix e Open Finance do Banco Central.

**Estrutura de pastas:**
```
data/raw/
  ├── pix/
  │   ├── circular_123_2023.pdf
  │   └── resolucao_456_2023.pdf
  └── open_finance/
      ├── circular_789_2023.pdf
      └── resolucao_012_2023.pdf
```

**Onde obter documentos:**

**Pix:**
- Todas as normas do Pix: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
- Use o script automático: `python scripts/download_pix_normas.py`

**Open Finance:**
- Site do Banco Central: https://www.bcb.gov.br
- Buscar por "Open Finance"
- Baixar PDFs das normas, circulares, resoluções

#### Passo 2: Fazer Upload dos Documentos

**Opção A: Via Git (se tiver acesso ao repositório)**
```bash
# Coloque os PDFs nas pastas corretas
# Commit e push
git add data/raw/pix/*.pdf
git commit -m "Adiciona documentos do Pix"
git push
```

**Opção B: Via Railway (se tiver acesso ao container)**
- Mais complexo, requer acesso SSH ao container

**Opção C: Indexar localmente e sincronizar**
- Indexe localmente no seu computador
- Os vetores ficam no Qdrant Cloud (compartilhado)

#### Passo 3: Executar Ingestão

**Via API (se os documentos estiverem no servidor):**
```bash
curl -X POST "https://ragregulatorio-production.up.railway.app/reindex?domain=pix&force=true"
```

**Localmente (recomendado):**
```bash
cd C:\Users\Felipe\RAG_REGULATORIO

# Coloque os PDFs em data/raw/pix/ ou data/raw/open_finance/

# Execute a ingestão
python -m app.ingestion.main pix
python -m app.ingestion.main open_finance
```

### Opção 2: Indexação Local (Mais Fácil)

#### Passo 1: Configurar Ambiente Local

```bash
cd C:\Users\Felipe\RAG_REGULATORIO

# Instalar dependências (se ainda não instalou)
pip install -r requirements.txt

# Configurar .env
# Copie .env.example para .env
# Configure:
# OPENAI_API_KEY=sk-...
# QDRANT_HOST=seu-cluster.qdrant.io
# QDRANT_API_KEY=sua-api-key
```

#### Passo 2: Baixar Documentos

**Opção A: Download Automático (Pix) - Recomendado**

```bash
# Baixar automaticamente as normas do Pix
python scripts/download_pix_normas.py
```

Este script:
- Acessa: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
- Baixa todos os PDFs disponíveis
- Salva em `data/raw/pix/`

**Opção B: Download Manual**

1. **Pix:** Acesse https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
2. Baixe os PDFs manualmente
3. Coloque em `data/raw/pix/`

4. **Open Finance:** Busque no site do Bacen
5. Baixe os PDFs
6. Coloque em `data/raw/open_finance/`

**Dica:** Organize os arquivos com nomes descritivos:
- `pix_circular_123_2023.pdf`
- `open_finance_resolucao_456_2023.pdf`

#### Passo 3: Executar Ingestão

```bash
# Para Pix
python -m app.ingestion.main pix

# Para Open Finance
python -m app.ingestion.main open_finance

# Para reindexar completamente (limpa e recria)
python -m app.ingestion.main pix --force
python -m app.ingestion.main open_finance --force
```

#### Passo 4: Verificar

Após a ingestão, teste:
```bash
curl https://ragregulatorio-production.up.railway.app/health
```

Deve retornar:
```json
{
  "collections": {
    "pix": true,  // ← Agora deve ser true
    "open_finance": true
  }
}
```

## 📋 Processo de Ingestão

O sistema faz automaticamente:

1. **Parse dos documentos** (PDF/HTML)
2. **Extração de metadados** (norma, artigo, ano, etc.)
3. **Chunking jurídico** (divide por artigo/inciso)
4. **Geração de embeddings** (vetorização)
5. **Indexação no Qdrant** (armazenamento)

## ⚠️ Importante

### Rate Limits da OpenAI

Durante a ingestão, você pode encontrar rate limits:
- **Free tier:** 3 requisições/minuto
- **Tier pago:** 300 requisições/minuto

**Solução:** O sistema já tem retry automático, mas pode demorar.

### Tempo de Ingestão

- **1 documento pequeno:** ~30 segundos
- **10 documentos:** ~5-10 minutos (free tier)
- **100 documentos:** ~1-2 horas (free tier)

### Custo

- **Embeddings:** ~$0.0001 por 1K tokens
- **100 documentos:** ~$1-5 (dependendo do tamanho)

## 🧪 Testar Após Indexação

1. **Health check:**
   ```bash
   curl https://ragregulatorio-production.up.railway.app/health
   ```

2. **Fazer uma pergunta:**
   ```bash
   curl -X POST https://ragregulatorio-production.up.railway.app/chat \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Quais são as obrigações de um PSP no Pix?",
       "domain": "pix"
     }'
   ```

3. **No frontend:**
   - Acesse o frontend no Vercel
   - Faça uma pergunta
   - Deve retornar resposta com base normativa

## 📝 Checklist

- [ ] Documentos PDF/HTML obtidos do Bacen
- [ ] Documentos colocados em `data/raw/pix/` ou `data/raw/open_finance/`
- [ ] `.env` configurado localmente (se indexar localmente)
- [ ] Ingestão executada
- [ ] Health check mostra `collections: {"pix": true}`
- [ ] Teste de pergunta funcionando

## 💡 Dicas

1. **Comece pequeno:** Indexe 1-2 documentos primeiro para testar
2. **Organize bem:** Use nomes descritivos nos arquivos
3. **Monitore logs:** Acompanhe o progresso da ingestão
4. **Use tier pago:** Se tiver muitos documentos, considere upgrade da OpenAI

## 🆘 Problemas Comuns

### Erro: "No module named 'app'"
**Solução:** Execute de dentro da pasta do projeto:
```bash
cd C:\Users\Felipe\RAG_REGULATORIO
python -m app.ingestion.main pix
```

### Erro: "OPENAI_API_KEY não configurada"
**Solução:** Configure no `.env` local

### Erro: Rate limit
**Solução:** Aguarde ou use tier pago da OpenAI

### Documentos não aparecem
**Solução:** Verifique se os arquivos estão em `data/raw/pix/` ou `data/raw/open_finance/`

