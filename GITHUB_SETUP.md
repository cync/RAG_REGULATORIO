# 🚀 Como Subir para o GitHub

## ✅ Passo 1: Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome do repositório: `RAG_REGULATORIO` (ou outro nome de sua preferência)
3. **NÃO** marque "Initialize with README" (já temos arquivos)
4. Clique em "Create repository"

## ✅ Passo 2: Conectar e Fazer Push

Execute os comandos abaixo no terminal (substitua `SEU_USUARIO` pelo seu usuário do GitHub):

```bash
cd C:\Users\Felipe\RAG_REGULATORIO

# Adicionar repositório remoto
git remote add origin https://github.com/SEU_USUARIO/RAG_REGULATORIO.git

# Renomear branch para main (se necessário)
git branch -M main

# Fazer push
git push -u origin main
```

## 🔐 Se pedir autenticação:

### Opção 1: Personal Access Token (Recomendado)
1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Dê um nome e selecione escopo `repo`
4. Copie o token gerado
5. Use o token como senha quando pedir

### Opção 2: GitHub CLI
```bash
# Instalar GitHub CLI
winget install GitHub.cli

# Login
gh auth login

# Fazer push
git push -u origin main
```

## ✅ Passo 3: Verificar

Acesse seu repositório no GitHub e verifique se todos os arquivos foram enviados.

## 📝 Comandos Úteis

```bash
# Ver status
git status

# Ver commits
git log

# Adicionar mudanças futuras
git add .
git commit -m "Descrição das mudanças"
git push

# Ver repositório remoto
git remote -v
```

## ⚠️ Importante

- O arquivo `.env` está no `.gitignore` (não será enviado)
- Nunca commite sua `OPENAI_API_KEY` no GitHub
- Use `.env.example` como template

