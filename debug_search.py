#!/usr/bin/env python3
"""
Script de debug para verificar búsqueda en MongoDB
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/src')

from pymongo import MongoClient
from dotenv import load_dotenv
import json

# Cargar configuración
load_dotenv()

# Conectar a MongoDB
uri = os.getenv('MONGODB_URI', "mongodb+srv://JGimeno:BabTak2023@cluster1.p3da8rm.mongodb.net/")
client = MongoClient(uri)
db = client['analisis_semantico']

print("="*70)
print("🔍 DEBUG: Verificación de datos en MongoDB")
print("="*70)

# Verificar colecciones
collections = db.list_collection_names()
print(f"\n📂 Colecciones disponibles: {collections}")

# Verificar ontology_vectors
print("\n📊 ONTOLOGY VECTORS:")
ontology_collection = db['ontology_vectors']
total_ontology = ontology_collection.count_documents({})
print(f"Total documentos: {total_ontology}")

# Buscar aplicaciones en ontology
apps_ontology = ontology_collection.distinct("application_id")
print(f"Aplicaciones: {apps_ontology[:5]}")

# Verificar rosetta_etl_v4
rosetta_docs = ontology_collection.count_documents({"application_id": "rosetta_etl_v4"})
print(f"Documentos de rosetta_etl_v4: {rosetta_docs}")

# Obtener un documento de ejemplo
sample = ontology_collection.find_one({"application_id": "rosetta_etl_v4"})
if sample:
    print("\n📄 Documento de ejemplo:")
    print(f"  - ID: {sample.get('_id')}")
    print(f"  - Tiene embedding: {'embedding' in sample}")
    print(f"  - Campos: {list(sample.keys())}")
    if 'chunk_text' in sample:
        print(f"  - Texto: {sample['chunk_text'][:200]}...")

# Verificar code_vectors
print("\n📊 CODE VECTORS:")
code_collection = db['code_vectors']
total_code = code_collection.count_documents({})
print(f"Total documentos: {total_code}")

apps_code = code_collection.distinct("application_id")
print(f"Aplicaciones: {apps_code[:5]}")

rosetta_code = code_collection.count_documents({"application_id": "rosetta_etl_v4"})
print(f"Documentos de rosetta_etl_v4: {rosetta_code}")

# Verificar embeddings en code_vectors
sample_code = code_collection.find_one({"application_id": "rosetta_etl_v4"})
if sample_code:
    print("\n📄 Documento de código de ejemplo:")
    print(f"  - ID: {sample_code.get('_id')}")
    print(f"  - Campos: {list(sample_code.keys())}")
    embeddings_fields = ['codebert_embedding', 'graphcodebert_embedding', 'hybrid_embedding']
    for field in embeddings_fields:
        if field in sample_code:
            print(f"  - Tiene {field}: Sí (dimensión: {len(sample_code[field])})")
        else:
            print(f"  - Tiene {field}: No")

# Búsqueda de texto simple
print("\n🔍 BÚSQUEDA DE TEXTO:")
query = "file"
ontology_results = list(ontology_collection.find(
    {
        "application_id": "rosetta_etl_v4",
        "$or": [
            {"chunk_text": {"$regex": query, "$options": "i"}},
            {"name": {"$regex": query, "$options": "i"}}
        ]
    }
).limit(5))

print(f"Resultados para '{query}' en ontology: {len(ontology_results)}")
if ontology_results:
    for r in ontology_results[:2]:
        text = r.get('chunk_text', r.get('name', ''))[:200]
        print(f"  - {text}...")

print("\n✅ Debug completado")