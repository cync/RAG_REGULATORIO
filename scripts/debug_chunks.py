"""
Script para debugar o conteúdo dos chunks indexados
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.rag.vector_store import VectorStore
from app.config import get_settings

def debug_chunks(domain: str = "pix", limit: int = 5):
    """Mostra conteúdo dos primeiros chunks"""
    vs = VectorStore()
    
    # Buscar alguns chunks aleatórios
    try:
        collection_info = vs.client.get_collection(domain)
        print(f"\n{'='*60}")
        print(f"COLEÇÃO: {domain.upper()}")
        print(f"{'='*60}")
        print(f"Total de pontos: {collection_info.points_count}")
        
        if collection_info.points_count == 0:
            print("⚠️  Coleção vazia!")
            return
        
        # Buscar alguns pontos
        from qdrant_client.models import ScrollRequest
        scroll_result = vs.client.scroll(
            collection_name=domain,
            limit=limit
        )
        
        points = scroll_result[0] if isinstance(scroll_result, tuple) else scroll_result.points
        
        print(f"\nMostrando {len(points)} chunks:\n")
        
        for i, point in enumerate(points, 1):
            payload = point.payload
            print(f"{'='*60}")
            print(f"CHUNK {i}")
            print(f"{'='*60}")
            print(f"ID: {point.id}")
            print(f"Norma: {payload.get('norma', 'N/A')} {payload.get('numero_norma', 'N/A')}/{payload.get('ano', 'N/A')}")
            print(f"Artigo: {payload.get('artigo', 'N/A')}")
            print(f"Tema: {payload.get('tema', 'N/A')}")
            print(f"Fonte: {payload.get('fonte', 'N/A')}")
            print(f"\nConteúdo (primeiros 500 chars):")
            print("-" * 60)
            text = payload.get('text', '')
            print(text[:500] + ("..." if len(text) > 500 else ""))
            print("-" * 60)
            print()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chunks("pix", limit=5)

