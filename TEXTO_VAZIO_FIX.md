# 🔧 Correção: Chunks com Texto Vazio no Qdrant

## ❌ Problema Crítico Identificado

Os logs mostram que **TODOS os chunks recuperados têm `text_length: 0`**:
- 5 documentos foram encontrados pela busca vetorial
- Mas todos têm texto vazio
- Resultado: "Nenhum chunk válido com conteúdo para construir contexto"

## 🔍 Causa Raiz

O problema pode estar em:

1. **Indexação com texto vazio**: Os chunks foram indexados sem texto desde o início
2. **Problema na recuperação**: O Qdrant pode não estar retornando o campo `text` corretamente
3. **Serialização/Deserialização**: Problema na conversão do payload

## ✅ Correções Aplicadas

### 1. **Validação na Indexação**
- Chunks com texto vazio ou muito curto (< 10 caracteres) são **ignorados durante a indexação**
- Log de warning quando chunks são ignorados
- Log do primeiro chunk indexado para debug

### 2. **Logging Detalhado na Busca**
- Log quando chunks são recuperados com texto vazio
- Mostra `payload_keys` para verificar quais campos estão no payload
- Mostra tipo do texto (`payload_text_type`)
- Preview do payload completo

### 3. **Conversão Explícita**
- Garantir que o texto seja convertido para string explicitamente
- Tratar casos onde o payload pode retornar `None` ou tipo inesperado

## 🧪 Diagnóstico

Após o redeploy, os logs devem mostrar:

### Se o problema for na indexação:
```
"Chunk com texto vazio ignorado durante indexação"
```
Isso significa que os chunks estão sendo criados sem texto durante a ingestão.

### Se o problema for na recuperação:
```
"Chunk recuperado com texto vazio ou muito curto"
payload_keys: [...]
payload_text_type: ...
```
Isso mostra o que está no payload do Qdrant.

## 🔧 Solução: Reingestão

Se os chunks foram indexados sem texto, é necessário **reingestão completa**:

```bash
# 1. Verificar status atual
python scripts/check_ingestion_status.py

# 2. Resetar ingestão (mover arquivos de volta para raw)
python scripts/reset_ingestion.py pix

# 3. Verificar um arquivo manualmente
# Abra um PDF e verifique se tem texto selecionável (não é imagem escaneada)

# 4. Reingestão
python -m app.ingestion.main pix
```

## 📋 Verificações

### 1. Verificar Conteúdo dos Chunks no Qdrant

Execute o script de debug:
```bash
python scripts/debug_chunks.py
```

Isso mostra o conteúdo real dos chunks no Qdrant.

### 2. Verificar Extração de Texto

Teste a extração de um PDF manualmente:
```python
import pypdf
with open("data/raw/pix/arquivo.pdf", "rb") as f:
    reader = pypdf.PdfReader(f)
    for page in reader.pages:
        text = page.extract_text()
        print(f"Página {page.page_number}: {len(text)} caracteres")
        print(text[:500])
```

### 3. Verificar Chunking

Verifique se o chunking está preservando o texto:
```python
from app.ingestion.chunker import JuridicalChunker
chunker = JuridicalChunker()
chunks = chunker.chunk(texto, metadata)
for chunk in chunks:
    print(f"Chunk {chunk.chunk_id}: {len(chunk.text)} caracteres")
    print(chunk.text[:200])
```

## 🎯 Próximos Passos

1. **Aguardar redeploy** - As correções devem aparecer nos logs
2. **Verificar logs** - Identificar se o problema é na indexação ou recuperação
3. **Se necessário, reingestão** - Reindexar todos os documentos
4. **Testar consulta** - Após reingestão, testar novamente

## 📊 Checklist

- [x] Validação de texto vazio na indexação
- [x] Logging detalhado na busca
- [x] Conversão explícita de tipos
- [ ] Verificar logs após redeploy
- [ ] Identificar causa raiz (indexação vs recuperação)
- [ ] Reingestão se necessário
- [ ] Testar consulta após correções

---

**Status:** ✅ Correções aplicadas - aguarde redeploy e verifique os logs para identificar a causa raiz!

