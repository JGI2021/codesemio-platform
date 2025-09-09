#!/usr/bin/env python3
"""
Test completo de Rosetta con ontología y código
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/src')

from codesemio_platform import CodeSemioPlatform

def test_rosetta():
    print("="*70)
    print("🧪 TEST: Rosetta ETL con Ontología + Código")
    print("="*70)
    
    # Inicializar
    print("\n1. Inicializando plataforma...")
    platform = CodeSemioPlatform()
    
    # Seleccionar Rosetta
    print("\n2. Seleccionando Rosetta ETL...")
    platform.select_application("rosetta_etl_v4")
    
    # Verificar estadísticas
    print("\n3. Estadísticas de embeddings:")
    stats = platform.embedding_manager.get_embedding_stats()
    for emb_type, info in stats.items():
        if info['loaded']:
            print(f"   ✅ {emb_type}: {info['count']} vectores cargados")
    
    # Búsquedas de prueba
    print("\n4. Búsquedas de prueba:")
    
    # Buscar en ontología
    print("\n   📚 Búsqueda en ONTOLOGÍA (tipos de fichero):")
    results = platform.search("JSON CSV file data", mode='ontology', limit=3)
    print(f"   Encontrados: {len(results)} resultados")
    for i, r in enumerate(results[:2], 1):
        print(f"   {i}. {r.get('text', '')[:80]}...")
    
    # Buscar en código
    print("\n   💻 Búsqueda en CÓDIGO (funciones):")
    results = platform.search("function import export", mode='code', limit=3)
    print(f"   Encontrados: {len(results)} resultados")
    for i, r in enumerate(results[:2], 1):
        print(f"   {i}. {r.get('text', '')[:80]}...")
    
    # Búsqueda híbrida
    print("\n   🔄 Búsqueda HÍBRIDA:")
    results = platform.search("rosetta file types JSON CSV", mode='hybrid', limit=5)
    print(f"   Encontrados: {len(results)} resultados")
    
    print("\n✅ Test completado exitosamente")
    print(f"   - Ontología: {platform.app_embeddings['rosetta_etl_v4']['ontology_count']} docs")
    print(f"   - Código: {platform.app_embeddings['rosetta_etl_v4']['code_count']} docs")

if __name__ == "__main__":
    test_rosetta()