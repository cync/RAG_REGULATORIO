# Deploy do Frontend - Agente Regulatório

## 🎨 Opções de Frontend

### 1. **Vercel** ⭐ Recomendado (React/Next.js)
**Vantagens:**
- Deploy automático do GitHub
- CDN global
- SSL automático
- Gratuito para começar

**Passo a passo:**
```bash
# 1. Criar projeto Next.js/React
npx create-next-app@latest rag-frontend
cd rag-frontend

# 2. Configurar API URL
# .env.local
NEXT_PUBLIC_API_URL=https://seu-backend.com

# 3. Conectar ao Vercel
vercel login
vercel

# 4. Deploy automático a cada push
```

**Custo**: Gratuito (até 100GB bandwidth)

---

### 2. **Netlify**
**Vantagens:**
- Similar ao Vercel
- Boa para sites estáticos
- Deploy contínuo

**Passo a passo:**
```bash
# 1. Build do projeto
npm run build

# 2. Conectar repositório no Netlify
# 3. Configurar build command: npm run build
# 4. Publish directory: out ou dist
```

**Custo**: Gratuito (até 100GB bandwidth)

---

### 3. **AWS S3 + CloudFront**
**Vantagens:**
- Integração com backend AWS
- Alta performance
- Controle total

**Passo a passo:**
```bash
# 1. Build
npm run build

# 2. Upload para S3
aws s3 sync out/ s3://seu-bucket-frontend --delete

# 3. Configurar CloudFront
# 4. Configurar SSL e domínio
```

**Custo**: ~$1-5/mês (S3) + CloudFront (pay-per-use)

---

### 4. **Railway**
**Vantagens:**
- Mesmo lugar do backend
- Simples
- Deploy automático

**Passo a passo:**
```bash
# 1. Conectar repositório
# 2. Railway detecta automaticamente
# 3. Configurar variáveis de ambiente
```

**Custo**: $5-20/mês

---

## 🚀 Exemplo: Frontend React + Vercel

### Estrutura do Projeto

```
rag-frontend/
├── src/
│   ├── components/
│   │   ├── Chat.tsx
│   │   ├── QuestionInput.tsx
│   │   └── ResponseDisplay.tsx
│   ├── services/
│   │   └── api.ts
│   └── App.tsx
├── .env.local
└── package.json
```

### Componente de Chat (Exemplo)

```typescript
// src/services/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const chatAPI = {
  async sendQuestion(question: string, domain: string) {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question, domain }),
    });
    return response.json();
  },
  
  async checkHealth() {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
  },
};
```

```typescript
// src/components/Chat.tsx
import { useState } from 'react';
import { chatAPI } from '../services/api';

export default function Chat() {
  const [question, setQuestion] = useState('');
  const [domain, setDomain] = useState('pix');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await chatAPI.sendQuestion(question, domain);
      setResponse(data);
    } catch (error) {
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <form onSubmit={handleSubmit}>
        <select value={domain} onChange={(e) => setDomain(e.target.value)}>
          <option value="pix">Pix</option>
          <option value="open_finance">Open Finance</option>
        </select>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Faça sua pergunta..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
      
      {response && (
        <div className="response">
          <h3>Resposta:</h3>
          <p>{response.answer}</p>
          {response.citations.length > 0 && (
            <div className="citations">
              <h4>Citações:</h4>
              <ul>
                {response.citations.map((citation, i) => (
                  <li key={i}>{citation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### Deploy no Vercel

```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel

# 4. Configurar variáveis de ambiente no dashboard
# NEXT_PUBLIC_API_URL=https://seu-backend.com
```

---

## 🔧 Configuração CORS no Backend

Atualizar `app/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-frontend.vercel.app",
        "http://localhost:3000",  # Desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📱 Exemplo: Frontend Simples (HTML + JS)

Se não quiser usar React, pode criar um frontend simples:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Agente Regulatório</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        input, select, button { padding: 10px; margin: 5px; }
        .response { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Agente Regulatório - Pix e Open Finance</h1>
    
    <div class="chat-container">
        <select id="domain">
            <option value="pix">Pix</option>
            <option value="open_finance">Open Finance</option>
        </select>
        <input type="text" id="question" placeholder="Faça sua pergunta..." />
        <button onclick="sendQuestion()">Enviar</button>
        
        <div id="response" class="response" style="display:none;"></div>
    </div>

    <script>
        const API_URL = 'https://seu-backend.com';
        
        async function sendQuestion() {
            const question = document.getElementById('question').value;
            const domain = document.getElementById('domain').value;
            const responseDiv = document.getElementById('response');
            
            responseDiv.style.display = 'block';
            responseDiv.innerHTML = 'Carregando...';
            
            try {
                const response = await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question, domain })
                });
                
                const data = await response.json();
                
                let html = `<h3>Resposta:</h3><p>${data.answer}</p>`;
                if (data.citations.length > 0) {
                    html += `<h4>Citações:</h4><ul>`;
                    data.citations.forEach(c => {
                        html += `<li>${c}</li>`;
                    });
                    html += `</ul>`;
                }
                
                responseDiv.innerHTML = html;
            } catch (error) {
                responseDiv.innerHTML = `Erro: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

Deploy: Coloque em S3, Netlify ou Vercel como site estático.

---

## 🎯 Recomendação

**Para começar rápido**: Vercel + React/Next.js
**Para simplicidade**: HTML estático + Netlify
**Para integração AWS**: S3 + CloudFront

