# 🔧 Configuração de OCR para PDFs Escaneados

## 📋 Pré-requisitos

Para usar OCR, você precisa instalar:

1. **Tesseract OCR** (aplicativo)
2. **Bibliotecas Python** (pytesseract, pdf2image, Pillow)

## 🪟 Windows

### 1. Instalar Tesseract OCR

1. Baixe o instalador do Tesseract:
   - https://github.com/UB-Mannheim/tesseract/wiki
   - Ou: https://digi.bib.uni-mannheim.de/tesseract/

2. Execute o instalador:
   - Instale em: `C:\Program Files\Tesseract-OCR` (padrão)
   - **IMPORTANTE**: Durante a instalação, marque a opção para instalar o **pacote de idioma Português (por)**

3. Adicione Tesseract ao PATH (se não foi adicionado automaticamente):
   - Abra "Variáveis de Ambiente"
   - Adicione `C:\Program Files\Tesseract-OCR` ao PATH

### 2. Instalar Bibliotecas Python

```bash
pip install pytesseract pdf2image Pillow
```

### 3. Instalar poppler (para pdf2image)

O `pdf2image` precisa do `poppler` para converter PDFs em imagens:

1. Baixe poppler para Windows:
   - https://github.com/oschwartz10612/poppler-windows/releases/
   - Baixe a versão mais recente (ex: `Release-23.11.0-0.zip`)

2. Extraia o arquivo ZIP

3. Adicione `poppler-XX.XX.X\Library\bin` ao PATH do Windows

   **OU** configure no código (veja abaixo)

## 🐧 Linux

### 1. Instalar Tesseract e poppler

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por poppler-utils

# Fedora
sudo dnf install tesseract tesseract-langpack-por poppler-utils
```

### 2. Instalar Bibliotecas Python

```bash
pip install pytesseract pdf2image Pillow
```

## 🍎 macOS

### 1. Instalar Tesseract e poppler

```bash
brew install tesseract tesseract-lang poppler
```

### 2. Instalar Bibliotecas Python

```bash
pip install pytesseract pdf2image Pillow
```

## ⚙️ Configuração no Código (Opcional)

Se o Tesseract ou poppler não estiverem no PATH, você pode configurar manualmente:

```python
import pytesseract

# Windows - se Tesseract não estiver no PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Linux/macOS - geralmente não é necessário
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
```

E para poppler (pdf2image):

```python
from pdf2image import convert_from_path

# Windows - se poppler não estiver no PATH
images = convert_from_path(
    pdf_path,
    dpi=300,
    poppler_path=r'C:\path\to\poppler\bin'
)
```

## 🧪 Testar Instalação

Execute este script para testar:

```python
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Testar Tesseract
try:
    print("Testando Tesseract...")
    test_text = pytesseract.image_to_string(Image.new('RGB', (100, 100), color='white'))
    print("✅ Tesseract OK")
except Exception as e:
    print(f"❌ Erro no Tesseract: {e}")

# Testar pdf2image
try:
    print("Testando pdf2image...")
    # Use um PDF de teste
    # images = convert_from_path("test.pdf")
    print("✅ pdf2image OK (teste manual necessário)")
except Exception as e:
    print(f"❌ Erro no pdf2image: {e}")
```

## 📝 Como Funciona

1. **Primeiro**: Tenta extrair texto com `pypdf` (rápido, para PDFs com texto)
2. **Se falhar**: Usa OCR com Tesseract (mais lento, para PDFs escaneados)
3. **Resultado**: Texto extraído de qualquer tipo de PDF

## ⚠️ Notas Importantes

- **OCR é mais lento**: Pode demorar vários minutos para processar muitos PDFs
- **Qualidade depende**: A qualidade do OCR depende da qualidade do scan
- **Idioma**: Certifique-se de instalar o pacote de idioma Português
- **DPI**: Usamos 300 DPI para melhor qualidade (pode ser ajustado)

## 🚀 Uso

Após instalar tudo, execute a ingestão normalmente:

```bash
python scripts/ingest.py pix
```

O sistema tentará `pypdf` primeiro e, se falhar, usará OCR automaticamente.

---

**Status:** ✅ OCR implementado - instale Tesseract e poppler para usar!

