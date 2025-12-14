# 🚀 Deploy do Frontend no Vercel

## O que hospedar no Vercel?

**A pasta `frontend/`** - Um frontend Next.js que se conecta ao backend no Railway.

## 📋 Passo a Passo

### 1. Preparar o Frontend

O frontend já está criado em `frontend/`. Ele é uma aplicação Next.js com:
- Interface moderna e responsiva
- Conexão com o backend via API
- Suporte a Pix e Open Finance

### 2. Deploy no Vercel

#### Opção A: Via Interface Web (Mais Fácil)

1. **Acesse:** https://vercel.com/new
2. **Conecte seu GitHub:**
   - Clique em "Import Project"
   - Selecione o repositório `cync/RAG_REGULATORIO`
3. **Configure o projeto:**
   - **Root Directory:** Selecione `frontend`
   - **Framework Preset:** Next.js (detectado automaticamente)
   - **Build Command:** `npm run build` (automático)
   - **Output Directory:** `.next` (automático)
4. **Configure variáveis de ambiente:**
   - Clique em "Environment Variables"
   - Adicione:
     ```
     NEXT_PUBLIC_API_URL=https://seu-backend.railway.app
     ```
   - **Substitua** `seu-backend.railway.app` pela URL real do seu backend no Railway
5. **Deploy:**
   - Clique em "Deploy"
   - Aguarde o build (2-3 minutos)
   - Pronto! 🎉

#### Opção B: Via CLI

```bash
cd frontend
npm install

# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Quando perguntar:
# - Set up and deploy? Yes
# - Which scope? (selecione sua conta)
# - Link to existing project? No
# - Project name? rag-regulatorio (ou outro)
# - Directory? ./
# - Override settings? No

# Adicionar variável de ambiente
vercel env add NEXT_PUBLIC_API_URL production
# Digite: https://seu-backend.railway.app
```

### 3. Obter URL do Backend

No Railway:
1. Acesse seu projeto
2. Vá em Settings → Networking
3. Copie a URL pública (ex: `rag-regulatorio-production.up.railway.app`)

Use essa URL no `NEXT_PUBLIC_API_URL`.

### 4. Testar

Após o deploy:
1. Acesse a URL fornecida pelo Vercel (ex: `rag-regulatorio.vercel.app`)
2. Teste fazendo uma pergunta
3. Verifique se conecta ao backend

## 🔧 Configurações Importantes

### Variáveis de Ambiente no Vercel

```
NEXT_PUBLIC_API_URL=https://seu-backend.railway.app
```

**Importante:** 
- Use `NEXT_PUBLIC_` para variáveis acessíveis no frontend
- Substitua pela URL real do seu backend

### CORS no Backend

O backend já está configurado para aceitar requisições do Vercel:
- `https://*.vercel.app` está na lista de origens permitidas

Se usar um domínio customizado, adicione no backend:
```python
# No Railway, adicione variável de ambiente:
FRONTEND_URL=https://seu-dominio.com
```

## 📱 Estrutura do Frontend

```
frontend/
├── src/
│   └── app/
│       ├── page.tsx      # Página principal (chat)
│       ├── layout.tsx     # Layout base
│       └── globals.css    # Estilos
├── package.json
├── next.config.js
└── tailwind.config.js
```

## 🎨 Funcionalidades

- ✅ Interface moderna com Tailwind CSS
- ✅ Seleção de domínio (Pix/Open Finance)
- ✅ Exibição de respostas formatadas
- ✅ Citações normativas
- ✅ Documentos utilizados
- ✅ Indicador de contexto suficiente
- ✅ Responsivo (mobile-friendly)

## 🐛 Troubleshooting

### Erro: "Failed to fetch"
- Verifique se `NEXT_PUBLIC_API_URL` está correto
- Verifique se o backend no Railway está rodando
- Verifique CORS no backend

### Erro: "Build failed"
- Verifique se todas as dependências estão no `package.json`
- Verifique logs do build no Vercel

### Frontend não conecta ao backend
- Verifique a URL do backend
- Verifique se o backend está acessível publicamente
- Verifique CORS no backend

## ✅ Checklist

- [ ] Frontend deployado no Vercel
- [ ] `NEXT_PUBLIC_API_URL` configurado
- [ ] Backend acessível publicamente
- [ ] CORS configurado no backend
- [ ] Teste de conexão funcionando

## 🎯 Próximos Passos

1. Deploy do frontend no Vercel
2. Configurar domínio customizado (opcional)
3. Testar integração completa
4. Compartilhar URL com usuários

---

**URL do Frontend:** `https://seu-projeto.vercel.app`
**URL do Backend:** `https://seu-backend.railway.app`

