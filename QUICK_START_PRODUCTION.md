# 🚀 Quick Start - Deploy em Produção

## Opção 1: Deploy Rápido (Recomendado para começar)

### Railway (Backend) + Qdrant Cloud + Vercel (Frontend)

**Tempo estimado**: 30 minutos  
**Custo**: $0-20/mês

#### Passo a Passo:

1. **Qdrant Cloud** (5 min)
   - Acesse https://cloud.qdrant.io
   - Crie conta gratuita
   - Crie cluster (1GB free)
   - Anote URL e API key

2. **Railway - Backend** (10 min)
   - Acesse https://railway.app
   - Conecte seu repositório GitHub
   - Railway detecta Dockerfile automaticamente
   - Configure variáveis:
     ```
     OPENAI_API_KEY=sk-...
     QDRANT_HOST=<seu-cluster>.qdrant.io
     QDRANT_PORT=6333
     QDRANT_API_KEY=<sua-key>
     APP_ENV=production
     ```
   - Deploy automático!

3. **Vercel - Frontend** (10 min)
   - Acesse https://vercel.com
   - Conecte repositório (ou crie frontend simples)
   - Configure:
     ```
     NEXT_PUBLIC_API_URL=https://seu-backend.railway.app
     ```
   - Deploy!

4. **Testar** (5 min)
   ```bash
   export PRODUCTION_URL=https://seu-backend.railway.app
   python scripts/test_production.py
   ```

---

## Opção 2: Deploy Completo (AWS)

**Tempo estimado**: 2-3 horas  
**Custo**: $50-200/mês

Veja guia completo em `PRODUCTION_DEPLOY.md`

---

## Opção 3: Deploy Simples (DigitalOcean)

**Tempo estimado**: 1 hora  
**Custo**: $24-48/mês

### Passo a Passo:

1. **Criar Droplet**
   - Acesse https://digitalocean.com
   - Crie Droplet: Ubuntu 22.04, 4GB RAM
   - Adicione SSH key

2. **Configurar Servidor**
   ```bash
   ssh root@<seu-ip>
   
   # Instalar Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   apt-get install docker-compose-plugin -y
   
   # Clonar projeto
   git clone <seu-repo> /opt/rag-regulatorio
   cd /opt/rag-regulatorio
   
   # Configurar .env
   nano .env
   # Adicionar OPENAI_API_KEY
   
   # Iniciar
   docker compose up -d
   ```

3. **Configurar Nginx + SSL**
   ```bash
   apt-get install nginx certbot python3-certbot-nginx -y
   
   # Configurar Nginx (veja PRODUCTION_DEPLOY.md)
   # Configurar SSL
   certbot --nginx -d seu-dominio.com
   ```

4. **Testar**
   ```bash
   curl https://seu-dominio.com/health
   ```

---

## ✅ Checklist Rápido

- [ ] Qdrant configurado (Cloud ou próprio)
- [ ] Backend deployado e acessível
- [ ] Variáveis de ambiente configuradas
- [ ] SSL/HTTPS ativo
- [ ] Health check funcionando
- [ ] Testes de produção passando
- [ ] Frontend configurado (opcional)
- [ ] Monitoramento básico ativo

---

## 🧪 Testar em Produção

```bash
# 1. Configurar URL
export PRODUCTION_URL=https://seu-backend.com

# 2. Executar testes
python scripts/test_production.py

# 3. Teste de carga (opcional)
python scripts/test_production.py --load 20
```

---

## 📚 Documentação Completa

- **Deploy detalhado**: `PRODUCTION_DEPLOY.md`
- **Frontend**: `FRONTEND_DEPLOY.md`
- **Deploy geral**: `DEPLOY.md`

---

## 🆘 Problemas Comuns

### Backend não conecta ao Qdrant
- Verifique `QDRANT_HOST` e `QDRANT_PORT`
- Se Qdrant Cloud, verifique API key
- Verifique firewall/security groups

### Timeout nas requisições
- Aumente `API_TIMEOUT` no .env
- Verifique recursos do servidor (CPU/RAM)
- Considere aumentar instância

### Erro 429 (Rate Limit)
- Ajuste `RATE_LIMIT_PER_MINUTE` no .env
- Verifique se não há múltiplas instâncias rodando

---

## 💡 Dicas

1. **Comece simples**: Use Railway + Qdrant Cloud
2. **Monitore logs**: Acompanhe `docker compose logs -f`
3. **Backup**: Configure backup do Qdrant regularmente
4. **SSL**: Sempre use HTTPS em produção
5. **Variáveis**: Nunca commite `.env` no Git

