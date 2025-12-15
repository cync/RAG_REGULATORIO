"""Script simples para verificar coleção"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.rag.vector_store import VectorStore

vs = VectorStore()
info = vs.get_collection_info('pix')

if info:
    print(f"\n{'='*60}")
    print("STATUS DA COLECAO PIX")
    print("="*60)
    print(f"Chunks indexados: {info['points_count']}")
    print(f"Status: {'OK - Colecao populada!' if info['points_count'] > 0 else 'VAZIA'}")
    print("="*60)
else:
    print("Erro ao acessar colecao")

