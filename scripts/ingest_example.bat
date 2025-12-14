@echo off
REM Script de exemplo para ingestão de documentos (Windows)

echo Iniciando ingestão de documentos...

REM Criar diretórios se não existirem
if not exist "data\raw\pix" mkdir "data\raw\pix"
if not exist "data\raw\open_finance" mkdir "data\raw\open_finance"

echo Coloque seus PDFs/HTMLs em:
echo   - data\raw\pix\ para documentos do Pix
echo   - data\raw\open_finance\ para documentos do Open Finance
echo.
echo Depois execute:
echo   python -m app.ingestion.main pix
echo   python -m app.ingestion.main open_finance
echo.
echo Ou para reindexar completamente:
echo   python -m app.ingestion.main pix --force
echo   python -m app.ingestion.main open_finance --force

