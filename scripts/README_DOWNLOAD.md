# 📥 Scripts de Download de Documentos

## Scripts Disponíveis

### 1. `download_pix_normas.py` - Download Automático

Tenta baixar automaticamente os documentos da página do Bacen.

**Uso:**
```bash
python scripts/download_pix_normas.py
```

**Funciona se:**
- A página tem links diretos de PDF
- Os links estão no HTML estático

**Pode não funcionar se:**
- A página usa JavaScript para carregar conteúdo
- Os links estão em iframes
- A estrutura HTML mudou

### 2. `download_pix_normas_manual.py` - Download Manual

Permite adicionar URLs específicas de documentos.

**Uso:**
1. Edite o arquivo e adicione URLs em `KNOWN_PIX_DOCUMENTS`
2. Execute: `python scripts/download_pix_normas_manual.py`

## 📋 Como Obter URLs dos Documentos Manualmente

### Método 1: Via Navegador

1. Acesse: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
2. Abra o DevTools (F12)
3. Vá na aba "Network"
4. Filtre por "PDF" ou "Document"
5. Clique nos links de documentos na página
6. Veja as requisições na aba Network
7. Copie as URLs dos PDFs

### Método 2: Inspecionar Elemento

1. Acesse a página
2. Clique com botão direito em um link de PDF
3. Selecione "Inspecionar elemento"
4. Veja o atributo `href` do link
5. Copie a URL completa

### Método 3: Download Manual

1. Acesse: https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
2. Baixe os PDFs manualmente
3. Coloque em `data/raw/pix/`
4. Execute a ingestão: `python -m app.ingestion.main pix`

## 🔍 Encontrar Documentos do Pix

### Documentos Principais

Procure por:
- **Circular BCB** (sobre Pix)
- **Resolução BCB** (sobre Pix)
- **Comunicado BCB** (sobre Pix)
- **Instrução Normativa** (sobre Pix)

### Onde Procurar

1. **Página principal:** https://www.bcb.gov.br/estabilidadefinanceira/pix-normas
2. **Busca no site:** https://www.bcb.gov.br (buscar "Pix normas")
3. **Seção de normas:** https://www.bcb.gov.br/normas

## 💡 Dica

Se o download automático não funcionar, a forma mais rápida é:
1. Baixar manualmente 2-3 documentos principais
2. Colocar em `data/raw/pix/`
3. Executar ingestão
4. Testar o sistema
5. Adicionar mais documentos conforme necessário

