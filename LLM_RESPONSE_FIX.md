# 🔧 Correção: LLM não está usando informações dos documentos

## ❌ Problema

O LLM está retornando "Não há base normativa explícita..." mesmo quando há documentos relevantes encontrados (`sources_count: 5`).

**Logs mostram:**
- ✅ Busca encontrou 5 documentos
- ✅ LLM foi chamado com sucesso (200 OK)
- ❌ Resposta não passou validação: `has_article_citation: false`, `has_normative_reference: false`
- ❌ LLM respondeu: "Não há base normativa explícita nos documentos analisados..."

## 🔍 Causa

O prompt não estava sendo suficientemente direto em instruir o LLM a:
1. Usar as informações dos documentos encontrados
2. Sempre citar artigo e norma
3. Reconhecer que os documentos foram encontrados como relevantes

## ✅ Correções Aplicadas

### 1. **SYSTEM_PROMPT melhorado**
- Instruções mais claras sobre usar os trechos fornecidos
- Ênfase que os trechos FORAM ENCONTRADOS como relevantes
- Formato de citação mais explícito

### 2. **Prompt de usuário mais direto**
- Removido texto desnecessário
- Instruções mais objetivas
- Exemplo de resposta correta
- Ênfase que os trechos CONTÊM informações relevantes

### 3. **Extração de citações melhorada**
- Sempre extrai citações dos sources, mesmo se LLM não citar
- Inclui citações no retorno mesmo se validação falhar

## 🚀 Próximos Passos

1. **Aguardar redeploy no Railway** (automático após push)

2. **Testar novamente:**
   ```bash
   curl -X POST https://ragregulatorio-production.up.railway.app/chat \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Quais são as obrigações de um PSP no PIX?",
       "domain": "pix"
     }'
   ```

3. **Verificar logs:**
   - Deve mostrar `has_article_citation: true` e `has_normative_reference: true`
   - Resposta deve conter citações explícitas

## 📋 Checklist

- [x] SYSTEM_PROMPT melhorado
- [x] Prompt de usuário mais direto
- [x] Extração de citações melhorada
- [ ] Testar após redeploy
- [ ] Verificar se validação passa

---

**Status:** ✅ Correções aplicadas - aguarde redeploy e teste novamente!

