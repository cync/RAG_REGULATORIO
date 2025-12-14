# Guia de Deploy em Produção - Agente Regulatório

## 🎯 Opções de Provedores Cloud

### 1. **AWS (Amazon Web Services)** ⭐ Recomendado
**Vantagens:**
- Serviços gerenciados completos
- Escalabilidade automática
- Alta disponibilidade
- Integração com outros serviços AWS

**Arquitetura sugerida:**
- **Backend (FastAPI)**: AWS ECS/Fargate ou EC2
- **Qdrant**: EC2 com EBS ou Qdrant Cloud
- **Frontend**: S3 + CloudFront
- **Banco de dados**: RDS (se necessário) ou manter Qdrant
- **Load Balancer**: ALB (Application Load Balancer)
- **Monitoramento**: CloudWatch

**Custo estimado**: $50-200/mês (dependendo do tráfego)

---

### 2. **Google Cloud Platform (GCP)**
**Vantagens:**
- Kubernetes nativo (GKE)
- Integração com Vertex AI
- Boa performance

**Arquitetura sugerida:**
- **Backend**: Cloud Run ou GKE
- **Qdrant**: Compute Engine
- **Frontend**: Cloud Storage + Cloud CDN
- **Load Balancer**: Cloud Load Balancing

**Custo estimado**: $40-180/mês

---

### 3. **Azure**
**Vantagens:**
- Integração com serviços Microsoft
- Boa para empresas já no ecossistema Azure

**Arquitetura sugerida:**
- **Backend**: Azure Container Instances ou AKS
- **Qdrant**: Azure VM
- **Frontend**: Azure Blob Storage + CDN
- **Load Balancer**: Azure Load Balancer

**Custo estimado**: $50-200/mês

---

### 4. **DigitalOcean** ⭐ Mais Simples
**Vantagens:**
- Simplicidade
- Preço fixo e previsível
- Boa para começar

**Arquitetura sugerida:**
- **Backend + Qdrant**: Droplet (4GB RAM mínimo)
- **Frontend**: Spaces + CDN
- **Load Balancer**: DigitalOcean Load Balancer

**Custo estimado**: $24-48/mês (droplet) + $12/mês (load balancer)

---

### 5. **Qdrant Cloud + Railway/Render** ⭐ Mais Rápido
**Vantagens:**
- Qdrant gerenciado (sem preocupação com infra)
- Deploy rápido
- Boa para MVP

**Arquitetura sugerida:**
- **Backend**: Railway ou Render
- **Qdrant**: Qdrant Cloud (gratuito até 1GB)
- **Frontend**: Vercel, Netlify ou Railway

**Custo estimado**: $0-50/mês (início)

---

## 🚀 Deploy Recomendado: AWS (Produção)

### Arquitetura Completa AWS

```
Internet
   ↓
CloudFront (CDN) → Frontend (S3)
   ↓
ALB (Application Load Balancer)
   ↓
ECS Fargate (Backend FastAPI) → Qdrant (EC2)
   ↓
CloudWatch (Logs e Métricas)
```

### Passo a Passo AWS

#### 1. Preparar Imagens Docker

```bash
# Build da imagem
docker build -f docker/Dockerfile.backend -t rag-regulatorio:latest .

# Tag para ECR
aws ecr create-repository --repository-name rag-regulatorio
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag rag-regulatorio:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-regulatorio:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-regulatorio:latest
```

#### 2. Criar ECS Task Definition

```json
{
  "family": "rag-regulatorio",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "rag-backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-regulatorio:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "QDRANT_HOST",
          "value": "<qdrant-ec2-private-ip>"
        },
        {
          "name": "QDRANT_PORT",
          "value": "6333"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:rag/openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rag-regulatorio",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Configurar Qdrant no EC2

```bash
# Launch EC2 instance (t3.medium mínimo)
# Security Group: Allow port 6333 from ECS security group

# Instalar Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Rodar Qdrant
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:v1.7.0

# Configurar persistência EBS
# Montar volume EBS em /qdrant/storage
```

#### 4. Criar Application Load Balancer

```bash
# Criar ALB via Console ou CLI
# Target Group apontando para ECS service
# Health check: /health
# SSL/TLS: Certificado ACM
```

#### 5. Configurar Secrets Manager

```bash
# Armazenar OpenAI API Key
aws secretsmanager create-secret \
  --name rag/openai-key \
  --secret-string "sk-..."
```

---

## 🚀 Deploy Alternativo: DigitalOcean (Mais Simples)

### Passo a Passo DigitalOcean

#### 1. Criar Droplet

```bash
# Droplet: 4GB RAM, 2 vCPU, Ubuntu 22.04
# Adicionar SSH key
```

#### 2. Configurar Servidor

```bash
# SSH no servidor
ssh root@<droplet-ip>

# Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install docker-compose-plugin -y

# Clonar repositório
git clone <seu-repo> /opt/rag-regulatorio
cd /opt/rag-regulatorio

# Configurar .env
nano .env
# Adicionar OPENAI_API_KEY e outras variáveis

# Iniciar serviços
docker compose up -d
```

#### 3. Configurar Nginx (Reverse Proxy)

```bash
# Instalar Nginx
apt-get install nginx -y

