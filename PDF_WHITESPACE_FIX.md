# 🔧 Correção: PDFs Extraídos com Apenas Whitespace

## ❌ Problema Identificado

Os logs mostram que os chunks foram indexados com texto contendo **apenas quebras de linha** (`\n\n\n...`):

```
payload_preview: {'text': '\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n', ...}
text_length: 10  # Apenas 10 quebras de linha
```

Isso significa que os PDFs foram "extraídos", mas o texto extraído contém apenas whitespace (espaços, quebras de linha, tabs), sem conteúdo real.

## 🔍 Causa Raiz

O problema está na **extração de PDF**. Possíveis causas:

1. **PDFs escaneados (imagens)**: PDFs que são imagens escaneadas sem OCR
   - O `pypdf` não consegue extrair texto de imagens
   - Retorna string vazia ou apenas whitespace

2. **PDFs com estrutura complexa**: PDFs com texto em camadas ou formatos especiais
   - O `pypdf` pode não conseguir extrair corretamente
   - Retorna apenas formatação (whitespace)

3. **PDFs corrompidos ou mal formatados**: PDFs que não seguem o padrão esperado

## ✅ Correções Aplicadas

### 1. **Validação Rigorosa na Extração de PDF**
- Conta caracteres **não-whitespace** (remove `\n`, espaços, tabs)
- Se tiver menos de 50 caracteres não-whitespace, considera vazio
- Loga quantas páginas têm conteúdo vs. apenas whitespace
- Retorna string vazia se o PDF não tiver conteúdo real

### 2. **Validação no Pipeline de Ingestão**
- Valida texto extraído antes do chunking
- Ignora arquivos com texto vazio ou muito curto
- Move arquivo para `processed` mesmo assim para não reprocessar

### 3. **Logging Detalhado**
- Mostra `text_non_whitespace_length` (conteúdo real)
- Mostra `pages_with_text` vs `pages_without_text`
- Preview do texto extraído para debug

## 🧪 Diagnóstico

Após o redeploy, os logs devem mostrar:

### Se o PDF for escaneado (imagem):
```
"PDF extraído com texto vazio ou muito curto (apenas whitespace)"
pages_with_text: 0
pages_without_text: X
text_non_whitespace_length: 0
```

### Se o PDF tiver conteúdo:
```
"PDF parseado com sucesso"
pages_with_text: X
text_non_whitespace_length: > 50
```

## 🔧 Solução: Reingestão

Como os chunks já foram indexados com texto vazio, é necessário **reingestão completa**:

```bash
# 1. Resetar ingestão
python scripts/reset_ingestion.py pix

# 2. Verificar um PDF manualmente
# Abra um PDF em um leitor e tente selecionar texto
# Se não conseguir selecionar, é PDF escaneado (imagem)

# 3. Reingestão (agora com validação melhorada)
python -m app.ingestion.main pix
```

## 📋 Verificações

### 1. Verificar se PDFs são Escaneados

Teste manualmente:
```python
import pypdf

with open("data/raw/pix/arquivo.pdf", "rb") as f:
    reader = pypdf.PdfReader(f)
    page = reader.pages[0]
    text = page.extract_text()
    
    # Contar caracteres não-whitespace
    non_ws = len(text.replace('\n', '').replace(' ', '').replace('\t', ''))
    print(f"Caracteres não-whitespace: {non_ws}")
    print(f"Texto: {text[:500]}")
```

### 2. Se PDFs Forem Escaneados

**Opções:**

1. **Usar OCR** (Tesseract):
   ```bash
   pip install pytesseract pdf2image
   ```
   Mas isso adiciona complexidade e dependências.

2. **Obter PDFs com texto selecionável**:
   - Baixar novamente do site do Bacen
   - Verificar se há versão com texto

3. **Usar biblioteca alternativa**:
   - `pdfplumber` (melhor para PDFs complexos)
   - `PyMuPDF` (fitz) (mais robusto)

### 3. Testar com pdfplumber (Alternativa)

Se `pypdf` não funcionar, podemos tentar `pdfplumber`:

```python
import pdfplumber

with pdfplumber.open("arquivo.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
```

## 🎯 Próximos Passos

1. **Aguardar redeploy** - Validações melhoradas devem aparecer nos logs
2. **Reingestão** - Resetar e reingestão com validações
3. **Verificar logs** - Identificar quais PDFs têm problema
4. **Se necessário, usar biblioteca alternativa** - `pdfplumber` ou `PyMuPDF`

## 📊 Checklist

- [x] Validação rigorosa de whitespace na extração
- [x] Validação no pipeline antes do chunking
- [x] Logging detalhado de páginas com/sem conteúdo
- [ ] Reingestão após correções
- [ ] Verificar quais PDFs têm problema
- [ ] Se necessário, implementar OCR ou biblioteca alternativa

---

**Status:** ✅ Correções aplicadas - **REINGESTÃO NECESSÁRIA** para corrigir chunks já indexados com texto vazio!

