# 🔧 Correção: Chunks com Metadados Incompletos e Texto Vazio

## ❌ Problema Identificado nos Logs

Os logs mostram que os chunks têm:
- **Metadados genéricos**: `norma: "Norma"`, `artigo: ""`, `numero_norma: "N/A"`
- **Texto possivelmente vazio**: `text_preview: "\n\n\n\..."`
- **Contexto mal formatado**: `"Norma N/A/2023"` não é útil para o LLM

**Resultado**: O LLM recebe contexto sem informações úteis e responde "Não há base normativa explícita..."

## 🔍 Causa Raiz

1. **Extração de metadados falhando**: Os documentos podem não ter metadados extraídos corretamente durante a ingestão
2. **Chunks vazios**: Alguns chunks podem ter sido criados sem conteúdo útil
3. **Contexto mal construído**: O contexto não filtra chunks vazios nem melhora metadados incompletos

## ✅ Correções Aplicadas

### 1. **Filtro de Chunks Vazios**
- Chunks com texto vazio ou muito curto (< 10 caracteres) são ignorados
- Log de warning quando chunks são ignorados

### 2. **Melhoria na Construção de Contexto**
- Quando `norma == "Norma"` (genérico), usa "Documento normativo"
- Quando `numero_norma == "N/A"`, omite da referência
- Formatação melhorada da referência normativa

### 3. **Validação de Contexto**
- Se não há contexto válido após filtrar chunks vazios, retorna erro imediatamente
- Evita chamar o LLM com contexto vazio

### 4. **Logging Melhorado**
- Mostra `valid_sources_count` (chunks válidos após filtro)
- Mostra `text_length` de cada source
- Ajuda a identificar se o problema é na ingestão ou na busca

## 🧪 Próximos Passos

### 1. **Verificar Ingestão**
Execute o script de debug para ver o conteúdo real dos chunks:

```bash
python scripts/debug_chunks.py
```

Isso mostra:
- Quantos chunks estão indexados
- Conteúdo real dos chunks
- Metadados de cada chunk

### 2. **Se Chunks Estiverem Vazios ou com Metadados Genéricos**

O problema está na **ingestão**. Possíveis causas:

- **PDFs não foram extraídos corretamente**
  - Verificar se os PDFs têm texto selecionável (não são imagens escaneadas)
  - Testar extração manual de um PDF

- **Extração de metadados falhando**
  - Verificar se os nomes dos arquivos seguem o padrão esperado
  - Verificar se o texto contém referências normativas

- **Chunking cortando informações importantes**
  - Verificar se o chunking está preservando artigos corretamente

### 3. **Reingestão**
Se os chunks estiverem vazios ou com metadados genéricos:

```bash
# Mover arquivos processados de volta para raw
python scripts/reset_ingestion.py pix

# Reingestão
python -m app.ingestion.main pix
```

### 4. **Verificar Logs Após Correções**
Após o redeploy, os logs devem mostrar:
- `valid_sources_count` > 0
- `text_length` > 10 para cada source
- Contexto com conteúdo útil

## 📋 Checklist

- [x] Filtro de chunks vazios implementado
- [x] Construção de contexto melhorada
- [x] Validação de contexto antes de chamar LLM
- [x] Logging detalhado adicionado
- [ ] Verificar conteúdo dos chunks com `debug_chunks.py`
- [ ] Se necessário, reingestão dos documentos
- [ ] Testar consulta após correções

## 🔍 Diagnóstico

Execute este comando para ver o status atual:

```bash
python scripts/check_ingestion_status.py
```

Isso mostra:
- Quantos documentos foram processados
- Quantos chunks foram criados
- Status das coleções no Qdrant

---

**Status:** ✅ Correções aplicadas - aguarde redeploy e verifique o conteúdo dos chunks!