# Configurar
cat > /etc/nginx/sites-available/rag-regulatorio << EOF
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/rag-regulatorio /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 4. Configurar SSL (Let's Encrypt)

```bash
apt-get install certbot python3-certbot-nginx -y
certbot --nginx -d seu-dominio.com
```

#### 5. Configurar Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## 🚀 Deploy Rápido: Railway/Render + Qdrant Cloud

### Railway (Backend)

1. Conecte seu repositório GitHub ao Railway
2. Configure variáveis de ambiente:
   - `OPENAI_API_KEY`
   - `QDRANT_HOST` (do Qdrant Cloud)
   - `QDRANT_PORT=6333`
   - `QDRANT_API_KEY` (do Qdrant Cloud)
3. Railway detecta automaticamente o Dockerfile
4. Deploy automático a cada push

### Qdrant Cloud

1. Crie conta em https://cloud.qdrant.io
2. Crie cluster (free tier: 1GB)
3. Obtenha URL e API key
4. Configure no backend

### Render (Alternativa)

1. Conecte repositório
2. Selecione "Web Service"
3. Build: `docker build -f docker/Dockerfile.backend -t . .`
4. Start: `uvicorn app.api.main:app --host 0.0.0.0 --port $PORT`
5. Configure variáveis de ambiente

---

## 🧪 Como Testar em Produção

### 1. Testes de Saúde

```bash
# Health check
curl https://seu-dominio.com/health

# Esperado:
{
  "status": "healthy",
  "qdrant_connected": true,
  "collections": {
    "pix": true,
    "open_finance": true
  }
}
```

### 2. Testes de Carga

```bash
# Instalar Apache Bench
apt-get install apache2-utils -y

# Teste de carga (100 requisições, 10 concorrentes)
ab -n 100 -c 10 -p test_request.json -T application/json \
  https://seu-dominio.com/chat

# test_request.json:
{
  "question": "Quais são as obrigações de um PSP no Pix?",
  "domain": "pix"
}
```

### 3. Testes Funcionais

```bash
# Usar script de testes adaptado
python scripts/test_production.py

# Ou manualmente:
curl -X POST https://seu-dominio.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais são as obrigações de um PSP no Pix?",
    "domain": "pix"
  }'
```

### 4. Monitoramento

```bash
# Logs em tempo real (AWS)
aws logs tail /ecs/rag-regulatorio --follow

# Logs (DigitalOcean)
docker compose logs -f backend

# Métricas
# - Tempo de resposta
# - Taxa de erro
# - Uso de CPU/Memória
# - Requisições por minuto
```

---

## 📊 Checklist de Produção

### Segurança
- [ ] HTTPS configurado (SSL/TLS)
- [ ] API keys em secrets manager
- [ ] Rate limiting ativo
- [ ] Firewall configurado
- [ ] Logs sem dados sensíveis
- [ ] CORS configurado corretamente

### Performance
- [ ] Load balancer configurado
- [ ] Auto-scaling configurado (se aplicável)
- [ ] CDN para frontend
- [ ] Cache de embeddings (opcional)
- [ ] Timeout configurado

### Confiabilidade
- [ ] Health checks funcionando
- [ ] Backup do Qdrant configurado
- [ ] Logs centralizados
- [ ] Alertas configurados
- [ ] Monitoramento ativo

### Operacional
- [ ] Documentação atualizada
- [ ] Processo de deploy documentado
- [ ] Rollback plan
- [ ] Disaster recovery plan

---

## 🔧 Configurações de Produção

### .env de Produção

```env
# Ambiente
APP_ENV=production
LOG_LEVEL=INFO

# OpenAI
OPENAI_API_KEY=<seu-key>

# Qdrant (Cloud ou EC2)
QDRANT_HOST=<qdrant-host>
QDRANT_PORT=6333
QDRANT_API_KEY=<seu-key>  # Se usar Qdrant Cloud

# Performance
API_TIMEOUT=60
RATE_LIMIT_PER_MINUTE=100
TOP_K_RESULTS=5
MIN_SIMILARITY_SCORE=0.7
MAX_TOKENS_RESPONSE=1500

# Domínios
DOMAINS=pix,open_finance
```

### Docker Compose de Produção

```yaml
version: '3.8'

services:
  backend:
    image: rag-regulatorio:latest
    restart: always
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
    env_file:
      - .env.production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 📈 Monitoramento Recomendado

### Métricas Essenciais

1. **Latência**: Tempo de resposta do `/chat`
2. **Throughput**: Requisições por segundo
3. **Taxa de erro**: % de erros 5xx
4. **Uso de recursos**: CPU, memória, disco
5. **Qdrant**: Conexões, queries, storage

### Ferramentas

- **AWS**: CloudWatch
- **DigitalOcean**: Monitoring + Logs
- **Geral**: Prometheus + Grafana
- **APM**: New Relic, Datadog (opcional)

---

## 🎯 Recomendação Final

**Para começar rápido**: Railway + Qdrant Cloud
**Para produção séria**: AWS ECS + EC2 (Qdrant)
**Para simplicidade**: DigitalOcean Droplet

Escolha baseada em:
- **Orçamento**: DigitalOcean é mais barato
- **Escalabilidade**: AWS é melhor
- **Simplicidade**: Railway é mais fácil

