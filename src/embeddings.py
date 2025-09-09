"""
Gestión de embeddings multi-modelo para CodeSemio
CodeBERT, GraphCodeBERT, Ontology, Hybrid
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import json


class EmbeddingManager:
    """Gestor de embeddings multi-modelo"""
    
    def __init__(self, mongodb_client=None):
        """
        Inicializa el gestor de embeddings
        
        Args:
            mongodb_client: Cliente de MongoDB para cargar vectores
        """
        self.mongodb_client = mongodb_client
        self.embedding_caches = {
            'codebert': None,
            'graphcodebert': None,
            'ontology': None,
            'hybrid': None
        }
        self.dimension_map = {
            'codebert': 768,
            'graphcodebert': 768,
            'ontology': 768,
            'hybrid': 768,
            'openai_ada': 1536,
            'openai_3_large': 3072
        }
        
    def load_embeddings_for_app(self, 
                               application_id: str,
                               embedding_types: List[str],
                               limit: int = 1000) -> Dict:
        """
        Carga embeddings para una aplicación específica
        
        Args:
            application_id: ID de la aplicación
            embedding_types: Tipos de embeddings a cargar
            limit: Límite de vectores por tipo
            
        Returns:
            Diccionario con embeddings cargados
        """
        loaded = {}
        
        if not self.mongodb_client:
            return loaded
            
        for emb_type in embedding_types:
            if emb_type == 'ontology':
                vectors = self._load_ontology_vectors(application_id, limit)
            elif emb_type in ['codebert', 'graphcodebert', 'hybrid']:
                vectors = self._load_code_vectors(application_id, emb_type, limit)
            else:
                continue
                
            if vectors:
                loaded[emb_type] = vectors
                self.embedding_caches[emb_type] = vectors
                
        return loaded
    
    def _load_ontology_vectors(self, app_id: str, limit: int) -> Dict:
        """Carga vectores de ontología"""
        db = self.mongodb_client['analisis_semantico']
        collection = db['ontology_vectors']
        
        docs = list(collection.find(
            {"application_id": app_id, "embedding": {"$exists": True}},
            {"_id": 1, "embedding": 1, "chunk_text": 1, "metadata": 1, "name": 1}
        ).limit(limit))
        
        if not docs:
            return None
            
        return {
            'ids': [str(d['_id']) for d in docs],
            'vectors': normalize(np.array([d['embedding'] for d in docs])),
            'texts': [d.get('chunk_text', d.get('name', ''))[:500] for d in docs],
            'metadata': [d.get('metadata', {}) for d in docs],
            'count': len(docs)
        }
    
    def _load_code_vectors(self, app_id: str, emb_type: str, limit: int) -> Dict:
        """Carga vectores de código"""
        db = self.mongodb_client['analisis_semantico']
        collection = db['code_vectors']
        
        field_map = {
            'codebert': 'codebert_embedding',
            'graphcodebert': 'graphcodebert_embedding',
            'hybrid': 'hybrid_embedding'
        }
        
        field = field_map.get(emb_type)
        if not field:
            return None
        
        # Para rosetta_etl_v4, buscar por source="rosetta_etl"
        if app_id == "rosetta_etl_v4":
            query = {"source": "rosetta_etl", field: {"$exists": True}}
        else:
            query = {"application_id": app_id, field: {"$exists": True}}
            
        docs = list(collection.find(
            query,
            {"_id": 1, field: 1, "code": 1, "file_path": 1, "module": 1}
        ).limit(limit))
        
        if not docs:
            return None
            
        return {
            'ids': [str(d['_id']) for d in docs],
            'vectors': normalize(np.array([d[field] for d in docs])),
            'texts': [d.get('code', '')[:500] for d in docs],
            'metadata': {
                'file_paths': [d.get('file_path', '') for d in docs],
                'modules': [d.get('module', '') for d in docs]
            },
            'count': len(docs)
        }
    
    def search_by_similarity(self,
                            query_vector: np.ndarray,
                            embedding_type: str,
                            top_k: int = 10) -> List[Dict]:
        """
        Búsqueda por similitud coseno
        
        Args:
            query_vector: Vector de consulta
            embedding_type: Tipo de embedding
            top_k: Número de resultados
            
        Returns:
            Lista de resultados ordenados por similitud
        """
        cache = self.embedding_caches.get(embedding_type)
        if cache is None or cache.get('vectors') is None:
            return []
            
        # Normalizar query
        query_norm = normalize(query_vector.reshape(1, -1))
        
        # Calcular similitudes
        similarities = cosine_similarity(query_norm, cache['vectors'])[0]
        
        # Top-k índices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Construir resultados
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Solo resultados con similitud positiva
                result = {
                    'id': cache['ids'][idx],
                    'text': cache['texts'][idx],
                    'score': float(similarities[idx]),
                    'type': embedding_type
                }
                
                # Añadir metadata específica
                if embedding_type == 'ontology' and 'metadata' in cache:
                    result['metadata'] = cache['metadata'][idx]
                elif embedding_type in ['codebert', 'graphcodebert', 'hybrid']:
                    if 'metadata' in cache:
                        result['file_path'] = cache['metadata'].get('file_paths', [''])[idx]
                        result['module'] = cache['metadata'].get('modules', [''])[idx]
                        
                results.append(result)
                
        return results
    
    def hybrid_search(self,
                     query_vector: Optional[np.ndarray],
                     query_text: str,
                     weights: Dict[str, float] = None,
                     top_k: int = 10) -> List[Dict]:
        """
        Búsqueda híbrida combinando múltiples embeddings
        
        Args:
            query_vector: Vector de consulta (opcional)
            query_text: Texto de consulta
            weights: Pesos para cada tipo de embedding
            top_k: Número de resultados
            
        Returns:
            Resultados fusionados y rankeados
        """
        if weights is None:
            weights = {
                'ontology': 0.3,
                'codebert': 0.25,
                'graphcodebert': 0.25,
                'hybrid': 0.2
            }
            
        all_results = {}
        
        # Búsqueda por vector si está disponible
        if query_vector is not None:
            for emb_type, weight in weights.items():
                if weight > 0 and self.embedding_caches.get(emb_type):
                    results = self.search_by_similarity(query_vector, emb_type, top_k * 2)
                    
                    for r in results:
                        key = f"{r['type']}_{r['id']}"
                        if key not in all_results:
                            all_results[key] = {
                                **r,
                                'weighted_score': 0,
                                'sources': []
                            }
                        all_results[key]['weighted_score'] += r['score'] * weight
                        all_results[key]['sources'].append(emb_type)
        
        # Si no hay vector o no hay resultados, usar búsqueda por texto
        if query_text and (query_vector is None or not all_results):
            text_results = self._text_search_fallback(query_text, weights)
            # Combinar con resultados existentes
            for key, result in text_results.items():
                if key not in all_results:
                    all_results[key] = result
            
        # Ordenar por score ponderado
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x.get('weighted_score', x.get('score', 0)),
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    def _text_search_fallback(self, query: str, weights: Dict) -> Dict:
        """Búsqueda por texto cuando no hay vectores"""
        results = {}
        
        # Dividir query en palabras clave para búsqueda más flexible
        query_words = query.lower().split()
        
        for emb_type, cache in self.embedding_caches.items():
            if cache and cache.get('texts'):
                weight = weights.get(emb_type, 0.25)
                
                for i, text in enumerate(cache['texts']):
                    text_lower = text.lower()
                    
                    # Calcular score basado en coincidencias
                    score = 0
                    for word in query_words:
                        if len(word) > 2:  # Ignorar palabras muy cortas
                            if word in text_lower:
                                score += 1
                    
                    # Si hay alguna coincidencia, añadir resultado
                    if score > 0:
                        key = f"{emb_type}_{cache['ids'][i]}"
                        if key not in results:
                            results[key] = {
                                'id': cache['ids'][i],
                                'text': text,
                                'type': emb_type,
                                'weighted_score': 0,
                                'sources': [],
                                'score': score / len(query_words)  # Normalizar score
                            }
                        results[key]['weighted_score'] += (score / len(query_words)) * weight
                        if emb_type not in results[key]['sources']:
                            results[key]['sources'].append(emb_type)
                        
        return results
    
    def get_embedding_stats(self) -> Dict:
        """Obtiene estadísticas de los embeddings cargados"""
        stats = {}
        
        for emb_type, cache in self.embedding_caches.items():
            if cache:
                stats[emb_type] = {
                    'loaded': True,
                    'count': cache.get('count', 0),
                    'dimension': self.dimension_map.get(emb_type, 'unknown')
                }
            else:
                stats[emb_type] = {
                    'loaded': False,
                    'count': 0,
                    'dimension': self.dimension_map.get(emb_type, 'unknown')
                }
                
        return stats
    
    def compute_cross_embedding_similarity(self,
                                          emb_type1: str,
                                          emb_type2: str,
                                          sample_size: int = 100) -> float:
        """
        Calcula similitud promedio entre dos tipos de embeddings
        
        Args:
            emb_type1: Primer tipo de embedding
            emb_type2: Segundo tipo de embedding
            sample_size: Tamaño de muestra
            
        Returns:
            Similitud promedio
        """
        cache1 = self.embedding_caches.get(emb_type1)
        cache2 = self.embedding_caches.get(emb_type2)
        
        if not cache1 or not cache2:
            return 0.0
            
        # Tomar muestra
        n1 = min(sample_size, cache1['vectors'].shape[0])
        n2 = min(sample_size, cache2['vectors'].shape[0])
        
        sample1 = cache1['vectors'][:n1]
        sample2 = cache2['vectors'][:n2]
        
        # Calcular similitud promedio
        similarities = cosine_similarity(sample1, sample2)
        avg_similarity = np.mean(similarities)
        
        return float(avg_similarity)


class EmbeddingFusion:
    """Fusión inteligente de embeddings"""
    
    @staticmethod
    def weighted_fusion(embeddings: Dict[str, np.ndarray],
                       weights: Dict[str, float] = None) -> np.ndarray:
        """
        Fusión ponderada de múltiples embeddings
        
        Args:
            embeddings: Diccionario de embeddings por tipo
            weights: Pesos para cada tipo
            
        Returns:
            Embedding fusionado
        """
        if weights is None:
            weights = {k: 1.0 / len(embeddings) for k in embeddings}
            
        # Normalizar pesos
        total_weight = sum(weights.values())
        norm_weights = {k: v / total_weight for k, v in weights.items()}
        
        # Fusionar
        fused = None
        for emb_type, vector in embeddings.items():
            weight = norm_weights.get(emb_type, 0)
            if weight > 0:
                weighted_vec = vector * weight
                if fused is None:
                    fused = weighted_vec
                else:
                    fused += weighted_vec
                    
        # Normalizar resultado
        if fused is not None:
            fused = normalize(fused.reshape(1, -1))[0]
            
        return fused
    
    @staticmethod
    def attention_fusion(embeddings: Dict[str, np.ndarray],
                        query: np.ndarray) -> np.ndarray:
        """
        Fusión basada en atención
        
        Args:
            embeddings: Diccionario de embeddings
            query: Vector de consulta para calcular atención
            
        Returns:
            Embedding fusionado con atención
        """
        # Calcular scores de atención
        attention_scores = {}
        for emb_type, vector in embeddings.items():
            similarity = cosine_similarity(
                query.reshape(1, -1),
                vector.reshape(1, -1)
            )[0, 0]
            attention_scores[emb_type] = similarity
            
        # Softmax sobre scores
        scores = np.array(list(attention_scores.values()))
        exp_scores = np.exp(scores - np.max(scores))
        softmax_scores = exp_scores / np.sum(exp_scores)
        
        # Aplicar atención
        fused = None
        for i, (emb_type, vector) in enumerate(embeddings.items()):
            weighted_vec = vector * softmax_scores[i]
            if fused is None:
                fused = weighted_vec
            else:
                fused += weighted_vec
                
        return normalize(fused.reshape(1, -1))[0] if fused is not None else None
    
    @staticmethod
    def concatenate_fusion(embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Fusión por concatenación
        
        Args:
            embeddings: Diccionario de embeddings
            
        Returns:
            Embeddings concatenados
        """
        vectors = list(embeddings.values())
        if vectors:
            concatenated = np.concatenate(vectors)
            return normalize(concatenated.reshape(1, -1))[0]
        return None