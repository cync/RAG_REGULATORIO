# 📥 Download Manual de Normas do Pix

Como o site do Banco Central carrega links via JavaScript, o download automático pode não funcionar. Siga este guia para download manual.

## 🎯 Passo a Passo

### 1. Acessar a Página

Acesse: **https://www.bcb.gov.br/estabilidadefinanceira/pix-normas**

### 2. Identificar Documentos

Na página, você verá uma lista de normas do Pix, como:
- Circulares
- Resoluções
- Comunicados
- Instruções Normativas

### 3. Baixar PDFs

Para cada documento:
1. Clique no link do documento
2. Se abrir em nova aba, clique com botão direito → "Salvar como"
3. Se for download direto, salve o arquivo

### 4. Organizar Arquivos

Salve os PDFs em:
```
C:\Users\Felipe\RAG_REGULATORIO\data\raw\pix\
```

**Dica:** Use nomes descritivos:
- `circular_123_2023.pdf`
- `resolucao_456_2023.pdf`
- `comunicado_789_2023.pdf`

### 5. Verificar Arquivos

Certifique-se de que os arquivos estão na pasta correta:
```bash
dir C:\Users\Felipe\RAG_REGULATORIO\data\raw\pix\
```

### 6. Executar Ingestão

Após baixar os documentos:
```bash
cd C:\Users\Felipe\RAG_REGULATORIO
python -m app.ingestion.main pix
```

## 📋 Documentos Importantes do Pix

Alguns documentos que você deve priorizar:

1. **Circular BCB nº 3.909** - Regulamenta o Pix
2. **Resoluções** sobre regras de participação
3. **Comunicados** sobre atualizações
4. **Instruções Normativas** sobre obrigações

## ⚡ Alternativa: Script com Selenium

Se você tiver Chrome instalado, pode tentar o script com Selenium:

```bash
pip install selenium webdriver-manager
python scripts/download_pix_normas_selenium.py
```

**Nota:** Requer Chrome/Chromium instalado.

## ✅ Após Download

1. Verifique se os PDFs estão em `data/raw/pix/`
2. Execute: `python -m app.ingestion.main pix`
3. Aguarde a indexação (pode demorar alguns minutos)
4. Teste: `curl https://ragregulatorio-production.up.railway.app/health`

Deve retornar:
```json
{
  "collections": {
    "pix": true  // ← Agora deve ser true!
  }
}
```

## 💡 Dica

Comece com 2-3 documentos principais para testar. Depois adicione mais conforme necessário.

