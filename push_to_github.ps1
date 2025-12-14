# Script para fazer push do repositório para o GitHub
# Execute: .\push_to_github.ps1

Write-Host "🚀 Configurando push para GitHub" -ForegroundColor Green
Write-Host ""

# Verificar se já existe remote
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "✅ Repositório remoto já configurado: $remote" -ForegroundColor Yellow
    $useExisting = Read-Host "Usar este repositório? (S/N)"
    if ($useExisting -eq "N" -or $useExisting -eq "n") {
        git remote remove origin
    } else {
        Write-Host "Fazendo push..." -ForegroundColor Green
        git push -u origin main
        exit
    }
}

# Solicitar informações
Write-Host "📝 Informe os dados do seu repositório GitHub:" -ForegroundColor Cyan
Write-Host ""

$username = Read-Host "Seu usuário do GitHub"
$repoName = Read-Host "Nome do repositório (ou pressione Enter para usar 'RAG_REGULATORIO')"

if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "RAG_REGULATORIO"
}

$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "🔗 URL do repositório: $repoUrl" -ForegroundColor Yellow
$confirm = Read-Host "Confirma? (S/N)"

if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "❌ Operação cancelada" -ForegroundColor Red
    exit
}

# Adicionar remote
Write-Host ""
Write-Host "➕ Adicionando repositório remoto..." -ForegroundColor Green
git remote add origin $repoUrl

# Verificar se o repositório existe
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Certifique-se de que o repositório '$repoName' já foi criado no GitHub!" -ForegroundColor Yellow
Write-Host "   Se ainda não criou, acesse: https://github.com/new" -ForegroundColor Yellow
Write-Host ""

$ready = Read-Host "Repositório já foi criado no GitHub? (S/N)"
if ($ready -ne "S" -and $ready -ne "s") {
    Write-Host ""
    Write-Host "📋 Passos:" -ForegroundColor Cyan
    Write-Host "   1. Acesse: https://github.com/new"
    Write-Host "   2. Nome: $repoName"
    Write-Host "   3. NÃO marque 'Initialize with README'"
    Write-Host "   4. Clique em 'Create repository'"
    Write-Host "   5. Execute este script novamente"
    Write-Host ""
    exit
}

# Fazer push
Write-Host ""
Write-Host "📤 Fazendo push para o GitHub..." -ForegroundColor Green
Write-Host ""

try {
    git push -u origin main
    
    Write-Host ""
    Write-Host "✅ Push concluído com sucesso!" -ForegroundColor Green
    Write-Host "🌐 Acesse: https://github.com/$username/$repoName" -ForegroundColor Cyan
} catch {
    Write-Host ""
    Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis causas:" -ForegroundColor Yellow
    Write-Host "  1. Repositório não existe no GitHub"
    Write-Host "  2. Problema de autenticação"
    Write-Host "  3. Repositório já tem commits"
    Write-Host ""
    Write-Host "💡 Dica: Se pedir autenticação, use um Personal Access Token:" -ForegroundColor Cyan
    Write-Host "   https://github.com/settings/tokens" -ForegroundColor Cyan
}

