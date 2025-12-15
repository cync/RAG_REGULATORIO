# 🔧 Correção: Erro no Frontend

## ❌ Problema

Erro "Application error: a client-side exception has occurred" no frontend.

## 🔍 Causa

A interface `ChatResponse` no frontend esperava `sources` com estrutura diferente do que o backend retorna:

**Frontend esperava:**
```typescript
sources: Array<{
  text: string
  metadata: { ... }
  score: number
}>
```

**Backend retorna:**
```typescript
sources: Array<{
  fonte: string
  norma: string
  numero_norma: string
  artigo: string | null
  ano: number
  tema: string
  url: string | null
}>
```

## ✅ Correção Aplicada

1. **Interface atualizada** - `ChatResponse` agora corresponde ao formato do backend
2. **Renderização corrigida** - Ajustado para usar `source.norma` ao invés de `source.metadata.norma`
3. **Tratamento de erros melhorado** - Mostra mensagens de erro mais detalhadas

## 🚀 Próximos Passos

### Se o frontend estiver no Vercel:

1. **Verificar variável de ambiente:**
   - Vá em Settings → Environment Variables
   - Confirme que `NEXT_PUBLIC_API_URL` está configurada
   - Deve apontar para: `https://ragregulatorio-production.up.railway.app`

2. **Redeploy:**
   - O Vercel deve fazer redeploy automaticamente após o push
   - Ou force um redeploy manualmente

3. **Testar:**
   - Acesse o frontend
   - Faça uma consulta
   - Deve funcionar agora

### Se estiver rodando localmente:

```bash
cd frontend
npm install
npm run dev
```

Certifique-se de ter `.env.local` com:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📋 Checklist

- [ ] Interface `ChatResponse` atualizada
- [ ] Renderização de sources corrigida
- [ ] Tratamento de erros melhorado
- [ ] Variável `NEXT_PUBLIC_API_URL` configurada no Vercel
- [ ] Frontend redeployado

---

**Status:** ✅ Correções aplicadas - aguarde redeploy do frontend!

