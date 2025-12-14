# Frontend - Agente Regulatório

Frontend Next.js para o sistema RAG Regulatório.

## 🚀 Deploy no Vercel

### Opção 1: Deploy Automático (Recomendado)

1. **Conecte o repositório no Vercel:**
   - Acesse: https://vercel.com/new
   - Conecte seu repositório GitHub
   - Selecione a pasta `frontend`

2. **Configure variáveis de ambiente:**
   - No painel do Vercel, vá em Settings → Environment Variables
   - Adicione:
     ```
     NEXT_PUBLIC_API_URL=https://seu-backend.railway.app
     ```
   - Substitua pela URL do seu backend no Railway

3. **Deploy:**
   - O Vercel detecta automaticamente que é Next.js
   - Deploy automático a cada push na branch `main`

### Opção 2: Deploy via CLI

```bash
cd frontend
npm install
npm run build

# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Configurar variável de ambiente
vercel env add NEXT_PUBLIC_API_URL
# Digite: https://seu-backend.railway.app
```

## 🛠️ Desenvolvimento Local

```bash
cd frontend
npm install

# Criar arquivo .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Rodar em desenvolvimento
npm run dev
```

Acesse: http://localhost:3000

## 📝 Notas

- O frontend se conecta ao backend via `NEXT_PUBLIC_API_URL`
- Certifique-se de que o backend no Railway está acessível
- Configure CORS no backend para permitir requisições do Vercel

