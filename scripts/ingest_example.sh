#!/bin/bash
# Script de exemplo para ingestão de documentos

echo "Iniciando ingestão de documentos..."

# Criar diretórios se não existirem
mkdir -p data/raw/pix
mkdir -p data/raw/open_finance

echo "Coloque seus PDFs/HTMLs em:"
echo "  - data/raw/pix/ para documentos do Pix"
echo "  - data/raw/open_finance/ para documentos do Open Finance"
echo ""
echo "Depois execute:"
echo "  python -m app.ingestion.main pix"
echo "  python -m app.ingestion.main open_finance"
echo ""
echo "Ou para reindexar completamente:"
echo "  python -m app.ingestion.main pix --force"
echo "  python -m app.ingestion.main open_finance --force"

