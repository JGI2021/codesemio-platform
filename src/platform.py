"""
CodeSemio Platform - Core
Sistema principal de la plataforma multi-aplicación y multi-modelo
"""

import os
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import dspy
from dotenv import load_dotenv
import json
from datetime import datetime
import hashlib

from .models import (
    LLMModel, Application, EmbeddingType,
    MODEL_CONFIGS, APPLICATION_CONFIGS,
    ModelSelector
)
from .embeddings import EmbeddingManager, EmbeddingFusion
from .dspy_modules import CodeSemioDSPyPipeline

# Cargar configuración
load_dotenv()


class CodeSemioPlatform:
    """
    Plataforma principal de CodeSemio
    Gestiona aplicaciones, modelos, embeddings y búsqueda
    """
    
    def __init__(self, mongodb_uri: str = None):
        """
        Inicializa la plataforma
        
        Args:
            mongodb_uri: URI de MongoDB Atlas
        """
        # MongoDB
        uri = mongodb_uri or os.getenv('MONGODB_URI', 
            "mongodb+srv://JGimeno:BabTak2023@cluster1.p3da8rm.mongodb.net/")
        self.mongo_client = MongoClient(uri)
        self.db = self.mongo_client['analisis_semantico']
        
        # Managers
        self.embedding_manager = EmbeddingManager(self.mongo_client)
        self.dspy_pipeline = CodeSemioDSPyPipeline()
        self.model_selector = ModelSelector()
        
        # Estado
        self.current_app = None
        self.current_model = LLMModel.GPT4_MINI
        self.app_embeddings = {}
        self.llm_cache = {}
        self.session_id = self._generate_session_id()
        
        # Historial para optimización
        self.interaction_history = []
        
        print(f"🚀 CodeSemio Platform v1.0.0")
        print(f"📍 Session: {self.session_id}")
        
        self._initialize()
    
    def _generate_session_id(self) -> str:
        """Genera ID único de sesión"""
        timestamp = str(datetime.now())
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def _initialize(self):
        """Inicializa la plataforma"""
        # Descubrir aplicaciones
        self._discover_applications()
        
        # Configurar modelo por defecto
        self._setup_default_model()
        
        print(f"✅ Plataforma lista con {len(self.app_embeddings)} aplicaciones")
    
    def _discover_applications(self):
        """Descubre aplicaciones disponibles en MongoDB"""
        try:
            # Buscar en ontology_vectors
            apps_ontology = self.db['ontology_vectors'].distinct("application_id")
            
            # Buscar en code_vectors
            apps_code = self.db['code_vectors'].distinct("application_id")
            
            # Combinar
            all_apps = set(apps_ontology + apps_code)
            
            for app_id in all_apps:
                if app_id:
                    self.app_embeddings[app_id] = {
                        'ontology_count': self.db['ontology_vectors'].count_documents(
                            {"application_id": app_id}
                        ),
                        'code_count': self.db['code_vectors'].count_documents(
                            {"application_id": app_id}
                        ),
                        'loaded': False,
                        'embeddings': {}
                    }
            
            print(f"📱 Aplicaciones encontradas: {list(self.app_embeddings.keys())[:5]}")
            
        except Exception as e:
            print(f"⚠️ Error descubriendo aplicaciones: {e}")
    
    def _setup_default_model(self):
        """Configura modelo LLM por defecto"""
        try:
            self.select_model(LLMModel.GPT4_MINI)
        except:
            print("⚠️ No se pudo configurar modelo por defecto")
    
    def select_application(self, app_id: str) -> bool:
        """
        Selecciona la aplicación activa
        
        Args:
            app_id: ID de la aplicación
            
        Returns:
            True si se seleccionó correctamente
        """
        # Verificar si existe
        if app_id not in self.app_embeddings and app_id not in [a.value for a in Application]:
            print(f"❌ Aplicación no encontrada: {app_id}")
            return False
        
        self.current_app = app_id
        print(f"✅ Aplicación seleccionada: {app_id}")
        
        # Cargar embeddings si no están cargados
        if app_id in self.app_embeddings and not self.app_embeddings[app_id]['loaded']:
            self._load_app_embeddings(app_id)
        
        return True
    
    def _load_app_embeddings(self, app_id: str):
        """Carga embeddings de una aplicación"""
        print(f"⏳ Cargando embeddings para {app_id}...")
        
        # Determinar tipos de embeddings a cargar
        if app_id in [a.value for a in Application]:
            # Aplicación conocida
            app_config = APPLICATION_CONFIGS.get(Application(app_id))
            if app_config:
                embedding_types = [e.value for e in app_config.embedding_types]
            else:
                embedding_types = ['ontology', 'codebert', 'graphcodebert', 'hybrid']
        else:
            # Aplicación genérica - cargar todos los disponibles
            embedding_types = ['ontology', 'codebert', 'graphcodebert', 'hybrid']
        
        # Cargar con el manager
        loaded = self.embedding_manager.load_embeddings_for_app(
            app_id, 
            embedding_types,
            limit=500
        )
        
        if app_id not in self.app_embeddings:
            self.app_embeddings[app_id] = {'embeddings': {}}
            
        self.app_embeddings[app_id]['embeddings'] = loaded
        self.app_embeddings[app_id]['loaded'] = True
        
        # Mostrar estadísticas
        stats = self.embedding_manager.get_embedding_stats()
        print(f"✅ Embeddings cargados:")
        for emb_type, info in stats.items():
            if info['loaded']:
                print(f"   - {emb_type}: {info['count']} vectores")
    
    def select_model(self, model: LLMModel) -> bool:
        """
        Selecciona el modelo LLM activo
        
        Args:
            model: Modelo a seleccionar
            
        Returns:
            True si se seleccionó correctamente
        """
        try:
            lm = self._get_or_create_llm(model)
            if lm:
                dspy.configure(lm=lm)
                self.current_model = model
                print(f"✅ Modelo seleccionado: {model.value}")
                return True
        except Exception as e:
            print(f"❌ Error seleccionando modelo: {e}")
        return False
    
    def _get_or_create_llm(self, model: LLMModel):
        """Obtiene o crea instancia de LLM"""
        if model not in self.llm_cache:
            config = MODEL_CONFIGS.get(model)
            if not config:
                return None
            
            # Por ahora solo soportamos OpenAI
            if config.provider == "openai":
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    lm = dspy.LM(f'openai/{model.value}', api_key=api_key)
                    self.llm_cache[model] = lm
            else:
                # Fallback a GPT para otros providers
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    lm = dspy.LM('openai/gpt-3.5-turbo', api_key=api_key)
                    self.llm_cache[model] = lm
        
        return self.llm_cache.get(model)
    
    def search(self, 
              query: str,
              mode: str = 'smart',
              limit: int = 10,
              rerank: bool = True) -> List[Dict]:
        """
        Búsqueda principal de la plataforma
        
        Args:
            query: Consulta del usuario
            mode: Modo de búsqueda (smart, hybrid, ontology, code)
            limit: Número de resultados
            rerank: Si re-rankear con DSPy
            
        Returns:
            Lista de resultados
        """
        if not self.current_app:
            print("⚠️ No hay aplicación seleccionada")
            return []
        
        # Determinar modo si es smart
        if mode == 'smart':
            mode = self._detect_search_mode(query)
        
        # Determinar pesos según el modo
        weights = self._get_search_weights(mode)
        
        # Búsqueda híbrida con embeddings
        results = self.embedding_manager.hybrid_search(
            query_vector=None,  # TODO: generar embedding del query
            query_text=query,
            weights=weights,
            top_k=limit * 2 if rerank else limit
        )
        
        # Re-rankear con DSPy si está habilitado
        if rerank and results:
            results = self._rerank_with_dspy(query, results, limit)
        
        return results[:limit]
    
    def _detect_search_mode(self, query: str) -> str:
        """Detecta el mejor modo de búsqueda"""
        query_lower = query.lower()
        
        code_keywords = ['función', 'function', 'clase', 'class', 'código', 'code']
        ontology_keywords = ['concepto', 'qué es', 'definición', 'ontología']
        
        if any(kw in query_lower for kw in code_keywords):
            return 'code'
        elif any(kw in query_lower for kw in ontology_keywords):
            return 'ontology'
        else:
            return 'hybrid'
    
    def _get_search_weights(self, mode: str) -> Dict[str, float]:
        """Obtiene pesos para búsqueda según el modo"""
        weight_configs = {
            'hybrid': {
                'ontology': 0.25,
                'codebert': 0.25,
                'graphcodebert': 0.25,
                'hybrid': 0.25
            },
            'ontology': {
                'ontology': 0.7,
                'hybrid': 0.3,
                'codebert': 0.0,
                'graphcodebert': 0.0
            },
            'code': {
                'codebert': 0.4,
                'graphcodebert': 0.4,
                'hybrid': 0.2,
                'ontology': 0.0
            }
        }
        
        return weight_configs.get(mode, weight_configs['hybrid'])
    
    def _rerank_with_dspy(self, 
                         query: str,
                         results: List[Dict],
                         limit: int) -> List[Dict]:
        """Re-rankea resultados usando DSPy"""
        # Por ahora, retornamos tal cual
        # TODO: Implementar re-ranking con DSPy
        return results
    
    def analyze(self, query: str) -> Dict:
        """
        Análisis completo de una consulta con DSPy
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Análisis completo
        """
        # Buscar información relevante
        search_results = self.search(query, limit=10)
        
        # Preparar contexto
        context = {
            'search_results': search_results,
            'app_context': self._get_app_context(),
            'model_info': self._get_model_info(),
            'embedding_results': self._get_embedding_results()
        }
        
        # Procesar con DSPy
        analysis = self.dspy_pipeline.process_query(query, context)
        
        # Guardar en historial para optimización
        self.interaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'app': self.current_app,
            'model': self.current_model.value,
            'analysis': analysis
        })
        
        return analysis
    
    def _get_app_context(self) -> Dict:
        """Obtiene contexto de la aplicación actual"""
        if self.current_app in [a.value for a in Application]:
            app_enum = Application(self.current_app)
            config = APPLICATION_CONFIGS.get(app_enum)
            if config:
                return {
                    'name': config.name,
                    'domain': config.domain,
                    'language': config.primary_language,
                    'embedding_types': [e.value for e in config.embedding_types]
                }
        
        return {
            'name': self.current_app or 'Generic',
            'domain': 'unknown',
            'embedding_types': ['ontology', 'codebert']
        }
    
    def _get_model_info(self) -> Dict:
        """Obtiene información del modelo actual"""
        config = MODEL_CONFIGS.get(self.current_model)
        if config:
            return {
                'name': config.name,
                'capabilities': config.capabilities,
                'context_window': config.context_window,
                'speed': config.speed
            }
        return {}
    
    def _get_embedding_results(self) -> Dict:
        """Obtiene resultados de embeddings actuales"""
        if self.current_app in self.app_embeddings:
            return self.app_embeddings[self.current_app].get('embeddings', {})
        return {}
    
    def transfer_knowledge(self,
                          source_app: str,
                          target_app: str,
                          pattern: str) -> Dict:
        """
        Transfiere conocimiento entre aplicaciones
        
        Args:
            source_app: Aplicación fuente
            target_app: Aplicación destino
            pattern: Patrón a transferir
            
        Returns:
            Resultado de la transferencia
        """
        # Buscar en aplicación fuente
        self.select_application(source_app)
        source_results = self.search(pattern, limit=5)
        
        # Buscar en aplicación destino
        self.select_application(target_app)
        target_results = self.search(pattern, limit=5)
        
        # Transferir con DSPy
        result = self.dspy_pipeline.transfer_engine.transfer(
            source_app=source_app,
            target_app=target_app,
            pattern=pattern,
            source_data=source_results,
            target_data=target_results
        )
        
        return result
    
    def optimize_model_selection(self, 
                                task: str,
                                constraints: Dict = None) -> Dict:
        """
        Optimiza la selección de modelo para una tarea
        
        Args:
            task: Descripción de la tarea
            constraints: Restricciones
            
        Returns:
            Modelo recomendado y alternativas
        """
        # Preparar modelos disponibles
        available_models = []
        for model, config in MODEL_CONFIGS.items():
            available_models.append({
                'model': model.value,
                'name': config.name,
                'speed': config.speed,
                'cost_input': config.cost_per_1k_input,
                'capabilities': config.capabilities,
                'best_for': config.best_for
            })
        
        # Obtener historial de rendimiento
        performance_history = self._get_performance_history()
        
        # Optimizar con DSPy
        result = self.dspy_pipeline.model_optimizer.select_optimal_model(
            task=task,
            available_models=available_models,
            history=performance_history,
            constraints=constraints
        )
        
        return result
    
    def _get_performance_history(self) -> Dict:
        """Obtiene historial de rendimiento por modelo"""
        history = {}
        
        for interaction in self.interaction_history[-100:]:  # Últimas 100
            model = interaction.get('model')
            if model:
                if model not in history:
                    history[model] = {
                        'count': 0,
                        'avg_confidence': 0
                    }
                history[model]['count'] += 1
                
                # TODO: Calcular confianza promedio real
                
        return history
    
    def get_platform_stats(self) -> Dict:
        """Obtiene estadísticas de la plataforma"""
        stats = {
            'session_id': self.session_id,
            'current_app': self.current_app,
            'current_model': self.current_model.value,
            'applications': {
                'total': len(self.app_embeddings),
                'loaded': sum(1 for a in self.app_embeddings.values() if a['loaded'])
            },
            'embeddings': self.embedding_manager.get_embedding_stats(),
            'models_cached': len(self.llm_cache),
            'interaction_history': len(self.interaction_history)
        }
        
        return stats