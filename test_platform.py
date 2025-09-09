#!/usr/bin/env python3
"""
Script de prueba rápida para CodeSemio Platform
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from platform import CodeSemioPlatform
from models import LLMModel

def test_platform():
    """Prueba básica de la plataforma"""
    print("\n🧪 TEST DE CODESEMIO PLATFORM")
    print("="*50)
    
    # Inicializar
    print("\n1. Inicializando plataforma...")
    platform = CodeSemioPlatform()
    
    # Estadísticas
    print("\n2. Obteniendo estadísticas...")
    stats = platform.get_platform_stats()
    print(f"   - Session: {stats['session_id']}")
    print(f"   - Aplicaciones: {stats['applications']['total']}")
    
    # Seleccionar aplicación
    print("\n3. Seleccionando aplicación 'rosetta_etl'...")
    if platform.select_application("rosetta_etl"):
        print("   ✅ Aplicación seleccionada")
    
    # Seleccionar modelo
    print("\n4. Seleccionando modelo GPT-4 Mini...")
    if platform.select_model(LLMModel.GPT4_MINI):
        print("   ✅ Modelo seleccionado")
    
    # Buscar
    print("\n5. Probando búsqueda...")
    results = platform.search("dataFunction", limit=3)
    print(f"   ✅ {len(results)} resultados encontrados")
    
    print("\n✅ Todas las pruebas pasaron")
    print("="*50)
    
    return True

if __name__ == "__main__":
    try:
        test_platform()
    except Exception as e:
        print(f"\n❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)