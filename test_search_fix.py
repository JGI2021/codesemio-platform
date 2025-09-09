#!/usr/bin/env python3
"""
Script de prueba para verificar que la búsqueda funciona correctamente
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/src')

from codesemio_platform import CodeSemioPlatform

def test_search():
    print("="*70)
    print("🧪 TEST: Verificación de búsqueda corregida")
    print("="*70)
    
    # Inicializar plataforma
    print("\n1. Inicializando plataforma...")
    platform = CodeSemioPlatform()
    
    # Seleccionar aplicación
    print("\n2. Seleccionando aplicación rosetta_etl_v4...")
    if platform.select_application("rosetta_etl_v4"):
        print("   ✅ Aplicación seleccionada")
    else:
        print("   ❌ Error seleccionando aplicación")
        return
    
    # Pruebas de búsqueda
    queries = [
        "file",
        "tipos fichero",
        "JSON",
        "data source",
        "rosetta"
    ]
    
    print("\n3. Ejecutando búsquedas de prueba:")
    print("-" * 50)
    
    for query in queries:
        print(f"\n📍 Query: '{query}'")
        
        # Búsqueda smart
        results = platform.search(query, mode='smart', limit=5)
        print(f"   Resultados encontrados: {len(results)}")
        
        if results:
            for i, r in enumerate(results[:2], 1):
                score = r.get('weighted_score', r.get('score', 0))
                text = r.get('text', '')[:100]
                print(f"   {i}. Score: {score:.3f}")
                print(f"      Texto: {text}...")
        else:
            print("   ⚠️ No se encontraron resultados")
    
    # Prueba de búsqueda híbrida
    print("\n4. Prueba de búsqueda híbrida:")
    results = platform.search("rosetta file JSON", mode='hybrid', limit=10)
    print(f"   Resultados encontrados: {len(results)}")
    
    # Estadísticas finales
    print("\n5. Estadísticas de embeddings:")
    stats = platform.embedding_manager.get_embedding_stats()
    for emb_type, info in stats.items():
        if info['loaded']:
            print(f"   ✅ {emb_type}: {info['count']} vectores cargados")
        else:
            print(f"   ❌ {emb_type}: no cargado")
    
    print("\n✅ Test completado")
    return True

if __name__ == "__main__":
    test_search()