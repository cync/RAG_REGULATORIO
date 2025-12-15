# 🔧 Correção: LLM Responde "Não há base normativa" mesmo com documentos

## ❌ Problema

O LLM está respondendo "Não há base normativa explícita nos documentos analisados..." mesmo quando:
- ✅ 5 documentos foram encontrados (`sources_count: 5`)
- ✅ A busca semântica funcionou
- ✅ Os documentos foram enviados ao LLM

**Logs mostram:**
```
validations: {
  "has_article_citation": false,
  "has_normative_reference": false
}
answer_preview: "Não há base normativa explícita nos documentos anali..."
```

## 🔍 Causa

O LLM não está sendo instruído de forma suficientemente clara para:
1. **Reconhecer** que os trechos foram encontrados como relevantes
2. **Analisar** o conteúdo dos trechos antes de responder
3. **Extrair** informações dos trechos para construir a resposta

## ✅ Correções Aplicadas

### 1. **SYSTEM_PROMPT Melhorado**
- Instruções mais explícitas sobre usar os trechos fornecidos
- Enfatiza que os trechos FORAM ENCONTRADOS como relevantes
- Instrui a ANALISAR antes de responder

### 2. **Prompt de Usuário Melhorado**
- Enfatiza que os trechos CONTÊM informações relevantes
- Instrui a EXTRAIR informações dos trechos
- Formato obrigatório de resposta com citação
- Exemplo claro de resposta correta

### 3. **Script de Debug Criado**
- `scripts/debug_chunks.py` - Para verificar o conteúdo dos chunks indexados
- Ajuda a identificar se os chunks têm conteúdo útil

## 🧪 Como Testar

### 1. Verificar conteúdo dos chunks:
```bash
python scripts/debug_chunks.py
```

Isso mostra:
- Quantos chunks estão indexados
- Conteúdo dos primeiros 5 chunks
- Metadados (norma, artigo, ano)

### 2. Testar consulta:
```bash
curl -X POST https://ragregulatorio-production.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais são as obrigações de um PSP no Pix?",
    "domain": "pix"
  }'
```

### 3. Verificar logs no Railway:
- A resposta deve começar com "Conforme Art. X..."
- `has_article_citation: true`
- `has_normative_reference: true`

## 🔍 Possíveis Causas Adicionais

Se ainda não funcionar, verifique:

1. **Chunks vazios ou sem conteúdo útil:**
   ```bash
   python scripts/debug_chunks.py
   ```
   - Se os chunks estiverem vazios ou com conteúdo irrelevante, a ingestão pode ter problemas

2. **Score muito baixo:**
   - Verifique os scores dos documentos encontrados nos logs
   - Se todos os scores forem muito baixos (< 0.2), os documentos podem não ser relevantes

3. **Conteúdo dos documentos:**
   - Os PDFs podem não ter sido extraídos corretamente
   - O chunking pode ter cortado informações importantes

## 📋 Checklist

- [x] SYSTEM_PROMPT melhorado
- [x] Prompt de usuário melhorado
- [x] Script de debug criado
- [ ] Testar consulta após deploy
- [ ] Verificar logs de resposta
- [ ] Se necessário, verificar conteúdo dos chunks

---

**Status:** ✅ Correções aplicadas - aguarde redeploy e teste novamente!
