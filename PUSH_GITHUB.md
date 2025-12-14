# 🚀 Push para GitHub - Comandos Rápidos

## ✅ Repositório já está pronto!

O código já foi commitado localmente. Agora siga estes passos:

## 📋 Passo 1: Criar Repositório no GitHub

1. Acesse: **https://github.com/new**
2. Nome: `RAG_REGULATORIO` (ou outro de sua preferência)
3. **NÃO** marque "Initialize with README"
4. Clique em **"Create repository"**

## 📋 Passo 2: Executar Comandos

Abra o PowerShell neste diretório e execute (substitua `SEU_USUARIO`):

```powershell
# Adicionar repositório remoto
git remote add origin https://github.com/SEU_USUARIO/RAG_REGULATORIO.git

# Fazer push
git push -u origin main
```

## 🔐 Autenticação

Quando pedir usuário/senha:
- **Usuário**: Seu usuário do GitHub
- **Senha**: Use um **Personal Access Token** (não sua senha normal)

### Como criar o token:

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Dê um nome (ex: "RAG Regulatorio")
4. Selecione escopo: **`repo`** (marca todas as opções de repo)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN** (você só verá uma vez!)
7. Use este token como senha quando o Git pedir

## ✅ Verificar

Após o push, acesse: `https://github.com/SEU_USUARIO/RAG_REGULATORIO`

---

## 🎯 Comandos Completos (Copie e Cole)

Substitua `SEU_USUARIO` pelo seu usuário do GitHub:

```powershell
cd C:\Users\Felipe\RAG_REGULATORIO
git remote add origin https://github.com/SEU_USUARIO/RAG_REGULATORIO.git
git push -u origin main
```

---

## ❓ Problemas?

### Erro: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/RAG_REGULATORIO.git
```

### Erro: "repository not found"
- Verifique se o repositório foi criado no GitHub
- Verifique se o nome do usuário está correto
- Verifique se você tem permissão no repositório

### Erro de autenticação
- Use Personal Access Token, não sua senha
- Verifique se o token tem escopo `repo`

